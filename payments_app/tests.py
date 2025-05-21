from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from booking_cart_app.models import Booking
from venues_app.models import Venue, Service
from .models import PaymentMethod, Transaction, Invoice


User = get_user_model()


class PaymentsAppTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='password123',
            is_customer=True
        )
        self.service_provider = User.objects.create_user(
            email='provider@example.com',
            password='password123',
            is_service_provider=True
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='password123',
            is_staff=True
        )

        # Create test venue and service
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.service_provider,
            description='Test Description',
            address='123 Test St',
            city='Test City',
            state='Test State',
            zip_code='12345',
            is_active=True
        )

        self.service = Service.objects.create(
            venue=self.venue,
            title='Test Service',
            description='Test Description',
            price=100.00,
            duration=60,
            is_active=True
        )

        # Create test booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=100.00,
            status='pending'
        )

        # Create test payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )

        # Create test transaction
        self.transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=100.00,
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )

        # Create test invoice
        self.invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            transaction=self.transaction,
            amount=100.00,
            status='paid',
            due_date=timezone.now() + timedelta(hours=24),
            paid_date=timezone.now()
        )

        # Set up client
        self.client = Client()

    def test_payment_method_default(self):
        """Test that only one payment method can be default"""
        # Create another payment method
        payment_method2 = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='debit_card',
            name='John Doe',
            last_four='5678',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )

        # Refresh the first payment method
        self.payment_method.refresh_from_db()

        # Check that the first payment method is no longer default
        self.assertFalse(self.payment_method.is_default)
        self.assertTrue(payment_method2.is_default)

    def test_invoice_mark_as_paid(self):
        """Test that invoice can be marked as paid"""
        # Create a pending invoice
        invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=100.00,
            status='pending',
            due_date=timezone.now() + timedelta(hours=24)
        )

        # Mark as paid
        invoice.mark_as_paid(transaction=self.transaction)

        # Check that the invoice is now paid
        self.assertEqual(invoice.status, 'paid')
        self.assertIsNotNone(invoice.paid_date)
        self.assertEqual(invoice.transaction, self.transaction)

    def test_invoice_is_overdue(self):
        """Test that invoice can be checked for overdue status"""
        # Create a pending invoice with due date in the past
        invoice = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=100.00,
            status='pending',
            due_date=timezone.now() - timedelta(hours=1)
        )

        # Check that the invoice is overdue
        self.assertTrue(invoice.is_overdue())

        # Create a pending invoice with due date in the future
        invoice2 = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=100.00,
            status='pending',
            due_date=timezone.now() + timedelta(hours=1)
        )

        # Check that the invoice is not overdue
        self.assertFalse(invoice2.is_overdue())

        # Create a paid invoice with due date in the past
        invoice3 = Invoice.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=100.00,
            status='paid',
            due_date=timezone.now() - timedelta(hours=1),
            paid_date=timezone.now()
        )

        # Check that the invoice is not overdue (because it's paid)
        self.assertFalse(invoice3.is_overdue())

    def test_customer_payment_process_view(self):
        """Test that customer can access payment process view"""
        # Login as customer
        self.client.login(email='customer@example.com', password='password123')

        # Access payment process view
        response = self.client.get(reverse('payments_app:payment_process', args=[self.booking.booking_id]))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/payment_process.html')

    def test_service_provider_payment_history_view(self):
        """Test that service provider can access payment history view"""
        # Login as service provider
        self.client.login(email='provider@example.com', password='password123')

        # Access payment history view
        response = self.client.get(reverse('payments_app:provider_payment_history'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/provider/payment_history.html')

    def test_admin_payment_list_view(self):
        """Test that admin can access payment list view"""
        # Login as admin
        self.client.login(email='admin@example.com', password='password123')

        # Access payment list view
        response = self.client.get(reverse('payments_app:admin_payment_list'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments_app/admin/payment_list.html')

    def test_customer_cannot_access_admin_views(self):
        """Test that customer cannot access admin views"""
        # Login as customer
        self.client.login(email='customer@example.com', password='password123')

        # Try to access admin payment list view
        response = self.client.get(reverse('payments_app:admin_payment_list'))

        # Check that the response is a redirect (to home page)
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_access_service_provider_views(self):
        """Test that customer cannot access service provider views"""
        # Login as customer
        self.client.login(email='customer@example.com', password='password123')

        # Try to access service provider payment history view
        response = self.client.get(reverse('payments_app:provider_payment_history'))

        # Check that the response is a redirect (to home page)
        self.assertEqual(response.status_code, 302)
