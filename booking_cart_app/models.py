from django.db import models
from django.conf import settings
from django.utils import timezone
from venues_app.models import Service, Venue
import uuid
from datetime import timedelta


class CartItem(models.Model):
    """Model for storing items in a user's cart"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    time_slot = models.TimeField()
    added_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['date', 'time_slot']
        unique_together = ['user', 'service', 'date', 'time_slot']

    def __str__(self):
        return f"{self.user.email} - {self.service.title} - {self.date} {self.time_slot}"

    def save(self, *args, **kwargs):
        # Set expiration time to 24 hours from now if not already set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the cart item has expired"""
        return timezone.now() > self.expires_at

    def get_total_price(self):
        """Calculate the total price for this cart item"""
        if self.service.discounted_price:
            return self.service.discounted_price * self.quantity
        return self.service.price * self.quantity

    def get_discount_info(self):
        """Get discount information for this cart item"""
        if hasattr(self.service, 'get_discount_info'):
            return self.service.get_discount_info()
        return None


class Booking(models.Model):
    """Model for storing bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),  # Added for dispute handling
        ('no_show', 'No Show'),  # Added for no-show handling
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    dispute_reason = models.TextField(blank=True)  # Added for dispute handling
    last_status_change = models.DateTimeField(auto_now=True)  # Track when status changes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the original status to track changes
        self._old_status = self.status if self.pk else None

    def save(self, *args, **kwargs):
        # Update last_status_change if status has changed
        if self.pk and hasattr(self, '_old_status') and self._old_status != self.status:
            self.last_status_change = timezone.now()
        super().save(*args, **kwargs)
        # Update _old_status after save
        self._old_status = self.status

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.email}"

    def get_earliest_service_datetime(self):
        """Get the earliest service datetime for this booking"""
        earliest_item = self.items.order_by('date', 'time_slot').first()
        if not earliest_item:
            return None

        # Convert date and time_slot to datetime
        return timezone.make_aware(
            timezone.datetime.combine(earliest_item.date, earliest_item.time_slot)
        )

    def can_cancel(self):
        """Check if the booking can be cancelled (within 6 hours of booking)"""
        # Check if booking is already cancelled or completed
        if self.status in ['cancelled', 'completed']:
            return False

        # Get the earliest service datetime
        service_datetime = self.get_earliest_service_datetime()
        if not service_datetime:
            return False

        # Check if service datetime is more than 6 hours from now
        return service_datetime > (timezone.now() + timedelta(hours=6))

    def cancel(self, reason=''):
        """Cancel the booking"""
        if self.can_cancel():
            self.status = 'cancelled'
            self.cancellation_reason = reason
            self.save()
            return True
        return False

    def is_upcoming(self):
        """Check if the booking is upcoming"""
        if self.status not in ['confirmed', 'pending']:
            return False

        # Get the earliest service datetime
        service_datetime = self.get_earliest_service_datetime()
        if not service_datetime:
            return False

        # Check if service datetime is in the future
        return service_datetime > timezone.now()

    def is_past_due(self):
        """Check if the booking is past due"""
        if self.status not in ['confirmed', 'pending']:
            return False

        # Get the earliest service datetime
        service_datetime = self.get_earliest_service_datetime()
        if not service_datetime:
            return False

        # Check if service datetime is in the past
        return service_datetime < timezone.now()

    def file_dispute(self, reason=''):
        """File a dispute for this booking"""
        if self.status not in ['cancelled', 'disputed']:
            self.status = 'disputed'
            self.dispute_reason = reason
            self.save()
            return True
        return False


class BookingItem(models.Model):
    """Model for storing items in a booking"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_title = models.CharField(max_length=255)  # Store title in case service is deleted
    service_price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of booking
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    time_slot = models.TimeField()

    class Meta:
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f"{self.service_title} - {self.date} {self.time_slot}"

    def get_total_price(self):
        """Calculate the total price for this booking item"""
        return self.service_price * self.quantity


class ServiceAvailability(models.Model):
    """Model for storing service availability"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    time_slot = models.TimeField()
    max_bookings = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Service Availabilities'
        ordering = ['date', 'time_slot']
        unique_together = ['service', 'date', 'time_slot']

    def __str__(self):
        return f"{self.service.title} - {self.date} {self.time_slot}"

    def is_fully_booked(self):
        """Check if the service is fully booked for this time slot"""
        return self.current_bookings >= self.max_bookings or not self.is_available

    def increment_bookings(self):
        """Increment the number of bookings for this time slot"""
        if not self.is_fully_booked():
            self.current_bookings += 1
            if self.current_bookings >= self.max_bookings:
                self.is_available = False
            self.save()
            return True
        return False

    def decrement_bookings(self):
        """Decrement the number of bookings for this time slot"""
        if self.current_bookings > 0:
            self.current_bookings -= 1
            self.is_available = True
            self.save()
            return True
        return False
