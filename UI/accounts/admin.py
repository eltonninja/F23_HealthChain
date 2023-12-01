from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Doctor, Patient

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

admin.site.register(CustomUser, CustomUserAdmin)

class DoctorAdmin(admin.ModelAdmin):
    model = Doctor
    list_display = ['name', 'phone', 'specialty', 'address', 'city', 'country']

    #change verbose name
    verbose_name_plural = "doctors"

admin.site.register(Doctor, DoctorAdmin)

class PatientAdmin(admin.ModelAdmin):
    model = Patient
    list_display = ['name', 'phone', 'address', 'city', 'country']

    #change verbose name
    verbose_name_plural = "patients"

admin.site.register(Patient, PatientAdmin)
