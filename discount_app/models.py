from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from venues_app.models import Venue, Service
from decimal import Decimal


class DiscountType(models.TextChoices):
    """Discount type choices"""
    PERCENTAGE = 'percentage', 'Percentage'
    FIXED_AMOUNT = 'fixed_amount', 'Fixed Amount'


class DiscountStatus(models.TextChoices):
    """Discount status choices"""
    ACTIVE = 'active', 'Active'
    SCHEDULED = 'scheduled', 'Scheduled'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'


class DiscountBase(models.Model):
    """Base model for all discount types"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def is_active(self):
        """Check if the discount is currently active"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def get_status(self):
        """Get the current status of the discount"""
        now = timezone.now()
        if self.start_date > now:
            return DiscountStatus.SCHEDULED
        elif self.end_date < now:
            return DiscountStatus.EXPIRED
        else:
            return DiscountStatus.ACTIVE

    def calculate_discount(self, original_price):
        """Calculate the discount amount based on the discount type and value"""
        if self.discount_type == DiscountType.PERCENTAGE:
            # Ensure discount_value is between 0 and 100 for percentage
            percentage = min(max(self.discount_value, 0), 100)
            return (original_price * percentage) / 100
        else:  # Fixed amount
            # Ensure discount doesn't exceed the original price
            return min(self.discount_value, original_price)

    def calculate_discounted_price(self, original_price):
        """Calculate the final price after applying the discount"""
        discount_amount = self.calculate_discount(original_price)
        return max(original_price - discount_amount, 0)  # Ensure price doesn't go below 0


class VenueDiscount(DiscountBase):
    """Discount applied to an entire venue"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='discounts')
    min_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_venue_discounts')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Venue Discount'
        verbose_name_plural = 'Venue Discounts'


class ServiceDiscount(DiscountBase):
    """Discount applied to a specific service"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='discounts')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_service_discounts')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Discount'
        verbose_name_plural = 'Service Discounts'


class PlatformDiscount(DiscountBase):
    """Platform-wide discount created by admins"""
    category = models.ForeignKey('venues_app.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='platform_discounts')
    min_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Platform Discount'
        verbose_name_plural = 'Platform Discounts'


class DiscountUsage(models.Model):
    """Track discount usage by customers"""
    DISCOUNT_MODEL_CHOICES = [
        ('VenueDiscount', 'Venue Discount'),
        ('ServiceDiscount', 'Service Discount'),
        ('PlatformDiscount', 'Platform Discount'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discount_usages')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_MODEL_CHOICES)
    discount_id = models.PositiveIntegerField()
    booking = models.ForeignKey('booking_cart_app.Booking', on_delete=models.CASCADE, related_name='discount_usages')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Discount Usage'
        verbose_name_plural = 'Discount Usages'

    def __str__(self):
        return f"{self.user.email} - {self.discount_type} - {self.used_at.strftime('%Y-%m-%d')}"

