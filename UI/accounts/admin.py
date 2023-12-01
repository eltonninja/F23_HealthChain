from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import NewUser

class CustomUserAdmin(UserAdmin):
    model = NewUser
    list_display = ['username', 'email', 'name', 'phone', 'address', 'city', 'country', 'specialty', 'ethereum_account']
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('name', 'phone', 'address', 'city', 'country', 'specialty', 'ethereum_account')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
            (None, {'fields': ('name', 'phone', 'address', 'city', 'country', 'specialty', 'ethereum_account')}),
    )


admin.site.register(NewUser, CustomUserAdmin)
