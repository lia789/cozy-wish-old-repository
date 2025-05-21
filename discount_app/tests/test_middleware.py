from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.response import TemplateResponse
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem
from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount
from discount_app.middleware import DiscountMiddleware

User = get_user_model()

class DiscountMiddlewareTest(TestCase):
    """Test the DiscountMiddleware"""
    
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
            price=Decimal('100.00'),
            duration=60,
            is_active=True
        )
        
        # Create a cart item
        self.cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Create a venue discount
        self.venue_discount = VenueDiscount.objects.create(
            name="Summer Special",
            description="20% off all services",
            discount_type="percentage",
            discount_value=Decimal('20.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            venue=self.venue,
            is_approved=True,
            created_by=self.provider
        )
        
        # Create a service discount
        self.service_discount = ServiceDiscount.objects.create(
            name="Flash Sale",
            description="30% off this service",
            discount_type="percentage",
            discount_value=Decimal('30.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            service=self.service,
            is_approved=True,
            created_by=self.provider
        )
        
        # Create a platform discount
        self.platform_discount = PlatformDiscount.objects.create(
            name="Welcome Discount",
            description="10% off all services",
            discount_type="percentage",
            discount_value=Decimal('10.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            created_by=self.provider
        )
        
        # Create the middleware
        self.middleware = DiscountMiddleware(lambda request: None)
    
    def test_apply_discount_to_service(self):
        """Test that the middleware applies the best discount to a service"""
        # Create a mock request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create a mock response with a service in the context
        response = TemplateResponse(request, 'template.html', {'service': self.service})
        
        # Process the response
        processed_response = self.middleware.process_template_response(request, response)
        
        # Check that the discount was applied
        self.assertIsNotNone(self.service.discounted_price)
        self.assertEqual(self.service.discounted_price, Decimal('70.00'))  # 30% off 100
        self.assertIsNotNone(self.service.discount_info)
        self.assertEqual(self.service.discount_info['name'], "Flash Sale")
    
    def test_apply_discount_to_service_list(self):
        """Test that the middleware applies discounts to a list of services"""
        # Create a mock request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create a mock response with a list of services in the context
        response = TemplateResponse(request, 'template.html', {'services': [self.service]})
        
        # Process the response
        processed_response = self.middleware.process_template_response(request, response)
        
        # Check that the discount was applied
        self.assertIsNotNone(self.service.discounted_price)
        self.assertEqual(self.service.discounted_price, Decimal('70.00'))  # 30% off 100
        self.assertIsNotNone(self.service.discount_info)
        self.assertEqual(self.service.discount_info['name'], "Flash Sale")
    
    def test_apply_discount_to_cart_items(self):
        """Test that the middleware applies discounts to cart items"""
        # Create a mock request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create a mock response with cart items in the context
        response = TemplateResponse(request, 'template.html', {'cart_items': [self.cart_item]})
        
        # Process the response
        processed_response = self.middleware.process_template_response(request, response)
        
        # Check that the discount was applied to the service in the cart item
        self.assertIsNotNone(self.service.discounted_price)
        self.assertEqual(self.service.discounted_price, Decimal('70.00'))  # 30% off 100
        self.assertIsNotNone(self.service.discount_info)
        self.assertEqual(self.service.discount_info['name'], "Flash Sale")
    
    def test_no_discount_when_not_approved(self):
        """Test that no discount is applied when the discount is not approved"""
        # Set the discount to not approved
        self.service_discount.is_approved = False
        self.service_discount.save()
        self.venue_discount.is_approved = False
        self.venue_discount.save()
        
        # Create a mock request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create a mock response with a service in the context
        response = TemplateResponse(request, 'template.html', {'service': self.service})
        
        # Process the response
        processed_response = self.middleware.process_template_response(request, response)
        
        # Check that the platform discount was applied (it doesn't need approval)
        self.assertIsNotNone(self.service.discounted_price)
        self.assertEqual(self.service.discounted_price, Decimal('90.00'))  # 10% off 100
        self.assertIsNotNone(self.service.discount_info)
        self.assertEqual(self.service.discount_info['name'], "Welcome Discount")
    
    def test_no_discount_when_expired(self):
        """Test that no discount is applied when the discount is expired"""
        # Set all discounts to expired
        self.service_discount.end_date = timezone.now() - timedelta(days=1)
        self.service_discount.save()
        self.venue_discount.end_date = timezone.now() - timedelta(days=1)
        self.venue_discount.save()
        self.platform_discount.end_date = timezone.now() - timedelta(days=1)
        self.platform_discount.save()
        
        # Create a mock request
        request = self.factory.get('/')
        request.user = self.customer
        
        # Create a mock response with a service in the context
        response = TemplateResponse(request, 'template.html', {'service': self.service})
        
        # Process the response
        processed_response = self.middleware.process_template_response(request, response)
        
        # Check that no discount was applied
        self.assertIsNone(self.service.discounted_price)
        self.assertIsNone(self.service.discount_info)
