from django.contrib import admin
from .models import Profile, Doctor, Appointment, Prescription


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'added_by')
    exclude = ('added_by',)   # hide field

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user 
        super().save_model(request, obj, form, change)
admin.site.register(Doctor, DoctorAdmin)

# ✅ Register models
admin.site.register(Profile)
admin.site.register(Appointment)
admin.site.register(Prescription)