from django.test import TestCase
from django.template import Context, Template
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from django.contrib.auth import get_user_model
from booking_cart_app.models import Booking
from venues_app.models import Venue, Category
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class PaymentTemplateTagsTest(TestCase):
    """Test the template tags in the payments_app"""
    
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
    
    def test_payment_status_badge_tag(self):
        """Test the payment_status_badge template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% payment_status_badge transaction.status %}"
        )
        
        # Render the template with the transaction
        context = Context({'transaction': self.transaction})
        rendered = template.render(context)
        
        # Check that the badge is rendered correctly
        self.assertIn('badge', rendered)
        self.assertIn('Completed', rendered)
        self.assertIn('bg-success', rendered)
    
    def test_invoice_status_badge_tag(self):
        """Test the invoice_status_badge template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% invoice_status_badge invoice.status %}"
        )
        
        # Render the template with the invoice
        context = Context({'invoice': self.invoice})
        rendered = template.render(context)
        
        # Check that the badge is rendered correctly
        self.assertIn('badge', rendered)
        self.assertIn('Paid', rendered)
        self.assertIn('bg-success', rendered)
    
    def test_payment_method_icon_tag(self):
        """Test the payment_method_icon template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% payment_method_icon transaction.payment_method %}"
        )
        
        # Render the template with the transaction
        context = Context({'transaction': self.transaction})
        rendered = template.render(context)
        
        # Check that the icon is rendered correctly
        self.assertIn('fa', rendered)
        self.assertIn('credit-card', rendered)
    
    def test_format_card_number_tag(self):
        """Test the format_card_number template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% format_card_number '1234567890123456' %}"
        )
        
        # Render the template
        rendered = template.render(Context())
        
        # Check that the card number is formatted correctly
        self.assertEqual(rendered, "•••• •••• •••• 3456")
    
    def test_format_expiry_date_tag(self):
        """Test the format_expiry_date template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% format_expiry_date payment_method.expiry_date %}"
        )
        
        # Create a payment method
        payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='credit_card',
            name='John Doe',
            last_four='1234',
            expiry_date=timezone.datetime(2025, 12, 31).date(),
            is_default=True
        )
        
        # Render the template with the payment method
        context = Context({'payment_method': payment_method})
        rendered = template.render(context)
        
        # Check that the expiry date is formatted correctly
        self.assertEqual(rendered, "12/25")
    
    def test_currency_format_tag(self):
        """Test the currency_format template tag"""
        # Load the template tag
        template = Template(
            "{% load payment_tags %}"
            "{% currency_format transaction.amount %}"
        )
        
        # Render the template with the transaction
        context = Context({'transaction': self.transaction})
        rendered = template.render(context)
        
        # Check that the amount is formatted correctly
        self.assertEqual(rendered, "$100.00")
