from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import Transaction, Invoice

User = get_user_model()

class SignalsTest(TestCase):
    """Test the signals in the payments_app"""
    
    def setUp(self):
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create a provider user
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create a category
        self.category = Category.objects.create(name="Spa")
        
        # Create a venue
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Test Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city.",
            approval_status="approved"
        )
        
        # Create a booking
        self.booking = Booking.objects.create(
            booking_id=uuid.uuid4(),
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='pending'
        )
    
    def test_create_invoice_for_booking_signal(self):
        """Test that an invoice is created when a booking is created"""
        # Check that an invoice was created for the booking
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.user, self.customer)
        self.assertEqual(invoice.booking, self.booking)
        self.assertEqual(invoice.amount, Decimal('100.00'))
        self.assertEqual(invoice.status, 'pending')
    
    def test_update_booking_status_on_transaction_completed_signal(self):
        """Test that booking status is updated when a transaction is completed"""
        # Create a completed transaction
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Check that the booking status was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')
        
        # Check that the invoice status was updated
        invoice = Invoice.objects.get(booking=self.booking)
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(invoice.transaction, transaction)
        self.assertIsNotNone(invoice.paid_date)
    
    def test_update_booking_status_on_transaction_refunded_signal(self):
        """Test that booking status is updated when a transaction is refunded"""
        # Create a refunded transaction
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='refunded',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234',
            notes='Refund requested by customer'
        )
        
        # Check that the booking status was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.booking.cancellation_reason, 'Refund requested by customer')
        
        # Check that the invoice status was updated
        invoice = Invoice.objects.get(booking=self.booking)
        self.assertEqual(invoice.status, 'cancelled')
    
    def test_update_booking_status_on_transaction_failed_signal(self):
        """Test that booking status is not updated when a transaction fails"""
        # Create a failed transaction
        Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='failed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234',
            notes='Payment failed'
        )
        
        # Check that the booking status was not updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'pending')
        
        # Check that the invoice status was not updated
        invoice = Invoice.objects.get(booking=self.booking)
        self.assertEqual(invoice.status, 'pending')
