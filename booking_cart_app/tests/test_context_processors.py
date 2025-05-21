from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem
from booking_cart_app.context_processors import cart_count

User = get_user_model()

class ContextProcessorsTest(TestCase):
    """Test the context processors in the booking_cart_app"""
    
    def setUp(self):
        # Create a request factory
        self.factory = RequestFactory()
        
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
        
        # Create a service
        self.service = Service.objects.create(
            venue=self.venue,
            title="Swedish Massage",
            short_description="A relaxing full-body massage.",
            price=Decimal("100.00"),
            duration=60,
            is_active=True
        )
        
        # Create cart items
        self.cart_item1 = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.cart_item2 = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=2,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time().replace(hour=11),
            expires_at=timezone.now() + timedelta(hours=24)
        )
    
    def test_cart_count_context_processor(self):
        """Test the cart_count context processor"""
        # Create a request for a customer
        request = self.factory.get('/')
        request.user = self.customer
        
        # Get the context
        context = cart_count(request)
        
        # Check the context
        self.assertIn('cart_count', context)
        self.assertEqual(context['cart_count'], 2)  # 2 cart items
        
        # Create a request for a provider
        request = self.factory.get('/')
        request.user = self.provider
        
        # Get the context
        context = cart_count(request)
        
        # Check the context
        self.assertIn('cart_count', context)
        self.assertEqual(context['cart_count'], 0)  # No cart items
        
        # Create a request for an anonymous user
        request = self.factory.get('/')
        request.user = None
        
        # Get the context
        context = cart_count(request)
        
        # Check the context
        self.assertIn('cart_count', context)
        self.assertEqual(context['cart_count'], 0)  # No cart items
