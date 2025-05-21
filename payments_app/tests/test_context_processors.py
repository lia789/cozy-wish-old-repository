from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking
from venues_app.models import Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice
from payments_app.context_processors import payment_context

User = get_user_model()

class PaymentContextProcessorTest(TestCase):
    """Test the payment_context context processor"""
    
    def setUp(self):
        # Create a request factory
        self.factory = RequestFactory()
        
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
        
        # Create a payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )
        
        # Create a transaction
        self.transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Create an invoice
        self.invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            transaction=self.transaction,
            amount=Decimal('100.00'),
            status='paid',
            issue_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
            paid_date=timezone.now()
        )
    
    def test_payment_context_for_customer(self):
        """Test the payment_context context processor for a customer"""
        # Create a request
        request = self.factory.get(reverse('venues_app:home'))
        request.user = self.customer
        
        # Call the context processor
        context = payment_context(request)
        
        # Check that the context contains the expected data
        self.assertIn('payment_methods_count', context)
        self.assertEqual(context['payment_methods_count'], 1)
        self.assertIn('pending_invoices_count', context)
        self.assertEqual(context['pending_invoices_count'], 0)
        self.assertIn('recent_transactions', context)
        self.assertEqual(len(context['recent_transactions']), 1)
        self.assertEqual(context['recent_transactions'][0], self.transaction)
    
    def test_payment_context_for_provider(self):
        """Test the payment_context context processor for a provider"""
        # Create a request
        request = self.factory.get(reverse('venues_app:home'))
        request.user = self.provider
        
        # Call the context processor
        context = payment_context(request)
        
        # Check that the context contains the expected data
        self.assertIn('provider_pending_invoices_count', context)
        self.assertEqual(context['provider_pending_invoices_count'], 0)
        self.assertIn('provider_recent_transactions', context)
        self.assertEqual(len(context['provider_recent_transactions']), 1)
        self.assertEqual(context['provider_recent_transactions'][0], self.transaction)
        self.assertIn('provider_total_revenue', context)
        self.assertEqual(context['provider_total_revenue'], Decimal('100.00'))
    
    def test_payment_context_for_anonymous_user(self):
        """Test the payment_context context processor for an anonymous user"""
        # Create a request with an anonymous user
        request = self.factory.get(reverse('venues_app:home'))
        request.user = None
        
        # Call the context processor
        context = payment_context(request)
        
        # Check that the context is empty
        self.assertEqual(context, {})
