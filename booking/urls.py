from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.logo),
    path('welcome/',views.welcome,name='welcome'),
    path('home/',views.home,name='home'),
    path('about/',views.about,name='about'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/',views.register_view,name='register'),

    path('search/',views.search,name='search_doctor'),
    path('book/<int:id>/',views.book,name='book'),
    path('success/',views.success_view,name='success'),
    path('history/',views.history,name='my_appointments'),

    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('doctor_dashboard/',views.doctor_dashboard,name='doctor_dashboard'),

    path('add_prescription/<int:id>/', views.add_prescription, name='add_prescription'),
    path('view_prescription/<int:id>/',views.view_prescription,name='view_prescription'),

    path('logout/',views.logout_view,name='logout'),

    path('manage_doctor/', views.manage_doctor, name='manage_doctor'),
    path('delete_doctor/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),   
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)