from django.contrib.auth.models import AbstractUser
from django.db import models

# class CustomUser(AbstractUser):
#     pass

class CustomUser(AbstractUser):
    ethereum_account = models.CharField(max_length=42, blank=True, null=True)

class Doctor(CustomUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Patient(CustomUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def has_filled_details(self):
        # Check if required fields are filled. Adjust the fields as necessary.
        required_fields = ['name', 'phone', 'address', 'city', 'country']
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True