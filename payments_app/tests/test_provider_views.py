from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking
from venues_app.models import Venue, Category
from payments_app.models import Transaction, Invoice

User = get_user_model()

class ProviderViewsTest(TestCase):
    """Test the provider views in the payments_app"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
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
            status='confirmed'
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
        
        # Login the provider
        self.client.login(email='provider@example.com', password='testpass123')
    
    def test_provider_payment_history_view(self):
        """Test the provider_payment_history view"""
        # Get the provider payment history page
        response = self.client.get(reverse('payments_app:provider_payment_history'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the transactions are in the context
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(response.context['transactions'][0], self.transaction)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'payments_app/provider/payment_history.html')
    
    def test_provider_payment_detail_view(self):
        """Test the provider_payment_detail view"""
        # Get the provider payment detail page
        response = self.client.get(
            reverse('payments_app:provider_payment_detail', args=[self.transaction.transaction_id])
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction, booking, and invoice are in the context
        self.assertIn('transaction', response.context)
        self.assertEqual(response.context['transaction'], self.transaction)
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'], self.booking)
        self.assertIn('invoice', response.context)
        self.assertEqual(response.context['invoice'], self.invoice)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'payments_app/provider/payment_detail.html')
    
    def test_provider_invoice_list_view(self):
        """Test the provider_invoice_list view"""
        # Get the provider invoice list page
        response = self.client.get(reverse('payments_app:provider_invoice_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the invoices are in the context
        self.assertIn('invoices', response.context)
        self.assertEqual(len(response.context['invoices']), 1)
        self.assertEqual(response.context['invoices'][0], self.invoice)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'payments_app/provider/invoice_list.html')
    
    def test_provider_invoice_detail_view(self):
        """Test the provider_invoice_detail view"""
        # Get the provider invoice detail page
        response = self.client.get(
            reverse('payments_app:provider_invoice_detail', args=[self.invoice.invoice_number])
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the invoice, booking, and transaction are in the context
        self.assertIn('invoice', response.context)
        self.assertEqual(response.context['invoice'], self.invoice)
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'], self.booking)
        self.assertIn('transaction', response.context)
        self.assertEqual(response.context['transaction'], self.transaction)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'payments_app/provider/invoice_detail.html')
    
    def test_provider_download_invoice_view(self):
        """Test the provider_download_invoice view"""
        # Get the provider download invoice page
        response = self.client.get(
            reverse('payments_app:provider_download_invoice', args=[self.invoice.invoice_number])
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the response is a PDF
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Check that the filename is correct
        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename="invoice_{self.invoice.invoice_number}.pdf"'
        )
    
    def test_provider_payment_dashboard_view(self):
        """Test the provider_payment_dashboard view"""
        # Get the provider payment dashboard page
        response = self.client.get(reverse('payments_app:provider_payment_dashboard'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the context contains the expected data
        self.assertIn('total_revenue', response.context)
        self.assertEqual(response.context['total_revenue'], Decimal('100.00'))
        self.assertIn('recent_transactions', response.context)
        self.assertEqual(len(response.context['recent_transactions']), 1)
        self.assertEqual(response.context['recent_transactions'][0], self.transaction)
        self.assertIn('pending_invoices', response.context)
        self.assertEqual(len(response.context['pending_invoices']), 0)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'payments_app/provider/payment_dashboard.html')
