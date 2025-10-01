# users/admin.py
app_name = 'users'

from django.contrib import admin

from .models import Referral, ReferralRule, PointCoupon, PointTransaction

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referree', 'created_at', 'modified_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'modified_at']
    search_fields = ['referrer__username', 'referree__username']
    readonly_fields = ['created_at', 'modified_at']


@admin.register(ReferralRule)
class ReferralRuleAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'description', 'created_at', 'modified_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'modified_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'modified_at']


@admin.register(PointCoupon)
class PointCouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'amount', 'usage_limit', 'usage_limit_per_user',
        'valid_from', 'valid_to', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'valid_from', 'valid_to', 'created_at', 'modified_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['code', 'created_at', 'modified_at']
    list_editable = ['is_active', 'amount']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'amount')
        }),
        ('Usage Limit', {
            'fields': ('usage_limit', 'usage_limit_per_user')
        }),
        ('Valid Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'amount', 'description', 'transaction_type', 'transaction_id',
        'is_active', 'created_at'
    ]
    list_filter = ['transaction_type', 'is_active', 'created_at', 'modified_at']
    search_fields = ['user__username', 'user__email', 'transaction_id']
    readonly_fields = ['created_at', 'modified_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'amount', 'description', 'transaction_type', 'transaction_id')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')