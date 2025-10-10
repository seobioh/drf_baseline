# payments/serializers.py

from rest_framework import serializers

from .models import Payment, Billing

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = [
            'id', 'user', 'vender',
            'card_company', 'card_number', 'card_type', 'card_owner_type', 'card_issuer_code', 'card_acquirer_code',
            'is_active', 'created_at', 'modified_at',
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'billing', 'butler', 'subscription', 'vender', 'payment_key',
            'status', 'type', 'order_id', 'order_name', 'merchant_id', 'method', 'country',
            'currency','total_amount', 'balance_amount', 'supplied_amount', 'vat', 'tax_exemption_amount', 'tax_free_amount', 
            'card_issuer_code', 'card_acquirer_code', 'card_number', 'card_installment_plan_months', 'card_is_interest_free', 'card_interest_payer', 
            'card_approve_no', 'card_use_card_point', 'card_type', 'card_owner_type', 'card_acquire_status', 'card_amount', 
            'easypay_provider', 'easypay_amount', 'easypay_discount_amount',
            'is_partial_cancelable', 'use_escrow', 'culture_expense', 'receipt_url', 'checkout_url', 'last_transaction_key',
            'secret', 'version', 'requested_at', 'approved_at', 'cancelled_at', 'created_at',
            'modified_at',
        ]
        read_only_fields = ['id', 'payment_key', 'last_transaction_key', 'created_at', 'modified_at']
    