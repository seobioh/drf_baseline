# accounts/admin.py
app_name = 'accounts'

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'mobile', 'name', 'username',
        'birthday', 'gender', 'profile_image',
        'created_at', 'modified_at', 'last_access', 
        'is_active', 'is_business', 'is_staff', 'is_admin'
    )

admin.site.register(User, UserAdmin)