# users/signals.py
app_name = "users"

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import PointTransaction

@receiver(pre_delete, sender=PointTransaction)
def return_point_on_delete(sender, instance, **kwargs):
    instance.user.point = instance.user.point - instance.amount
    instance.user.save()