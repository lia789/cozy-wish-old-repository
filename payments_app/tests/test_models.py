from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class PaymentMethodModelTest(TestCase):
    """Test the PaymentMethod model"""
    
    def setUp(self):
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True,
            first_name='John',
            last_name='Doe'
        )
    
    def test_payment_method_creation(self):
        """Test creating a payment method"""
        payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )
        
        self.assertEqual(payment_method.user, self.customer)
        self.assertEqual(payment_method.payment_type, 'credit_card')
        self.assertEqual(payment_method.name, 'John Doe')
        self.assertEqual(payment_method.last_four, '1234')
        self.assertTrue(payment_method.is_default)
    
    def test_payment_method_str(self):
        """Test the string representation of a payment method"""
        payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )
        
        self.assertEqual(str(payment_method), 'Credit Card ending in 1234')
    
    def test_payment_method_get_payment_type_display(self):
        """Test the get_payment_type_display method"""
        payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=365),
            is_default=True
        )
        
        self.assertEqual(payment_method.get_payment_type_display(), 'Credit Card')
    
    def test_payment_method_is_expired(self):
        """Test the is_expired method"""
        # Create a payment method that expires tomorrow
        payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.now().date() + timedelta(days=1),
            is_default=True
        )
        
        # Check that it's not expired
        self.assertFalse(payment_method.is_expired())
        
        # Create a payment method that expired yesterday
        expired_payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='5678',
            expiry_date=timezone.now().date() - timedelta(days=1),
            is_default=False
        )
        
        # Check that it's expired
        self.assertTrue(expired_payment_method.is_expired())
        
        # Create a payment method with no expiry date (e.g., PayPal)
        no_expiry_payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='paypal',
            name='John Doe PayPal',
            is_default=False
        )
        
        # Check that it's not expired
        self.assertFalse(no_expiry_payment_method.is_expired())

class TransactionModelTest(TestCase):
    """Test the Transaction model"""
    
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
    
    def test_transaction_creation(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        self.assertEqual(transaction.user, self.customer)
        self.assertEqual(transaction.booking, self.booking)
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.status, 'completed')
        self.assertEqual(transaction.payment_method, 'credit_card')
        self.assertEqual(transaction.payment_method_details, 'Credit Card ending in 1234')
    
    def test_transaction_str(self):
        """Test the string representation of a transaction"""
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        self.assertEqual(str(transaction), f'Transaction {transaction.id} - $100.00')
    
    def test_transaction_get_status_display(self):
        """Test the get_status_display method"""
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        self.assertEqual(transaction.get_status_display(), 'Completed')
    
    def test_transaction_can_refund(self):
        """Test the can_refund method"""
        # Create a completed transaction
        completed_transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Check that it can be refunded
        self.assertTrue(completed_transaction.can_refund())
        
        # Create a pending transaction
        pending_transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Check that it cannot be refunded
        self.assertFalse(pending_transaction.can_refund())
        
        # Create a failed transaction
        failed_transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='failed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Check that it cannot be refunded
        self.assertFalse(failed_transaction.can_refund())
        
        # Create a refunded transaction
        refunded_transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='refunded',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Check that it cannot be refunded again
        self.assertFalse(refunded_transaction.can_refund())

class InvoiceModelTest(TestCase):
    """Test the Invoice model"""
    
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
        
        # Create a transaction
        self.transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
    
    def test_invoice_creation(self):
        """Test creating an invoice"""
        invoice = Invoice.objects.create(
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
        
        self.assertEqual(invoice.user, self.customer)
        self.assertEqual(invoice.booking, self.booking)
        self.assertEqual(invoice.transaction, self.transaction)
        self.assertEqual(invoice.amount, Decimal('100.00'))
        self.assertEqual(invoice.status, 'paid')
    
    def test_invoice_str(self):
        """Test the string representation of an invoice"""
        invoice = Invoice.objects.create(
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
        
        self.assertEqual(str(invoice), f'Invoice {invoice.invoice_number} - $100.00')
    
    def test_invoice_get_status_display(self):
        """Test the get_status_display method"""
        invoice = Invoice.objects.create(
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
        
        self.assertEqual(invoice.get_status_display(), 'Paid')
    
    def test_invoice_is_overdue(self):
        """Test the is_overdue method"""
        # Create an invoice that's due tomorrow
        invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            issue_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=1)
        )
        
        # Check that it's not overdue
        self.assertFalse(invoice.is_overdue())
        
        # Create an invoice that was due yesterday
        overdue_invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            issue_date=timezone.now() - timedelta(days=7),
            due_date=timezone.now() - timedelta(days=1)
        )
        
        # Check that it's overdue
        self.assertTrue(overdue_invoice.is_overdue())
        
        # Create a paid invoice that was due yesterday
        paid_invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            transaction=self.transaction,
            amount=Decimal('100.00'),
            status='paid',
            issue_date=timezone.now() - timedelta(days=7),
            due_date=timezone.now() - timedelta(days=1),
            paid_date=timezone.now() - timedelta(days=2)
        )
        
        # Check that it's not overdue (because it's paid)
        self.assertFalse(paid_invoice.is_overdue())
    
    def test_invoice_days_until_due(self):
        """Test the days_until_due method"""
        # Create an invoice that's due in 7 days
        invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            issue_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7)
        )
        
        # Check that it returns 7
        self.assertEqual(invoice.days_until_due(), 7)
        
        # Create an invoice that was due 7 days ago
        overdue_invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='pending',
            issue_date=timezone.now() - timedelta(days=14),
            due_date=timezone.now() - timedelta(days=7)
        )
        
        # Check that it returns -7
        self.assertEqual(overdue_invoice.days_until_due(), -7)
