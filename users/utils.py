# users/rules.py
app_name = 'users'

from django.db import transaction

from .models import Referral, ReferralRule

class ReferralHandler:
    def __init__(self, referrer, referree):
        self.referrer = referrer
        self.referree = referree

    def create(self):
        with transaction.atomic():
            referral_rule = ReferralRule.objects.filter(user=self.referrer).first()
            if referral_rule:
                referral = Referral.objects.create(referrer=self.referrer, referree=self.referree)
                return referral
            else:
                referral = Referral.objects.create(referrer=self.referrer, referree=self.referree)
                return referral
