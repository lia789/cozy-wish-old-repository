from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import VenueDiscount, ServiceDiscount, PlatformDiscount


@receiver(post_save, sender=VenueDiscount)
def handle_venue_discount_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a venue discount is saved
    """
    # If this is a new discount and it's already active, we might want to notify customers
    if created and instance.is_approved and instance.start_date <= timezone.now() <= instance.end_date:
        # This would be a good place to trigger notifications
        pass


@receiver(post_save, sender=ServiceDiscount)
def handle_service_discount_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a service discount is saved
    """
    # If this is a new discount and it's already active, we might want to notify customers
    if created and instance.is_approved and instance.start_date <= timezone.now() <= instance.end_date:
        # This would be a good place to trigger notifications
        pass


@receiver(post_save, sender=PlatformDiscount)
def handle_platform_discount_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a platform discount is saved
    """
    # If this is a new discount and it's already active, we might want to notify customers
    if created and instance.start_date <= timezone.now() <= instance.end_date:
        # This would be a good place to trigger notifications
        pass
