# accounts/admin.py
app_name = 'accounts'

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'nickname', 'birthday', 'gender', 'profile_img', 'is_active', 'is_business', 'is_staff', 'is_admin')

admin.site.register(User, UserAdmin)