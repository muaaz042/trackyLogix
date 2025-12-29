from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, ClientProfile, Subscription


@receiver(post_save, sender=User)
def create_related_entities(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == "client":
        ClientProfile.objects.create(user=instance)

    if instance.role == "admin":
        Subscription.objects.create(user=instance)
