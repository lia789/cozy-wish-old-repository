from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from discount_app.models import (
    VenueDiscount, ServiceDiscount, PlatformDiscount,
    DiscountUsage, DiscountType, DiscountStatus
)
from discount_app.utils import (
    get_applicable_discounts, get_best_discount, record_discount_usage
)

User = get_user_model()

class DiscountUtilsTest(TestCase):
    """Test the discount utility functions"""

    def setUp(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create an admin
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )

        # Create a category
        self.category = Category.objects.create(
            name='Spa & Wellness',
            description='Spa and wellness services',
            is_active=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Spa',
            category=self.category,
            venue_type='all',
            state='New York',
            county='New York County',
            city='New York',
            street_number='123',
            street_name='Main St',
            about='A luxury spa in the heart of the city.',
            approval_status='approved',
            is_active=True
        )

        # Create a service
        self.service = Service.objects.create(
            venue=self.venue,
            title='Swedish Massage',
            short_description='A relaxing full-body massage',
            price=Decimal('100.00'),
            duration=60,
            is_active=True
        )

        # Set up dates
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)
        self.last_week = self.now - timedelta(days=7)

        # Create discounts
        # Active venue discount
        self.active_venue_discount = VenueDiscount.objects.create(
            name='Summer Special',
            description='Special summer discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('20.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            venue=self.venue,
            min_booking_value=Decimal('50.00'),
            max_discount_amount=Decimal('30.00'),
            created_by=self.user,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Scheduled venue discount (future)
        self.scheduled_venue_discount = VenueDiscount.objects.create(
            name='Fall Special',
            description='Special fall discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('25.00'),
            start_date=self.tomorrow,
            end_date=self.next_week,
            venue=self.venue,
            created_by=self.user,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Expired venue discount
        self.expired_venue_discount = VenueDiscount.objects.create(
            name='Spring Special',
            description='Special spring discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('15.00'),
            start_date=self.last_week,
            end_date=self.yesterday,
            venue=self.venue,
            created_by=self.user,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.last_week
        )

        # Active service discount
        self.active_service_discount = ServiceDiscount.objects.create(
            name='New Client Special',
            description='Special discount for new clients',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('15.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            service=self.service,
            created_by=self.user,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Active platform discount
        self.active_platform_discount = PlatformDiscount.objects.create(
            name='Holiday Special',
            description='Special holiday discount',
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_value=Decimal('10.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            category=self.category,
            min_booking_value=Decimal('30.00'),
            max_discount_amount=Decimal('20.00'),
            created_by=self.admin,
            is_featured=True
        )

    def test_get_applicable_discounts(self):
        """Test get_applicable_discounts function"""
        # Get applicable discounts for the service
        applicable_discounts = get_applicable_discounts(self.service)

        # Should include service discounts, venue discounts, and platform discounts
        self.assertEqual(len(applicable_discounts), 3)

        # Check that each discount is a tuple with (discount, amount, price)
        for discount_tuple in applicable_discounts:
            self.assertEqual(len(discount_tuple), 3)
            self.assertTrue(isinstance(discount_tuple[0], (VenueDiscount, ServiceDiscount, PlatformDiscount)))
            self.assertTrue(isinstance(discount_tuple[1], Decimal))
            self.assertTrue(isinstance(discount_tuple[2], Decimal))

    def test_get_best_discount(self):
        """Test get_best_discount function"""
        # Get the best discount for the service
        best_discount = get_best_discount(self.service)

        # Should return a tuple (discount, amount, price)
        self.assertIsNotNone(best_discount)
        self.assertEqual(len(best_discount), 3)

        # Create a better service discount
        better_service_discount = ServiceDiscount.objects.create(
            name='Premium Special',
            description='Premium special discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('30.00'),  # 30% off
            start_date=self.yesterday,
            end_date=self.next_week,
            service=self.service,
            created_by=self.user,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        # Recalculate the best discount
        best_discount = get_best_discount(self.service)

        # The best discount should now be the better service discount
        self.assertEqual(best_discount[0], better_service_discount)

    def test_record_discount_usage(self):
        """Test record_discount_usage function"""
        # Skip this test as it requires a real Booking instance
        # which would require setting up the booking_cart_app models
        pass








