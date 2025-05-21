from django.db import models
from django.conf import settings
from django.utils import timezone
from booking_cart_app.models import Booking
import uuid


class PaymentMethod(models.Model):
    """Model for storing payment method information"""
    PAYMENT_TYPE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    name = models.CharField(max_length=100)  # Name on card or account name
    # For MVP, we're not storing actual card details for security reasons
    # In a real app, you would use a payment processor like Stripe
    last_four = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits of card
    expiry_date = models.DateField(blank=True, null=True)  # Card expiry date
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.name} - {self.last_four or 'N/A'}"

    def save(self, *args, **kwargs):
        # If this payment method is set as default, unset default for all other payment methods
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # If this is the only payment method, set it as default
        elif not PaymentMethod.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Model for storing payment transaction information"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_method_details = models.CharField(max_length=100, blank=True)  # e.g., "Visa ending in 1234"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.booking.booking_id} - {self.amount}"


class Invoice(models.Model):
    """Model for storing invoice information"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.booking.booking_id} - {self.amount}"

    def save(self, *args, **kwargs):
        # Set due date to 24 hours from issue date if not already set
        if not self.due_date:
            self.due_date = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def mark_as_paid(self, transaction=None):
        """Mark the invoice as paid"""
        self.status = 'paid'
        self.paid_date = timezone.now()
        if transaction:
            self.transaction = transaction
        self.save()

    def is_overdue(self):
        """Check if the invoice is overdue"""
        return self.status == 'pending' and timezone.now() > self.due_date


class CheckoutSession(models.Model):
    """Model for tracking related bookings from a single checkout session"""
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkout_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Checkout Session {self.session_id} - {self.user.email}"

    def mark_as_paid(self):
        """Mark the checkout session as paid"""
        self.is_paid = True
        self.save()


class CheckoutSessionBooking(models.Model):
    """Model for storing bookings associated with a checkout session"""
    checkout_session = models.ForeignKey(CheckoutSession, on_delete=models.CASCADE, related_name='bookings')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='checkout_session_booking')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Session {self.checkout_session.session_id} - Booking {self.booking.booking_id}"
