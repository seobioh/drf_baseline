# users/admin.py
app_name = 'users'

from django.contrib import admin
from .models import Referral

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referree', 'created_at', 'modified_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'modified_at']
    search_fields = ['referrer__username', 'referree__username']
    readonly_fields = ['created_at', 'modified_at']
