# payments/models.py
app_name = 'payments'

from django.db import models

from accounts.models import User

VENDER_CHOICES = [
    ('TOSS', 'Toss'),
    ('PORTONE', 'PortOne'),
]


class Billing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billings')
    vender = models.CharField(max_length=20, choices=VENDER_CHOICES)
    customer_key = models.CharField(max_length=255, null=True, blank=True)
    billing_key = models.CharField(max_length=255)

    card_company = models.CharField(max_length=50, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    card_type = models.CharField(max_length=10, null=True, blank=True)
    card_owner_type = models.CharField(max_length=10, null=True, blank=True)
    card_issuer_code = models.CharField(max_length=2, null=True, blank=True)
    card_acquirer_code = models.CharField(max_length=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Billing'
        verbose_name_plural = 'Billings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} {self.card_company} - {self.card_number}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('READY', 'Ready'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING_FOR_DEPOSIT', 'Waiting For Deposit'),
        ('DONE', 'Done'),
        ('CANCELED', 'Canceled'),
        ('PARTIAL_CANCELED', 'Partial Canceled'),
        ('ABORTED', 'Aborted'),
        ('EXPIRED', 'Expired'),
    ]

    TYPE_CHOICES = [
        ('NORMAL', 'Normal'),
        ('BILLING', 'Billing'),
        ('BRANDPAY', 'BrandPay'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    billing = models.ForeignKey(Billing, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    vender = models.CharField(max_length=20, choices=VENDER_CHOICES)
    payment_key = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order_id = models.CharField(max_length=64)
    order_name = models.CharField(max_length=100)
    merchant_id = models.CharField(max_length=64)
    
    currency = models.CharField(max_length=20)
    method = models.CharField(max_length=20, null=True, blank=True)
    total_amount = models.IntegerField()
    balance_amount = models.IntegerField()
    supplied_amount = models.IntegerField()
    vat = models.IntegerField()
    tax_exemption_amount = models.IntegerField(default=0)
    tax_free_amount = models.IntegerField(default=0)

    # 카드 정보 (flat하게)
    card_issuer_code = models.CharField(max_length=2, null=True, blank=True)
    card_acquirer_code = models.CharField(max_length=2, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    card_installment_plan_months = models.IntegerField(null=True, blank=True)
    card_is_interest_free = models.BooleanField(null=True, blank=True)
    card_interest_payer = models.CharField(max_length=20, null=True, blank=True)
    card_approve_no = models.CharField(max_length=8, null=True, blank=True)
    card_use_card_point = models.BooleanField(null=True, blank=True)
    card_type = models.CharField(max_length=10, null=True, blank=True)
    card_owner_type = models.CharField(max_length=10, null=True, blank=True)
    card_acquire_status = models.CharField(max_length=20, null=True, blank=True)
    card_amount = models.IntegerField(null=True, blank=True)

    # EasyPay 정보 (flat하게)
    easypay_provider = models.CharField(max_length=50, null=True, blank=True)
    easypay_amount = models.IntegerField(null=True, blank=True)
    easypay_discount_amount = models.IntegerField(null=True, blank=True)

    # 기타 정보
    country = models.CharField(max_length=2, default='KR')
    is_partial_cancelable = models.BooleanField(default=True)
    use_escrow = models.BooleanField(default=False)
    culture_expense = models.BooleanField(default=False)
    receipt_url = models.URLField(null=True, blank=True)
    checkout_url = models.URLField(null=True, blank=True)
    last_transaction_key = models.CharField(max_length=64, null=True, blank=True)

    # 추가 필드들 (API 문서에서 누락된 것들)
    secret = models.CharField(max_length=50, null=True, blank=True)
    version = models.CharField(max_length=20, default='2022-11-16')

    requested_at = models.DateTimeField()
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_name} - {self.status} ({self.total_amount:,}원)"