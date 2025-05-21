from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice
from payments_app.utils import (
    validate_credit_card, mask_card_number, get_last_four_digits,
    process_payment, get_transaction_history, get_provider_transaction_history,
    generate_invoice, generate_invoice_pdf
)

User = get_user_model()

class UtilsTest(TestCase):
    """Test the utility functions in the payments_app"""
    
    def setUp(self):
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
    
    def test_validate_credit_card(self):
        """Test the validate_credit_card function"""
        # Valid card numbers
        self.assertTrue(validate_credit_card('4111111111111111'))  # Visa
        self.assertTrue(validate_credit_card('5555555555554444'))  # Mastercard
        self.assertTrue(validate_credit_card('378282246310005'))   # American Express
        
        # Valid card numbers with spaces and dashes
        self.assertTrue(validate_credit_card('4111-1111-1111-1111'))
        self.assertTrue(validate_credit_card('5555 5555 5555 4444'))
        
        # Invalid card numbers
        self.assertFalse(validate_credit_card('1234567890123456'))  # Invalid checksum
        self.assertFalse(validate_credit_card('123456789012'))      # Too short
        self.assertFalse(validate_credit_card('12345678901234567890')) # Too long
        self.assertFalse(validate_credit_card('411111111111111a'))  # Contains non-digits
    
    def test_mask_card_number(self):
        """Test the mask_card_number function"""
        self.assertEqual(mask_card_number('4111111111111111'), '************1111')
        self.assertEqual(mask_card_number('5555-5555-5555-4444'), '************4444')
        self.assertEqual(mask_card_number('378282246310005'), '**********0005')
    
    def test_get_last_four_digits(self):
        """Test the get_last_four_digits function"""
        self.assertEqual(get_last_four_digits('4111111111111111'), '1111')
        self.assertEqual(get_last_four_digits('5555-5555-5555-4444'), '4444')
        self.assertEqual(get_last_four_digits('378282246310005'), '0005')
    
    def test_process_payment(self):
        """Test the process_payment function"""
        # Process a payment
        transaction = process_payment(
            user=self.customer,
            booking=self.booking,
            payment_method_type='credit_card',
            payment_method_details='Credit Card ending in 1234',
            amount=Decimal('100.00')
        )
        
        # Check that the transaction was created
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.user, self.customer)
        self.assertEqual(transaction.booking, self.booking)
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.status, 'completed')
        self.assertEqual(transaction.payment_method, 'credit_card')
        self.assertEqual(transaction.payment_method_details, 'Credit Card ending in 1234')
        
        # Check that the booking status was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')
        
        # Check that an invoice was created
        invoice = Invoice.objects.filter(booking=self.booking).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(invoice.amount, Decimal('100.00'))
        self.assertEqual(invoice.transaction, transaction)
    
    def test_get_transaction_history(self):
        """Test the get_transaction_history function"""
        # Create some transactions
        transaction1 = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        transaction2 = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('50.00'),
            status='refunded',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Get transaction history for the customer
        transactions = get_transaction_history(self.customer)
        
        # Check that both transactions are returned
        self.assertEqual(transactions.count(), 2)
        self.assertIn(transaction1, transactions)
        self.assertIn(transaction2, transactions)
        
        # Check that they are ordered by created_at (newest first)
        self.assertEqual(transactions[0], transaction2)
        self.assertEqual(transactions[1], transaction1)
    
    def test_get_provider_transaction_history(self):
        """Test the get_provider_transaction_history function"""
        # Create some transactions
        transaction1 = Transaction.objects.create(
            user=self.customer,
            booking=self.booking,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Create another booking and transaction for a different venue
        other_venue = Venue.objects.create(
            owner=User.objects.create_user(
                email='other_provider@example.com',
                password='testpass123',
                is_service_provider=True
            ),
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
        
        other_booking = Booking.objects.create(
            booking_id=uuid.uuid4(),
            user=self.customer,
            venue=other_venue,
            total_price=Decimal("150.00"),
            status='pending'
        )
        
        transaction2 = Transaction.objects.create(
            user=self.customer,
            booking=other_booking,
            amount=Decimal('150.00'),
            status='completed',
            payment_method='credit_card',
            payment_method_details='Credit Card ending in 1234'
        )
        
        # Get transaction history for the provider
        transactions = get_provider_transaction_history(self.provider)
        
        # Check that only the provider's transaction is returned
        self.assertEqual(transactions.count(), 1)
        self.assertIn(transaction1, transactions)
        self.assertNotIn(transaction2, transactions)
    
    def test_generate_invoice(self):
        """Test the generate_invoice function"""
        # Generate an invoice
        invoice = generate_invoice(self.booking)
        
        # Check that the invoice was created
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.user, self.customer)
        self.assertEqual(invoice.booking, self.booking)
        self.assertEqual(invoice.amount, Decimal('100.00'))
        self.assertEqual(invoice.status, 'pending')
        
        # Check that calling the function again returns the existing invoice
        invoice2 = generate_invoice(self.booking)
        self.assertEqual(invoice, invoice2)
    
    def test_generate_invoice_pdf(self):
        """Test the generate_invoice_pdf function"""
        # Generate an invoice
        invoice = generate_invoice(self.booking)
        
        # Generate a PDF
        pdf = generate_invoice_pdf(invoice)
        
        # Check that the PDF was created
        self.assertIsNotNone(pdf)
        self.assertTrue(hasattr(pdf, 'read'))  # Check that it's a file-like object
