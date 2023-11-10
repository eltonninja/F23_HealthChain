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
        fields = UserCreationForm.Meta.fields + ('phone', 'specialty', 'address', 'city', 'country',)

class PatientCreationForm(CustomUserCreationForm):

    class Meta(CustomUserCreationForm.Meta):
        model = Patient
        fields = UserCreationForm.Meta.fields + ('phone', 'address', 'city' , 'country',)

class DoctorChangeForm(CustomUserChangeForm):

    class Meta:
        model = Doctor
        fields = UserChangeForm.Meta.fields

class PatientChangeForm(CustomUserChangeForm):

    class Meta:
        model = Patient
        fields = UserChangeForm.Meta.fields