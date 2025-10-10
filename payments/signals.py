# payments/signals.py
app_name = "payments"

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Billing
from .utils import inactivate_billing

# Billing
# <-------------------------------------------------------------------------------------------------------------------------------->
@receiver(post_save, sender=Billing)
def inactivate_billing_key(sender, instance, **kwargs):
    if instance.is_active == False:
        inactivate_billing(instance)