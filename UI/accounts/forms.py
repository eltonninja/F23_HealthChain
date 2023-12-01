from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import NewUser


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = NewUser
        fields = ('name', 'phone', 'address', 'city', 'country', 'specialty')
        labels = {
            'name': 'Name',
            'phone': 'Phone',
            'address': 'Address',
            'city': 'City',
            'country': 'Country',
            'specialty': 'Specialty (leave blank if patient)',
        }
    
    def __init__(self, *args, **kwargs):
        super(UserDetailsForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].required = False