from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import NewUser, Fhir

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = NewUser
        fields = ('name', 'phone', 'address', 'city', 'country', 'specialty', 'year')
        labels = {
            'name': 'Name',
            'year': 'Year',
            'phone': 'Phone',
            'address': 'Address',
            'city': 'City',
            'country': 'Country',
            'specialty': 'Specialty (leave blank if patient)',
        }
    
    def __init__(self, *args, **kwargs):
        super(UserDetailsForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].required = False

class fhirForm(forms.ModelForm):
    class Meta:
        model = Fhir
        fields = ('file', 'Eth_address')
        labels = {
            'file': 'Fhir File',
            'Eth_address': 'Eth_address',
        }
    
    def __init__(self, *args, **kwargs):
        super(fhirForm, self).__init__(*args, **kwargs)
        self.fields['Eth_address'].required = False
        self.fields['file'].required = False

