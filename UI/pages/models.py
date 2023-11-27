from django.db import models

# Create your models here.
#doctor and patient user types

from django.contrib.auth.models import Group, Permission

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class DoctorManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Doctor(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)

    objects = DoctorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(Group, related_name='doctor_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='doctor_permissions')

class Patient(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)




