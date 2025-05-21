from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts_app.models import ServiceProviderProfile
from booking_cart_app.models import Booking
from review_app.models import Review, ReviewResponse

from .utils import (
    notify_new_booking, notify_booking_cancellation, notify_new_review,
    notify_review_response, notify_service_provider_approval,
    notify_service_provider_rejection, notify_booking_status_changed
)

User = get_user_model()


@receiver(post_save, sender=Booking)
def booking_notification(sender, instance, created, **kwargs):
    """Create notifications when a booking is created or updated"""
    # Get the old status from the instance's __dict__ if it exists
    old_status = instance._old_status if hasattr(instance, '_old_status') else None

    if created:
        # New booking
        notify_new_booking(instance)
    elif instance.status == 'cancelled' and old_status != 'cancelled':
        # Booking cancelled
        notify_booking_cancellation(instance)
    elif old_status and instance.status != old_status:
        # Status changed
        notify_booking_status_changed(instance, old_status)


@receiver(post_save, sender=Review)
def review_notification(sender, instance, created, **kwargs):
    """Create notifications when a review is created"""
    if created:
        notify_new_review(instance)


@receiver(post_save, sender=ReviewResponse)
def review_response_notification(sender, instance, created, **kwargs):
    """Create notifications when a review response is created"""
    if created:
        notify_review_response(instance.review, instance)


@receiver(post_save, sender=ServiceProviderProfile)
def service_provider_approval_notification(sender, instance, created, **kwargs):
    """Create notifications when a service provider is created"""
    # Since ServiceProviderProfile doesn't have approval_status,
    # we'll just notify when a new profile is created
    if created:
        notify_service_provider_approval(instance)
