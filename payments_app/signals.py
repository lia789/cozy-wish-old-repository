from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from booking_cart_app.models import Booking
from .models import Invoice, Transaction

# Check if notifications_app is installed
NOTIFICATIONS_ENABLED = 'notifications_app' in settings.INSTALLED_APPS
if NOTIFICATIONS_ENABLED:
    try:
        from notifications_app.utils import send_notification
    except ImportError:
        NOTIFICATIONS_ENABLED = False


@receiver(post_save, sender=Booking)
def create_invoice_for_booking(sender, instance, created, **kwargs):
    """
    Create an invoice for a booking when it is created
    """
    if created:
        # Create invoice for the booking
        Invoice.objects.create(
            user=instance.user,
            booking=instance,
            amount=instance.total_price,
            status='pending',
        )


@receiver(post_save, sender=Transaction)
def update_booking_status_on_transaction(sender, instance, created, **kwargs):
    """
    Update booking status when a transaction is created or updated
    """
    if instance.status == 'completed':
        # Update booking status to confirmed
        booking = instance.booking
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])

        # Update invoice status to paid
        try:
            invoice = Invoice.objects.get(booking=booking)
            invoice.status = 'paid'
            invoice.transaction = instance
            invoice.paid_date = timezone.now()
            invoice.save(update_fields=['status', 'transaction', 'paid_date'])
        except Invoice.DoesNotExist:
            pass

        # Send notification if enabled
        if NOTIFICATIONS_ENABLED:
            # Notify customer
            send_notification(
                user=instance.user,
                title='Payment Completed',
                message=f'Your payment of ${instance.amount} has been completed successfully.',
                notification_type='payment_completed',
                related_object=instance
            )

            # Notify service provider
            if booking.venue and booking.venue.owner:
                send_notification(
                    user=booking.venue.owner,
                    title='Payment Received',
                    message=f'You have received a payment of ${instance.amount} for booking #{booking.booking_id}.',
                    notification_type='payment_received',
                    related_object=instance
                )

    elif instance.status == 'refunded':
        # Update booking status to cancelled
        booking = instance.booking
        booking.status = 'cancelled'
        booking.cancellation_reason = instance.notes or 'Payment refunded'
        booking.save(update_fields=['status', 'cancellation_reason'])

        # Update invoice status to cancelled
        try:
            invoice = Invoice.objects.get(booking=booking)
            invoice.status = 'cancelled'
            invoice.save(update_fields=['status'])
        except Invoice.DoesNotExist:
            pass

        # Send notification if enabled
        if NOTIFICATIONS_ENABLED:
            send_notification(
                user=instance.user,
                title='Payment Refunded',
                message=f'Your payment of ${instance.amount} has been refunded.',
                notification_type='payment_refunded',
                related_object=instance
            )

            # Notify service provider
            if booking.venue and booking.venue.owner:
                send_notification(
                    user=booking.venue.owner,
                    title='Payment Refunded',
                    message=f'A payment of ${instance.amount} for booking #{booking.booking_id} has been refunded.',
                    notification_type='payment_refunded',
                    related_object=instance
                )
