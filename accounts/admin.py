# accounts/admin.py
app_name = 'accounts'

from django.contrib import admin
from .models import User, UserSocialAccount, Verification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'mobile', 'name', 'username',
        'ci_hash', 'birthday', 'gender', 'profile_image',
        'created_at', 'modified_at', 'last_access', 
        'is_active', 'is_business', 'is_staff', 'is_admin'
    )

@admin.register(UserSocialAccount)
class UserSocialAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'provider', 'provider_user_id',
        'connected_at'
    )

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'target', 'verification_code',
        'created_at'
    )