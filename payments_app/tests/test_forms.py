from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from booking_cart_app.models import Booking, Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice
from payments_app.forms import PaymentMethodForm, PaymentForm, RefundForm

User = get_user_model()

class PaymentMethodFormTest(TestCase):
    """Test the PaymentMethodForm"""
    
    def setUp(self):
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
    
    def test_payment_method_form_valid_data(self):
        """Test the PaymentMethodForm with valid data"""
        form_data = {
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'last_four': '1234',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'is_default': True
        }
        form = PaymentMethodForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_payment_method_form_invalid_data(self):
        """Test the PaymentMethodForm with invalid data"""
        # Missing required fields
        form_data = {
            'payment_type': '',
            'name': '',
            'last_four': '',
            'expiry_date': '',
            'is_default': True
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('payment_type', form.errors)
        self.assertIn('name', form.errors)
        
        # Invalid expiry date (in the past)
        form_data = {
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'last_four': '1234',
            'expiry_date': (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'is_default': True
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('expiry_date', form.errors)
    
    def test_payment_method_form_save(self):
        """Test saving the PaymentMethodForm"""
        form_data = {
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'last_four': '1234',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'is_default': True
        }
        form = PaymentMethodForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form
        payment_method = form.save(commit=False)
        payment_method.user = self.customer
        payment_method.save()
        
        # Check that the payment method was saved
        self.assertEqual(PaymentMethod.objects.count(), 1)
        saved_payment_method = PaymentMethod.objects.first()
        self.assertEqual(saved_payment_method.payment_type, 'credit_card')
        self.assertEqual(saved_payment_method.name, 'John Doe')
        self.assertEqual(saved_payment_method.last_four, '1234')
        self.assertTrue(saved_payment_method.is_default)
        self.assertEqual(saved_payment_method.user, self.customer)

class PaymentFormTest(TestCase):
    """Test the PaymentForm"""
    
    def setUp(self):
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
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
    
    def test_payment_form_init(self):
        """Test initializing the PaymentForm"""
        # Initialize form with user
        form = PaymentForm(user=self.customer)
        
        # Check that the saved_payment_method queryset is filtered by user
        self.assertEqual(form.fields['saved_payment_method'].queryset.count(), 1)
        self.assertEqual(form.fields['saved_payment_method'].queryset.first(), self.payment_method)
        
        # Initialize form without user
        form = PaymentForm()
        
        # Check that the saved_payment_method queryset is empty
        self.assertEqual(form.fields['saved_payment_method'].queryset.count(), 0)
    
    def test_payment_form_valid_data_new_payment_method(self):
        """Test the PaymentForm with valid data for a new payment method"""
        form_data = {
            'payment_method_choice': 'new',
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'card_number': '4111111111111111',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'cvv': '123',
            'save_payment_method': True
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertTrue(form.is_valid())
    
    def test_payment_form_valid_data_saved_payment_method(self):
        """Test the PaymentForm with valid data for a saved payment method"""
        form_data = {
            'payment_method_choice': 'saved',
            'saved_payment_method': self.payment_method.id
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertTrue(form.is_valid())
    
    def test_payment_form_invalid_data_new_payment_method(self):
        """Test the PaymentForm with invalid data for a new payment method"""
        # Missing required fields
        form_data = {
            'payment_method_choice': 'new',
            'payment_type': '',
            'name': '',
            'card_number': '',
            'expiry_date': '',
            'cvv': '',
            'save_payment_method': False
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertFalse(form.is_valid())
        
        # Invalid card number (too short)
        form_data = {
            'payment_method_choice': 'new',
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'card_number': '1234',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'cvv': '123',
            'save_payment_method': False
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertFalse(form.is_valid())
        self.assertIn('card_number', form.errors)
        
        # Invalid expiry date (in the past)
        form_data = {
            'payment_method_choice': 'new',
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'card_number': '4111111111111111',
            'expiry_date': (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'cvv': '123',
            'save_payment_method': False
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertFalse(form.is_valid())
        self.assertIn('expiry_date', form.errors)
        
        # Invalid CVV (too short)
        form_data = {
            'payment_method_choice': 'new',
            'payment_type': 'credit_card',
            'name': 'John Doe',
            'card_number': '4111111111111111',
            'expiry_date': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'cvv': '1',
            'save_payment_method': False
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertFalse(form.is_valid())
        self.assertIn('cvv', form.errors)
    
    def test_payment_form_invalid_data_saved_payment_method(self):
        """Test the PaymentForm with invalid data for a saved payment method"""
        # Missing required fields
        form_data = {
            'payment_method_choice': 'saved',
            'saved_payment_method': ''
        }
        form = PaymentForm(data=form_data, user=self.customer)
        self.assertFalse(form.is_valid())
        self.assertIn('saved_payment_method', form.errors)

class RefundFormTest(TestCase):
    """Test the RefundForm"""
    
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
    
    def test_refund_form_valid_data(self):
        """Test the RefundForm with valid data"""
        form_data = {
            'notes': 'I changed my mind'
        }
        form = RefundForm(data=form_data, instance=self.transaction)
        self.assertTrue(form.is_valid())
    
    def test_refund_form_save(self):
        """Test saving the RefundForm"""
        form_data = {
            'notes': 'I changed my mind'
        }
        form = RefundForm(data=form_data, instance=self.transaction)
        self.assertTrue(form.is_valid())
        
        # Save the form
        transaction = form.save(commit=False)
        transaction.status = 'refunded'
        transaction.save()
        
        # Check that the transaction was updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'refunded')
        self.assertEqual(self.transaction.notes, 'I changed my mind')
