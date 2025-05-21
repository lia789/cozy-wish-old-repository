from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem
from booking_cart_app.middleware import CartCleanupMiddleware

User = get_user_model()

class MiddlewareTest(TestCase):
    """Test the middleware in the booking_cart_app"""
    
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
        
        # Create an expired cart item
        self.expired_cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        # Create a non-expired cart item
        self.active_cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=2,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time().replace(hour=11),
            expires_at=timezone.now() + timedelta(hours=23)  # Not expired
        )
    
    def test_cart_cleanup_middleware(self):
        """Test the CartCleanupMiddleware"""
        # Create a request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create the middleware
        middleware = CartCleanupMiddleware(lambda r: None)
        
        # Process the request
        middleware(request)
        
        # Check that the expired cart item was deleted
        self.assertFalse(CartItem.objects.filter(id=self.expired_cart_item.id).exists())
        
        # Check that the non-expired cart item was not deleted
        self.assertTrue(CartItem.objects.filter(id=self.active_cart_item.id).exists())
