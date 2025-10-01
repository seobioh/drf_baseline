# users/models.py
app_name = 'users'

import random, string

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from accounts.models import User

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    referree = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrees')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = ('referrer', 'referree')

    def __str__(self):
        return f"{self.referrer.username} -> {self.referree.username}"


class ReferralRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rules')
    name = models.CharField(max_length=20, verbose_name="Name")
    description = models.TextField(verbose_name="Description")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Referral Rule'
        verbose_name_plural = 'Referral Rules'

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PointCoupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code", editable=False)
    name = models.CharField(max_length=20, verbose_name="Name")
    description = models.TextField(verbose_name="Description")

    amount = models.IntegerField(verbose_name="Amount", default=0)

    usage_limit = models.IntegerField(verbose_name="Usage Limit", default=1)                            # Usage Limit
    usage_limit_per_user = models.IntegerField(verbose_name="Usage Limit Per User", default=1)          # Usage Limit Per User

    valid_from = models.DateTimeField(verbose_name="Valid From", default=timezone.now)                  # Valid From
    valid_to = models.DateTimeField(verbose_name="Valid To")                                            # Valid To

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Point Coupon'
        verbose_name_plural = 'Point Coupons'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def generate_code(self):
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(8))
            if not PointCoupon.objects.filter(code=code).exists():
                return code

    def clean(self):
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError("유효 시작일은 유효 종료일보다 이전이어야 합니다.")

        # 사용 제한 검사
        if self.usage_limit <= 0:
            raise ValidationError("사용 제한은 1 이상이어야 합니다.")
        if self.usage_limit_per_user <= 0:
            raise ValidationError("사용자당 사용 제한은 1 이상이어야 합니다.")
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.code:
                self.code = self.generate_code()
        
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_valid_now(self):
        now = timezone.now()
        
        # valid_from이 None이거나 valid_to가 None이면 유효하지 않음
        if self.valid_from is None or self.valid_to is None:
            return False
            
        return self.is_active and self.valid_from <= now <= self.valid_to


class PointTransaction(models.Model):
    TYPE_CHOICES = [
        ('COUPON', 'Coupon'),
        ('REFERRAL', 'Referral'),

        ('WITHDRAW', 'Withdraw'),
        ('DEPOSIT', 'Deposit'),

        ('REVIEW', 'Review'),
        ('COMMENT', 'Comment'),
        ('ACTIVITY', 'Activity'),

        ('CANCEL', 'Cancel'),
        ('SERVICE', 'Service'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    transaction_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'

    def save(self, *args, **kwargs):
        if not self.pk:
            points = self.user.point_transactions.filter(is_active=True).aggregate(total=models.Sum('amount'))['total'] or 0
        else:
            points = self.user.point_transactions.filter(is_active=True).exclude(pk=self.pk).aggregate(total=models.Sum('amount'))['total'] or 0

        total_points = points + self.amount
        if total_points < 0:
            raise ValidationError("포인트 잔액이 부족합니다.")

        self.user.point = total_points
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type} - {self.transaction_id if self.transaction_id else 'None'}"