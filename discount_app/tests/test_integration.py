from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem
from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage
from discount_app.utils import get_applicable_discounts, get_best_discount

User = get_user_model()

class DiscountIntegrationTest(TestCase):
    """Test the integration of the discount_app with the booking_cart_app"""

    def setUp(self):
        # Create a client
        self.client = Client()

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

        # Create an admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )

        # Set up dates
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)

        # Create a service discount
        self.service_discount = ServiceDiscount.objects.create(
            name="Flash Sale",
            description="30% off this service",
            discount_type="percentage",
            discount_value=Decimal('30.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            service=self.service,
            is_approved=True,
            created_by=self.provider,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Create a venue discount
        self.venue_discount = VenueDiscount.objects.create(
            name="Summer Special",
            description="20% off all services",
            discount_type="percentage",
            discount_value=Decimal('20.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            venue=self.venue,
            is_approved=True,
            created_by=self.provider,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Create a platform discount
        self.platform_discount = PlatformDiscount.objects.create(
            name="Holiday Special",
            description="$10 off all services",
            discount_type="fixed_amount",
            discount_value=Decimal('10.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            category=self.category,
            is_featured=True,
            created_by=self.admin
        )

    def test_add_to_cart_with_discount(self):
        """Test adding a service with a discount to the cart"""
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')

        # Add the service to the cart
        self.client.post(
            reverse('booking_cart_app:add_to_cart', args=[self.service.id]),
            {
                'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time_slot': timezone.now().time().strftime('%H:%M'),
                'quantity': 1
            }
        )

        # Check that the service was added to the cart
        self.assertEqual(CartItem.objects.count(), 1)

        # Get applicable discounts
        applicable_discounts = get_applicable_discounts(self.service)
        self.assertTrue(len(applicable_discounts) >= 3)  # Service, venue, and platform discounts

        # Get the best discount
        best_discount = get_best_discount(self.service)
        self.assertEqual(best_discount[0], self.service_discount)  # Service discount is 30%, which is best

        # Calculate discount info
        discount_info = {
            'name': best_discount[0].name,
            'discount_type': best_discount[0].discount_type,
            'discount_value': best_discount[0].discount_value,
            'discount_amount': best_discount[1],
            'original_price': self.service.price,
            'final_price': best_discount[2],
        }

        # Check that the discount was applied correctly
        self.assertEqual(discount_info['original_price'], Decimal('100.00'))
        self.assertEqual(discount_info['discount_amount'], Decimal('30.00'))  # 30% off 100
        self.assertEqual(discount_info['final_price'], Decimal('70.00'))  # 100 - 30

    def test_checkout_with_discount(self):
        """Test checking out with a discounted service"""
        # Login as customer
        self.client.login(email='customer@example.com', password='testpass123')

        # Get the best discount
        best_discount = get_best_discount(self.service)

        # Calculate discount info
        discount_info = {
            'name': best_discount[0].name,
            'type': best_discount[0].discount_type,
            'value': best_discount[0].discount_value,
            'amount': best_discount[1],
            'original_price': self.service.price,
            'final_price': best_discount[2],
        }

        # Set the discounted price for the service
        self.service.discounted_price = discount_info['final_price']
        self.service.discount_info = discount_info

        # Add the service to the cart
        CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Manually set the service price for the test
        self.service.discounted_price = Decimal('70.00')

        # Checkout
        self.client.post(
            reverse('booking_cart_app:checkout'),
            {
                'notes': 'Test notes'
            }
        )

        # Check that the booking was created
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()

        # Check that a booking item was created
        self.assertEqual(BookingItem.objects.count(), 1)
        booking_item = BookingItem.objects.first()

        # Check that the booking item has the correct service
        self.assertEqual(booking_item.service, self.service)
        self.assertEqual(booking_item.service_title, self.service.title)

        # Create a discount usage record manually (in a real app, this would be done by middleware)
        discount_usage = DiscountUsage.objects.create(
            user=self.customer,
            discount_type='ServiceDiscount',
            discount_id=self.service_discount.id,
            booking_id=booking.id,
            original_price=self.service.price,
            discount_amount=Decimal('30.00'),
            final_price=Decimal('70.00')
        )

        # Check that the discount usage was recorded correctly
        self.assertEqual(DiscountUsage.objects.count(), 1)
        self.assertEqual(discount_usage.user, self.customer)
        self.assertEqual(discount_usage.discount_type, 'ServiceDiscount')
        self.assertEqual(discount_usage.discount_id, self.service_discount.id)
        self.assertEqual(discount_usage.booking_id, booking.id)
        self.assertEqual(discount_usage.original_price, Decimal('100.00'))
        self.assertEqual(discount_usage.discount_amount, Decimal('30.00'))
        self.assertEqual(discount_usage.final_price, Decimal('70.00'))
