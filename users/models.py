# users/models.py
app_name = 'users'

from django.db import models

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