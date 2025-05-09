# accounts/admin.py
app_name = 'accounts'

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'user_name', 'birthday', 'gender', 'profile_img_url', 'last_login', 'created_at', 'is_active', 'is_business', 'is_staff', 'is_admin')

admin.site.register(User, UserAdmin)