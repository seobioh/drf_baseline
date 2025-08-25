# users/rules.py
app_name = 'users'

from .models import Referral

class RefferalRule:
    def __init__(self, referrer, referree):
        self.referrer = referrer
        self.referree = referree

    def create(self):
        referral = Referral.objects.create(referrer=self.referrer, referree=self.referree)
        return referral
