from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# 🔹 PROFILE MODEL
class Profile(models.Model):
    ROLE = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE, default='PATIENT')
    status = models.CharField(max_length=20, default="INACTIVE")

    def __str__(self):
        return self.user.username


# 🔹 DOCTOR MODEL
class Doctor(models.Model):
    # optional doctor login
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # ✅ who added doctor
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctors', null=True, blank=True)
    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100,null=True,blank=True)
    specialization = models.CharField(max_length=100)
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Staff(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
# 🔹 APPOINTMENT MODEL
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()

    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    )

    status = models.CharField(max_length=20, choices=STATUS, default='Pending')

    class Meta:
        unique_together = ('doctor', 'date', 'time')  # ✅ prevents double booking

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.date}"


# 🔹 PRESCRIPTION MODEL
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicines = models.TextField()
    notes = models.TextField(blank=True)
    file = models.FileField(upload_to='prescriptions/', null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.patient.name}-{self.doctor}"


# 🔹 AUTO CREATE PROFILE
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# 🔹 SAVE PROFILE AUTOMATICALLY
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()