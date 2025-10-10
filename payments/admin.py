# payments/admin.py
app_name = 'payments'

from django.contrib import admin

from .models import Payment, Billing

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'vender', 'status', 'type', 'order_name', 
        'total_amount', 'method', 'card_company', 'created_at'
    ]
    list_filter = [
        'status', 'type', 'vender', 'method', 'card_type', 
        'created_at', 'approved_at', 'is_partial_cancelable'
    ]
    search_fields = [
        'user__username', 'user__email', 'order_id', 'order_name', 
        'payment_key', 'card_number', 'merchant_id'
    ]
    readonly_fields = [
        'created_at', 'modified_at', 'payment_key', 'last_transaction_key'
    ]
    autocomplete_fields = ['billing']
    list_editable = ['status']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'vender', 'status', 'type', 'payment_key')
        }),
        ('Order Information', {
            'fields': ('order_id', 'order_name', 'merchant_id', 'currency')
        }),
        ('Amount Information', {
            'fields': (
                'total_amount', 'balance_amount', 'supplied_amount', 
                'vat', 'tax_exemption_amount', 'tax_free_amount'
            )
        }),
        ('Payment Method', {
            'fields': ('method', 'billing')
        }),
        ('Card Information', {
            'fields': (
                'card_issuer_code', 'card_acquirer_code', 'card_number',
                'card_installment_plan_months', 'card_is_interest_free',
                'card_interest_payer', 'card_approve_no', 'card_use_card_point',
                'card_type', 'card_owner_type', 'card_acquire_status', 'card_amount'
            ),
            'classes': ('collapse',)
        }),
        ('EasyPay Information', {
            'fields': (
                'easypay_provider', 'easypay_amount', 'easypay_discount_amount'
            ),
            'classes': ('collapse',)
        }),
        ('Other Information', {
            'fields': (
                'country', 'is_partial_cancelable', 'use_escrow', 
                'culture_expense', 'receipt_url', 'checkout_url',
                'last_transaction_key', 'secret', 'version'
            ),
            'classes': ('collapse',)
        }),
        ('Time Information', {
            'fields': ('requested_at', 'approved_at', 'cancelled_at', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'billing'
        )
    
    def card_company(self, obj):
        if obj.billing and obj.billing.card_company:
            return obj.billing.card_company
        return '-'
    card_company.short_description = 'Card Company'


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'vender', 'card_company', 'card_number', 
        'card_type', 'is_active', 'created_at'
    ]
    list_filter = [
        'vender', 'card_type', 'card_owner_type', 'is_active', 
        'created_at', 'modified_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'customer_key', 'billing_key',
        'card_company', 'card_number'
    ]
    readonly_fields = ['created_at', 'modified_at']
    list_editable = ['is_active']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'vender', 'customer_key', 'billing_key', 'is_active')
        }),
        ('Card Information', {
            'fields': (
                'card_company', 'card_number', 'card_type', 'card_owner_type',
                'card_issuer_code', 'card_acquirer_code'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['activate_billings', 'deactivate_billings']
    
    def activate_billings(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} billings have been activated.')
    activate_billings.short_description = 'Activate selected billings'
    
    def deactivate_billings(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} billings have been deactivated.')
    deactivate_billings.short_description = 'Deactivate selected billings'
