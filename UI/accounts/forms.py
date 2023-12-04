from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import NewUser, Fhir

#Form to create a new user
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

#Form to edit user details
class UserEditForm(forms.ModelForm):
    class Meta:
        model = NewUser
        fields = ['name', 'phone', 'address', 'city', 'specialty', 'country', 'year']

#Form to upload fhir file
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

#Form to connect patient to doctor - takes in doctor eth address
class connectForm(forms.ModelForm):
    class Meta:
        model = NewUser
        fields = ('address',)
        labels = {
            'address': 'Doctor Eth Address',
        }
    
    def __init__(self, *args, **kwargs):
        super(connectForm, self).__init__(*args, **kwargs)
        self.fields['address'].required = False
        self.fields['address'].widg
