from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .decorators import role_required
from .models import Appointment
from booking.models import Doctor,Staff
from .models import Patient,Prescription 
from django.http import HttpResponse
from django.db import IntegrityError

def logo(request):
    return render(request, 'logo.html')

def welcome(request):  
    return render(request, 'welcome.html')
    
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')
    
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ Admin
            if user.is_superuser:
                return redirect('admin_dashboard')

            # ✅ Staff → Doctor Dashboard
            elif user.is_staff: 
                return redirect('doctor_dashboard')

            else:
                return redirect('home')

    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        name = request.POST.get('name')

        # Password match
        if password != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        #  Username check
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        # Email check
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered'})
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
  
        Patient.objects.create(
           user=user,
           name=name,
           email=email,
           age=age,
           gender=gender,
           address=address,
           phone=phone
        )
        return redirect('success') 
    return render(request, 'register.html')
       
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@role_required("PATIENT")
def search(request):
    doctors = Doctor.objects.all()
    return render(request,'search.html',{'doctors':doctors})

@login_required(login_url='login')
@role_required("PATIENT")
def book(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    patient = Patient.objects.get(user=request.user) 
    
    if request.method == "POST":
        date = request.POST.get('date')
        time = request.POST.get('time')

        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            messages.error(request, "❌ Time slot already booked")
            return redirect(request.path)

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=date,
            time=time
        )

        messages.success(request, "✅ Booking Confirmed!")
        return redirect('home')

    return render(request, 'book.html', {'doctor': doctor})

def success_view(request):
    return render(request, 'success.html')

@login_required(login_url='login')
@role_required("PATIENT")
def history(request):
    patient = get_object_or_404(Patient, user=request.user)
    data = Appointment.objects.filter(patient=patient)
    return render(request, 'history.html', {'data': data})
  

@login_required(login_url='login')
@role_required("ADMIN")
def admin_dashboard(request):
    doctors = Profile.objects.filter(role="DOCTOR")
    patients = User.objects.filter(profile__role="PATIENT")
    appointments = Appointment.objects.all()

    context = {
        'doctors': doctors,
        'patients': patients,
        'appointments': appointments,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='login')
def doctor_dashboard(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        appt_id = request.POST.get("id")
        status = request.POST.get("status")

        try:
            appointment = Appointment.objects.get(id=appt_id)
            appointment.status = status
            appointment.save()
        except Appointment.DoesNotExist:
            pass

        return redirect("doctor_dashboard")

    if hasattr(user, 'doctor'):
        appointments = Appointment.objects.filter(doctor=user.doctor)

    elif user.is_staff:
        appointments = Appointment.objects.all()

    else:
        return redirect('home')

    return render(request, 'doctor_dashboard.html', {
        'appointments': appointments,
        'role': 'doctor' if hasattr(user, 'is_doctor') and user.is_doctor else 'staff',
        'doctor': user
    })

def add_prescription(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    # ✅ Restrict: Only doctors allowed
    if not hasattr(request.user, 'doctor'):
        messages.error(request, "Only doctors can add prescriptions.")
        return redirect('doctor_dashboard')  # or staff dashboard

    # ✅ Get objects
    appointment = get_object_or_404(Appointment, id=id)
    doctor = request.user.doctor
    patient = appointment.patient

    # ✅ POST logic
    if request.method == "POST":
        medicines = request.POST.get('medicines')
        notes = request.POST.get('notes')

        # Prevent duplicate prescription
        if Prescription.objects.filter(appointment=appointment).exists():
            messages.error(request, "Prescription already exists")
            return redirect('doctor_dashboard')

        Prescription.objects.create(
            appointment=appointment,
            doctor=doctor,
            patient=patient,
            medicines=medicines,
            notes=notes
        )

        messages.success(request, "Prescription added successfully")
        return redirect('doctor_dashboard')

    # ✅ GET request
    return render(request, 'add_prescription.html', {'appointment': appointment})


@login_required(login_url='login')
def view_prescription(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    p = get_object_or_404(Prescription, appointment=appointment)

    return render(request, 'view_prescription.html', {'p': p})
   

def manage_doctor(request):
    doctors = Doctor.objects.all()
    return render(request, 'manage_doctor.html', {
        'doctors': doctors
    })

def delete_doctor(request, id):
    doctor= Doctor.objects.get(id=id)
    user=doctor.user
    user.delete()
    return redirect('manage_doctor')

def add_doctor(request):
    if request.method == "POST":

        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        image = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('add_doctor')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password   
            )

            user.first_name = name
            user.save()

            Doctor.objects.create(
                user=user,
                name=name,
                username=username,
                added_by=request.user,
                specialization=specialization,
                image=image
            )

            messages.success(request, "Doctor added successfully!")
            return redirect('manage_doctor')

        except IntegrityError:
            messages.error(request, "Something went wrong (duplicate entry).")
            return redirect('add_doctor')

    return render(request, 'add_doctor.html')


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # check if user has profile and is admin
            if hasattr(user, 'profile') and user.profile.role == "ADMIN":
                return redirect('admin_dashboard')
            else:
                return render(request, 'admin_login.html', {
                    'error': 'You are not authorized as admin'
                })

        else:
            return render(request, 'admin_login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'admin_login.html')

