from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class CustomerViewsTest(TestCase):
    """Test the customer views in the payments_app"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True,
            first_name='John',
            last_name='Doe'
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
        
        # URLs
        self.payment_methods_url = reverse('payments_app:payment_methods')
        self.add_payment_method_url = reverse('payments_app:add_payment_method')
        self.edit_payment_method_url = reverse('payments_app:edit_payment_method', args=[self.payment_method.id])
        self.delete_payment_method_url = reverse('payments_app:delete_payment_method', args=[self.payment_method.id])
        self.set_default_payment_method_url = reverse('payments_app:set_default_payment_method', args=[self.payment_method.id])
        self.payment_history_url = reverse('payments_app:payment_history')
        self.payment_detail_url = reverse('payments_app:payment_detail', args=[self.transaction.id])
        self.invoice_list_url = reverse('payments_app:invoice_list')
        self.invoice_detail_url = reverse('payments_app:invoice_detail', args=[self.invoice.invoice_number])
        self.download_invoice_url = reverse('payments_app:download_invoice', args=[self.invoice.invoice_number])
        self.request_refund_url = reverse('payments_app:request_refund', args=[self.transaction.id])
    
    def test_payment_methods_view(self):
        """Test the payment_methods view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the payment methods page
        response = self.client.get(self.payment_methods_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/payment_methods.html')
        self.assertIn('payment_methods', response.context)
        self.assertEqual(len(response.context['payment_methods']), 1)
        self.assertEqual(response.context['payment_methods'][0], self.payment_method)
    
    def test_add_payment_method_view(self):
        """Test the add_payment_method view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the add payment method page
        response = self.client.get(self.add_payment_method_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/add_payment_method.html')
        self.assertIn('form', response.context)
        
        # Post a new payment method
        response = self.client.post(self.add_payment_method_url, {
            'payment_type': 'debit_card',
            'name': 'John Doe',
            'last_four': '5678',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'is_default': False
        })
        
        # Check that the payment method was created
        self.assertRedirects(response, self.payment_methods_url)
        self.assertEqual(PaymentMethod.objects.count(), 2)
        self.assertTrue(PaymentMethod.objects.filter(payment_type='debit_card', last_four='5678').exists())
    
    def test_edit_payment_method_view(self):
        """Test the edit_payment_method view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the edit payment method page
        response = self.client.get(self.edit_payment_method_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/edit_payment_method.html')
        self.assertIn('form', response.context)
        self.assertIn('payment_method', response.context)
        self.assertEqual(response.context['payment_method'], self.payment_method)
        
        # Post updated payment method
        response = self.client.post(self.edit_payment_method_url, {
            'payment_type': 'credit_card',
            'name': 'John Doe Updated',
            'last_four': '1234',
            'expiry_date': (timezone.now().date() + timedelta(days=730)).strftime('%Y-%m-%d'),
            'is_default': True
        })
        
        # Check that the payment method was updated
        self.assertRedirects(response, self.payment_methods_url)
        self.payment_method.refresh_from_db()
        self.assertEqual(self.payment_method.name, 'John Doe Updated')
        self.assertEqual(self.payment_method.expiry_date, timezone.now().date() + timedelta(days=730))
    
    def test_delete_payment_method_view(self):
        """Test the delete_payment_method view"""
        # Create a non-default payment method
        non_default_payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='debit_card',
            name='John Doe',
            last_four='5678',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=False
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the delete payment method page
        response = self.client.get(reverse('payments_app:delete_payment_method', args=[non_default_payment_method.id]))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/delete_payment_method.html')
        self.assertIn('payment_method', response.context)
        self.assertEqual(response.context['payment_method'], non_default_payment_method)
        
        # Post to delete the payment method
        response = self.client.post(reverse('payments_app:delete_payment_method', args=[non_default_payment_method.id]))
        
        # Check that the payment method was deleted
        self.assertRedirects(response, self.payment_methods_url)
        self.assertEqual(PaymentMethod.objects.count(), 1)
        self.assertFalse(PaymentMethod.objects.filter(id=non_default_payment_method.id).exists())
    
    def test_delete_default_payment_method_view(self):
        """Test the delete_payment_method view with a default payment method"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the delete payment method page
        response = self.client.get(self.delete_payment_method_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/delete_payment_method.html')
        self.assertIn('payment_method', response.context)
        self.assertEqual(response.context['payment_method'], self.payment_method)
        
        # Post to delete the payment method
        response = self.client.post(self.delete_payment_method_url)
        
        # Check that the payment method was not deleted (because it's the default)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/delete_payment_method.html')
        self.assertIn('error', response.context)
        self.assertEqual(PaymentMethod.objects.count(), 1)
        self.assertTrue(PaymentMethod.objects.filter(id=self.payment_method.id).exists())
    
    def test_set_default_payment_method_view(self):
        """Test the set_default_payment_method view"""
        # Create a non-default payment method
        non_default_payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='debit_card',
            name='John Doe',
            last_four='5678',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=False
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Post to set the non-default payment method as default
        response = self.client.post(reverse('payments_app:set_default_payment_method', args=[non_default_payment_method.id]))
        
        # Check that the payment method was set as default
        self.assertRedirects(response, self.payment_methods_url)
        non_default_payment_method.refresh_from_db()
        self.payment_method.refresh_from_db()
        self.assertTrue(non_default_payment_method.is_default)
        self.assertFalse(self.payment_method.is_default)
    
    def test_payment_history_view(self):
        """Test the payment_history view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the payment history page
        response = self.client.get(self.payment_history_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/payment_history.html')
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(response.context['transactions'][0], self.transaction)
    
    def test_payment_detail_view(self):
        """Test the payment_detail view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the payment detail page
        response = self.client.get(self.payment_detail_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/payment_detail.html')
        self.assertIn('transaction', response.context)
        self.assertEqual(response.context['transaction'], self.transaction)
    
    def test_invoice_list_view(self):
        """Test the invoice_list view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the invoice list page
        response = self.client.get(self.invoice_list_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/invoice_list.html')
        self.assertIn('invoices', response.context)
        self.assertEqual(len(response.context['invoices']), 1)
        self.assertEqual(response.context['invoices'][0], self.invoice)
    
    def test_invoice_detail_view(self):
        """Test the invoice_detail view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the invoice detail page
        response = self.client.get(self.invoice_detail_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/invoice_detail.html')
        self.assertIn('invoice', response.context)
        self.assertEqual(response.context['invoice'], self.invoice)
    
    def test_download_invoice_view(self):
        """Test the download_invoice view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the download invoice page
        response = self.client.get(self.download_invoice_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="invoice_{self.invoice.invoice_number}.pdf"')
    
    def test_request_refund_view(self):
        """Test the request_refund view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the request refund page
        response = self.client.get(self.request_refund_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/request_refund.html')
        self.assertIn('transaction', response.context)
        self.assertEqual(response.context['transaction'], self.transaction)
        self.assertIn('form', response.context)
        
        # Post a refund request
        response = self.client.post(self.request_refund_url, {
            'reason': 'I changed my mind'
        })
        
        # Check that the refund request was submitted
        self.assertRedirects(response, self.payment_history_url)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'refunded')
        self.assertEqual(self.transaction.notes, 'Refund requested: I changed my mind')
        
        # Check that the booking was cancelled
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.booking.cancellation_reason, 'Payment refunded')
        
        # Check that the invoice was cancelled
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'cancelled')
