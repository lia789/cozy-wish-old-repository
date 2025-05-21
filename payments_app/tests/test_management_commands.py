from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid
from io import StringIO

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class GenerateTestPaymentsCommandTest(TestCase):
    """Test the generate_test_payments management command"""
    
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
        
        # Create bookings without transactions
        for i in range(5):
            Booking.objects.create(
                booking_id=uuid.uuid4(),
                user=self.customer,
                venue=self.venue,
                total_price=Decimal("100.00"),
                status='pending'
            )
    
    def test_generate_test_payments_command(self):
        """Test the generate_test_payments command"""
        # Check initial state
        self.assertEqual(Booking.objects.count(), 5)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Invoice.objects.count(), 0)
        
        # Call the command
        out = StringIO()
        call_command('generate_test_payments', count=3, stdout=out)
        
        # Check that transactions and invoices were created
        self.assertEqual(Transaction.objects.count(), 3)
        self.assertEqual(Invoice.objects.count(), 3)
        
        # Check that some bookings were updated
        self.assertEqual(Booking.objects.filter(status='confirmed').count(), 3)
        
        # Check output
        self.assertIn('Successfully generated 3 test payments', out.getvalue())
    
    def test_generate_test_payments_with_status(self):
        """Test the generate_test_payments command with a specific status"""
        # Call the command with status=refunded
        out = StringIO()
        call_command('generate_test_payments', count=2, status='refunded', stdout=out)
        
        # Check that transactions and invoices were created
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Invoice.objects.count(), 2)
        
        # Check that all transactions have the specified status
        self.assertEqual(Transaction.objects.filter(status='refunded').count(), 2)
        
        # Check that bookings were updated
        self.assertEqual(Booking.objects.filter(status='cancelled').count(), 2)
        
        # Check output
        self.assertIn('Successfully generated 2 test payments', out.getvalue())
    
    def test_generate_test_payments_with_clear(self):
        """Test the generate_test_payments command with clear option"""
        # Create some existing transactions and invoices
        booking = Booking.objects.first()
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=booking,
            transaction=transaction,
            amount=Decimal('100.00'),
            status='paid',
            issue_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
            paid_date=timezone.now()
        )
        
        # Check initial state
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Invoice.objects.count(), 1)
        
        # Call the command with clear option
        out = StringIO()
        call_command('generate_test_payments', count=2, clear=True, stdout=out)
        
        # Check that old transactions and invoices were cleared
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Invoice.objects.count(), 2)
        
        # Check output
        self.assertIn('Successfully generated 2 test payments', out.getvalue())
    
    def test_generate_test_payments_with_user_email(self):
        """Test the generate_test_payments command with user_email option"""
        # Create another user with bookings
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_customer=True
        )
        for i in range(3):
            Booking.objects.create(
                booking_id=uuid.uuid4(),
                user=other_user,
                venue=self.venue,
                total_price=Decimal("100.00"),
                status='pending'
            )
        
        # Call the command with user_email option
        out = StringIO()
        call_command('generate_test_payments', count=2, user_email='other@example.com', stdout=out)
        
        # Check that transactions were created only for the specified user
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Transaction.objects.filter(user=other_user).count(), 2)
        self.assertEqual(Transaction.objects.filter(user=self.customer).count(), 0)
        
        # Check output
        self.assertIn('Successfully generated 2 test payments', out.getvalue())

class CleanOldTransactionsCommandTest(TestCase):
    """Test the clean_old_transactions management command"""
    
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
        
        # Create old transactions (100 days ago)
        old_date = timezone.now() - timedelta(days=100)
        for i in range(3):
            transaction = Transaction.objects.create(
                user=self.customer,
                booking=self.booking,
                amount=Decimal('100.00'),
                status='completed',
                payment_method='credit_card',
                payment_method_details='Credit Card ending in 1234',
                notes='Test transaction'
            )
            # Update created_at directly in the database
            Transaction.objects.filter(id=transaction.id).update(created_at=old_date)
            
            # Create invoice for the transaction
            invoice = Invoice.objects.create(
                invoice_number=uuid.uuid4(),
                user=self.customer,
                booking=self.booking,
                transaction=transaction,
                amount=Decimal('100.00'),
                status='paid',
                issue_date=old_date,
                due_date=old_date + timedelta(days=7),
                paid_date=old_date
            )
        
        # Create recent transactions (10 days ago)
        recent_date = timezone.now() - timedelta(days=10)
        for i in range(2):
            transaction = Transaction.objects.create(
                user=self.customer,
                booking=self.booking,
                amount=Decimal('100.00'),
                status='completed',
                payment_method='credit_card',
                payment_method_details='Credit Card ending in 1234'
            )
            # Update created_at directly in the database
            Transaction.objects.filter(id=transaction.id).update(created_at=recent_date)
            
            # Create invoice for the transaction
            invoice = Invoice.objects.create(
                invoice_number=uuid.uuid4(),
                user=self.customer,
                booking=self.booking,
                transaction=transaction,
                amount=Decimal('100.00'),
                status='paid',
                issue_date=recent_date,
                due_date=recent_date + timedelta(days=7),
                paid_date=recent_date
            )
    
    def test_clean_old_transactions_command(self):
        """Test the clean_old_transactions command"""
        # Check initial state
        self.assertEqual(Transaction.objects.count(), 5)
        self.assertEqual(Invoice.objects.count(), 5)
        
        # Call the command
        out = StringIO()
        call_command('clean_old_transactions', days=30, stdout=out)
        
        # Check that old transactions and invoices were deleted
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Invoice.objects.count(), 2)
        
        # Check output
        self.assertIn('Successfully deleted 3 transactions and 3 invoices', out.getvalue())
    
    def test_clean_old_transactions_with_test_only(self):
        """Test the clean_old_transactions command with test_only option"""
        # Create an old transaction without 'Test' in notes
        old_date = timezone.now() - timedelta(days=100)
        transaction = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234',
            notes='Regular transaction'
        )
        # Update created_at directly in the database
        Transaction.objects.filter(id=transaction.id).update(created_at=old_date)
        
        # Create invoice for the transaction
        invoice = Invoice.objects.create(
            invoice_number=uuid.uuid4(),
            user=self.customer,
            booking=self.booking,
            transaction=transaction,
            amount=Decimal('100.00'),
            status='paid',
            issue_date=old_date,
            due_date=old_date + timedelta(days=7),
            paid_date=old_date
        )
        
        # Check initial state
        self.assertEqual(Transaction.objects.count(), 6)
        self.assertEqual(Invoice.objects.count(), 6)
        
        # Call the command with test_only option
        out = StringIO()
        call_command('clean_old_transactions', days=30, test_only=True, stdout=out)
        
        # Check that only test transactions were deleted
        self.assertEqual(Transaction.objects.count(), 3)
        self.assertEqual(Invoice.objects.count(), 3)
        self.assertEqual(Transaction.objects.filter(notes='Test transaction').count(), 0)
        self.assertEqual(Transaction.objects.filter(notes='Regular transaction').count(), 1)
        
        # Check output
        self.assertIn('Successfully deleted 3 transactions and 3 invoices', out.getvalue())
    
    def test_clean_old_transactions_with_dry_run(self):
        """Test the clean_old_transactions command with dry_run option"""
        # Check initial state
        self.assertEqual(Transaction.objects.count(), 5)
        self.assertEqual(Invoice.objects.count(), 5)
        
        # Call the command with dry_run option
        out = StringIO()
        call_command('clean_old_transactions', days=30, dry_run=True, stdout=out)
        
        # Check that no transactions or invoices were deleted
        self.assertEqual(Transaction.objects.count(), 5)
        self.assertEqual(Invoice.objects.count(), 5)
        
        # Check output
        self.assertIn('Would delete 3 transactions and 3 invoices', out.getvalue())
