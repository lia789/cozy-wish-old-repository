from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, ServiceProviderProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for a user when they are created"""
    if created:
        if instance.is_customer:
            CustomerProfile.objects.create(user=instance)
        elif instance.is_service_provider:
            ServiceProviderProfile.objects.create(
                user=instance,
                business_name=f"{instance.email}'s Business"  # Default business name
            )
