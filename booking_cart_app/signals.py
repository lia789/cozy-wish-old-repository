from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Booking, BookingItem, ServiceAvailability


@receiver(post_save, sender=BookingItem)
def update_service_availability_on_booking_item_create(sender, instance, created, **kwargs):
    """
    Update service availability when a booking item is created
    """
    if created and instance.booking.status in ['pending', 'confirmed']:
        try:
            availability = ServiceAvailability.objects.get(
                service=instance.service,
                date=instance.date,
                time_slot=instance.time_slot
            )
            availability.increment_bookings()
        except ServiceAvailability.DoesNotExist:
            # Create availability if it doesn't exist
            availability = ServiceAvailability.objects.create(
                service=instance.service,
                date=instance.date,
                time_slot=instance.time_slot,
                max_bookings=10,
                current_bookings=1,
                is_available=True
            )


@receiver(post_delete, sender=BookingItem)
def update_service_availability_on_booking_item_delete(sender, instance, **kwargs):
    """
    Update service availability when a booking item is deleted
    """
    try:
        availability = ServiceAvailability.objects.get(
            service=instance.service,
            date=instance.date,
            time_slot=instance.time_slot
        )
        availability.decrement_bookings()
    except ServiceAvailability.DoesNotExist:
        pass


@receiver(post_save, sender=Booking)
def update_service_availability_on_booking_status_change(sender, instance, **kwargs):
    """
    Update service availability when a booking status changes
    """
    # Get the old status from the instance's __dict__ if it exists
    old_status = instance._old_status if hasattr(instance, '_old_status') else None
    
    # If this is a status change to or from cancelled/completed
    if old_status and instance.status != old_status:
        # If booking was active and now is cancelled/completed
        if old_status in ['pending', 'confirmed'] and instance.status in ['cancelled', 'completed', 'disputed', 'no_show']:
            # Decrement availability for all booking items
            for item in instance.items.all():
                try:
                    availability = ServiceAvailability.objects.get(
                        service=item.service,
                        date=item.date,
                        time_slot=item.time_slot
                    )
                    availability.decrement_bookings()
                except ServiceAvailability.DoesNotExist:
                    pass
        
        # If booking was cancelled/completed and now is active again
        elif old_status in ['cancelled', 'completed', 'disputed', 'no_show'] and instance.status in ['pending', 'confirmed']:
            # Increment availability for all booking items
            for item in instance.items.all():
                try:
                    availability = ServiceAvailability.objects.get(
                        service=item.service,
                        date=item.date,
                        time_slot=item.time_slot
                    )
                    availability.increment_bookings()
                except ServiceAvailability.DoesNotExist:
                    # Create availability if it doesn't exist
                    availability = ServiceAvailability.objects.create(
                        service=item.service,
                        date=item.date,
                        time_slot=item.time_slot,
                        max_bookings=10,
                        current_bookings=1,
                        is_available=True
                    )
