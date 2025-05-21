from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking
from venues_app.models import Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class PermissionsTest(TestCase):
    """Test the permissions in the payments_app"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create another customer user
        self.other_customer = User.objects.create_user(
            email='other_customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create a provider user
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create an admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
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
    
    def test_customer_can_access_own_payment_methods(self):
        """Test that a customer can access their own payment methods"""
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')
        
        # Access payment methods
        response = self.client.get(reverse('payments_app:payment_methods'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the payment method is in the context
        self.assertIn('payment_methods', response.context)
        self.assertEqual(len(response.context['payment_methods']), 1)
        self.assertEqual(response.context['payment_methods'][0], self.payment_method)
    
    def test_customer_cannot_access_other_customer_payment_methods(self):
        """Test that a customer cannot access another customer's payment methods"""
        # Create a payment method for the other customer
        other_payment_method = PaymentMethod.objects.create(
            user=self.other_customer,
            payment_type='credit_card',
            name='Jane Doe',
            last_four='5678',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )
        
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')
        
        # Try to access the other customer's payment method
        response = self.client.get(
            reverse('payments_app:edit_payment_method', args=[other_payment_method.id])
        )
        
        # Check that the response is a 404
        self.assertEqual(response.status_code, 404)
    
    def test_customer_can_access_own_transactions(self):
        """Test that a customer can access their own transactions"""
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')
        
        # Access payment history
        response = self.client.get(reverse('payments_app:payment_history'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is in the context
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(response.context['transactions'][0], self.transaction)
    
    def test_customer_cannot_access_other_customer_transactions(self):
        """Test that a customer cannot access another customer's transactions"""
        # Create a transaction for the other customer
        other_booking = Booking.objects.create(
            booking_id=uuid.uuid4(),
            user=self.other_customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        other_transaction = Transaction.objects.create(
            user=self.other_customer,
            booking=other_booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 5678'
        )
        
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')
        
        # Try to access the other customer's transaction
        response = self.client.get(
            reverse('payments_app:payment_detail', args=[other_transaction.transaction_id])
        )
        
        # Check that the response is a 404
        self.assertEqual(response.status_code, 404)
    
    def test_provider_can_access_own_venue_transactions(self):
        """Test that a provider can access transactions for their own venues"""
        # Login as provider
        self.client.login(email='provider@example.com', password='testpass123')
        
        # Access provider payment history
        response = self.client.get(reverse('payments_app:provider_payment_history'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is in the context
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(response.context['transactions'][0], self.transaction)
    
    def test_provider_cannot_access_other_venue_transactions(self):
        """Test that a provider cannot access transactions for other venues"""
        # Create another provider
        other_provider = User.objects.create_user(
            email='other_provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create another venue
        other_venue = Venue.objects.create(
            owner=other_provider,
            name="Other Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="456",
            street_name="Main St",
            about="Another luxury spa in the heart of the city.",
            approval_status="approved"
        )
        
        # Create a booking for the other venue
        other_booking = Booking.objects.create(
            booking_id=uuid.uuid4(),
            user=self.customer,
            venue=other_venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a transaction for the other booking
        other_transaction = Transaction.objects.create(
            user=self.customer,
            booking=other_booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Login as provider
        self.client.login(email='provider@example.com', password='testpass123')
        
        # Try to access the other venue's transaction
        response = self.client.get(
            reverse('payments_app:provider_payment_detail', args=[other_transaction.transaction_id])
        )
        
        # Check that the response is a 404
        self.assertEqual(response.status_code, 404)
    
    def test_admin_can_access_all_transactions(self):
        """Test that an admin can access all transactions"""
        # Login as admin
        self.client.login(email='admin@example.com', password='testpass123')
        
        # Access admin payment list
        response = self.client.get(reverse('payments_app:admin_payment_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is in the context
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)
        self.assertEqual(response.context['transactions'][0], self.transaction)
        
        # Create another transaction
        other_booking = Booking.objects.create(
            booking_id=uuid.uuid4(),
            user=self.other_customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        other_transaction = Transaction.objects.create(
            user=self.other_customer,
            booking=other_booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 5678'
        )
        
        # Access admin payment list again
        response = self.client.get(reverse('payments_app:admin_payment_list'))
        
        # Check that both transactions are in the context
        self.assertEqual(len(response.context['transactions']), 2)
        self.assertIn(self.transaction, response.context['transactions'])
        self.assertIn(other_transaction, response.context['transactions'])
    
    def test_anonymous_user_cannot_access_payment_pages(self):
        """Test that an anonymous user cannot access payment pages"""
        # Try to access payment methods
        response = self.client.get(reverse('payments_app:payment_methods'))
        
        # Check that the response redirects to login
        self.assertRedirects(
            response,
            f"{reverse('accounts_app:login')}?next={reverse('payments_app:payment_methods')}"
        )
        
        # Try to access payment history
        response = self.client.get(reverse('payments_app:payment_history'))
        
        # Check that the response redirects to login
        self.assertRedirects(
            response,
            f"{reverse('accounts_app:login')}?next={reverse('payments_app:payment_history')}"
        )
        
        # Try to access payment detail
        response = self.client.get(
            reverse('payments_app:payment_detail', args=[self.transaction.transaction_id])
        )
        
        # Check that the response redirects to login
        self.assertRedirects(
            response,
            f"{reverse('accounts_app:login')}?next={reverse('payments_app:payment_detail', args=[self.transaction.transaction_id])}"
        )
