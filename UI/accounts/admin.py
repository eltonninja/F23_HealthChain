from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NewUser

class CustomUserAdmin(UserAdmin):
    model = NewUser
    # Remove 'ethereum_account' from list_display
    list_display = ['username', 'email', 'name', 'phone', 'address', 'city', 'country', 'specialty']
    # Update fieldsets by removing 'ethereum_account'
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('name', 'phone', 'address', 'city', 'country', 'specialty')}),
    )
    # Update add_fieldsets by removing 'ethereum_account'
    add_fieldsets = UserAdmin.add_fieldsets + (
            (None, {'fields': ('name', 'phone', 'address', 'city', 'country', 'specialty')}),
    )

admin.site.register(NewUser, CustomUserAdmin)
