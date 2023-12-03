from django.contrib.auth.models import AbstractUser
from django.db import models

class NewUser(AbstractUser):
    #inherits username from AbstractUser and sets username=ethereum_account
    # Other fields
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    #if specialty is blank, then it is a patient
    def is_patient(self):
        return not self.specialty
    
    #if specialty is not blank, then it is a doctor
    def is_doctor(self):
        return self.specialty

    def __str__(self):
        return self.name
    
    def has_filled_details(self):
        # Check if required fields are filled. Adjust the fields as necessary.
        required_fields = ['name', 'phone', 'address', 'city', 'country']
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True
    
class Fhir(models.Model):
    file = models.FileField(upload_to='files/')
    Eth_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    