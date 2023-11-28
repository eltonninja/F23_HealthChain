from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Doctor, Patient

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username',)

class DoctorCreationForm(CustomUserCreationForm):

    class Meta(CustomUserCreationForm.Meta):
        model = Doctor
        fields = UserCreationForm.Meta.fields + ('name', 'phone', 'address', 'city' , 'country', 'specialty',)

class PatientCreationForm(CustomUserCreationForm):

    class Meta(CustomUserCreationForm.Meta):
        model = Patient
        fields = UserCreationForm.Meta.fields + ('name', 'phone', 'address', 'city' , 'country',)

class DoctorChangeForm(CustomUserChangeForm):

    class Meta:
        model = Doctor
        fields = UserChangeForm.Meta.fields

class PatientChangeForm(CustomUserChangeForm):

    class Meta:
        model = Patient
        fields = UserChangeForm.Meta.fields


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = Patient  # or CustomUser/Doctor/Patient, depending on your requirements
        fields = ['name', 'phone', 'address', 'city', 'country']  # Add any other fields you need

    def __init__(self, *args, **kwargs):
        super(UserDetailsForm, self).__init__(*args, **kwargs)
        # Here you can add any custom initialization or modifications to the form fields