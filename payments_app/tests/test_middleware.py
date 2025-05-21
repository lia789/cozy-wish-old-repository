from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking
from venues_app.models import Venue, Category
from payments_app.models import Invoice
from payments_app.middleware import InvoiceReminderMiddleware

User = get_user_model()

class InvoiceReminderMiddlewareTest(TestCase):
    """Test the InvoiceReminderMiddleware"""
    
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
        
        # Create an invoice that's due soon
        self.due_soon_invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            issue_date=timezone.now() - timedelta(days=6),
            due_date=timezone.now() + timedelta(days=1)
        )
        
        # Create an invoice that's overdue
        self.overdue_invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('50.00'),
            status='pending',
            issue_date=timezone.now() - timedelta(days=8),
            due_date=timezone.now() - timedelta(days=1)
        )
        
        # Create a middleware instance
        self.middleware = InvoiceReminderMiddleware(lambda request: HttpResponse())
    
    def test_middleware_adds_due_soon_invoices_to_context(self):
        """Test that the middleware adds due soon invoices to the context"""
        # Create a request
        request = self.factory.get(reverse('venues_app:home'))
        request.user = self.customer
        
        # Process the request
        response = self.middleware(request)
        
        # Check that the due soon invoices are added to the request
        self.assertTrue(hasattr(request, 'due_soon_invoices'))
        self.assertEqual(len(request.due_soon_invoices), 1)
        self.assertEqual(request.due_soon_invoices[0], self.due_soon_invoice)
    
    def test_middleware_adds_overdue_invoices_to_context(self):
        """Test that the middleware adds overdue invoices to the context"""
        # Create a request
        request = self.factory.get(reverse('venues_app:home'))
        request.user = self.customer
        
        # Process the request
        response = self.middleware(request)
        
        # Check that the overdue invoices are added to the request
        self.assertTrue(hasattr(request, 'overdue_invoices'))
        self.assertEqual(len(request.overdue_invoices), 1)
        self.assertEqual(request.overdue_invoices[0], self.overdue_invoice)
    
    def test_middleware_skips_anonymous_users(self):
        """Test that the middleware skips anonymous users"""
        # Create a request with an anonymous user
        request = self.factory.get(reverse('venues_app:home'))
        request.user = None
        
        # Process the request
        response = self.middleware(request)
        
        # Check that no invoices are added to the request
        self.assertFalse(hasattr(request, 'due_soon_invoices'))
        self.assertFalse(hasattr(request, 'overdue_invoices'))
    
    def test_middleware_skips_non_customer_users(self):
        """Test that the middleware skips non-customer users"""
        # Create a request with a provider user
        request = self.factory.get(reverse('venues_app:home'))
        request.user = self.provider
        
        # Process the request
        response = self.middleware(request)
        
        # Check that no invoices are added to the request
        self.assertFalse(hasattr(request, 'due_soon_invoices'))
        self.assertFalse(hasattr(request, 'overdue_invoices'))
    
    def test_middleware_skips_ajax_requests(self):
        """Test that the middleware skips AJAX requests"""
        # Create an AJAX request
        request = self.factory.get(
            reverse('venues_app:home'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.customer
        
        # Process the request
        response = self.middleware(request)
        
        # Check that no invoices are added to the request
        self.assertFalse(hasattr(request, 'due_soon_invoices'))
        self.assertFalse(hasattr(request, 'overdue_invoices'))
