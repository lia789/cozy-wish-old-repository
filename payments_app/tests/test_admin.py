from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice
from payments_app.admin import PaymentMethodAdmin, TransactionAdmin, InvoiceAdmin

User = get_user_model()

class AdminTest(TestCase):
    """Test the admin interface for the payments_app"""
    
    def setUp(self):
        # Create a superuser
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create a client
        self.client = Client()
        
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
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
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            transaction=self.transaction,
            amount=Decimal('100.00'),
            status='paid',
            issue_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
            paid_date=timezone.now()
        )
    
    def test_payment_method_admin(self):
        """Test the PaymentMethodAdmin"""
        # Check that the PaymentMethodAdmin has the expected attributes
        self.assertEqual(PaymentMethodAdmin.list_display, ('user', 'payment_type', 'name', 'last_four', 'is_default', 'created_at'))
        self.assertEqual(PaymentMethodAdmin.list_filter, ('payment_type', 'is_default', 'created_at'))
        self.assertEqual(PaymentMethodAdmin.search_fields, ('user__email', 'name', 'last_four'))
        self.assertEqual(PaymentMethodAdmin.date_hierarchy, 'created_at')
        
        # Check that the admin page loads
        url = reverse('admin:payments_app_paymentmethod_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the payment method is in the response
        self.assertContains(response, 'John Doe')
        self.assertContains(response, '1234')
        
        # Check that the admin detail page loads
        url = reverse('admin:payments_app_paymentmethod_change', args=[self.payment_method.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, '1234')
    
    def test_transaction_admin(self):
        """Test the TransactionAdmin"""
        # Check that the TransactionAdmin has the expected attributes
        self.assertEqual(TransactionAdmin.list_display, ('transaction_id', 'user', 'booking', 'amount', 'status', 'payment_method', 'created_at'))
        self.assertEqual(TransactionAdmin.list_filter, ('status', 'payment_method', 'created_at'))
        self.assertEqual(TransactionAdmin.search_fields, ('transaction_id', 'user__email', 'booking__booking_id', 'payment_method_details'))
        self.assertEqual(TransactionAdmin.date_hierarchy, 'created_at')
        self.assertEqual(TransactionAdmin.readonly_fields, ('transaction_id', 'created_at', 'updated_at'))
        
        # Check that the admin page loads
        url = reverse('admin:payments_app_transaction_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is in the response
        self.assertContains(response, str(self.transaction.id))
        self.assertContains(response, '100.00')
        
        # Check that the admin detail page loads
        url = reverse('admin:payments_app_transaction_change', args=[self.transaction.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.transaction.id))
        self.assertContains(response, '100.00')
    
    def test_invoice_admin(self):
        """Test the InvoiceAdmin"""
        # Check that the InvoiceAdmin has the expected attributes
        self.assertEqual(InvoiceAdmin.list_display, ('invoice_number', 'user', 'booking', 'amount', 'status', 'issue_date', 'due_date', 'paid_date'))
        self.assertEqual(InvoiceAdmin.list_filter, ('status', 'issue_date', 'due_date', 'paid_date'))
        self.assertEqual(InvoiceAdmin.search_fields, ('invoice_number', 'user__email', 'booking__booking_id'))
        self.assertEqual(InvoiceAdmin.date_hierarchy, 'issue_date')
        self.assertEqual(InvoiceAdmin.readonly_fields, ('invoice_number', 'issue_date'))
        
        # Check that the admin page loads
        url = reverse('admin:payments_app_invoice_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the invoice is in the response
        self.assertContains(response, str(self.invoice.invoice_number))
        self.assertContains(response, '100.00')
        
        # Check that the admin detail page loads
        url = reverse('admin:payments_app_invoice_change', args=[self.invoice.invoice_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.invoice.invoice_number))
        self.assertContains(response, '100.00')
