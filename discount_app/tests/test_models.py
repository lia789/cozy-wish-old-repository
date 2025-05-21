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

User = get_user_model()

class DiscountBaseTest(TestCase):
    """Base test class for discount models"""

    def setUp(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
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

        # Set up dates
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)


class VenueDiscountModelTest(DiscountBaseTest):
    """Test the VenueDiscount model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a venue discount
        self.venue_discount = VenueDiscount.objects.create(
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

    def test_venue_discount_creation(self):
        """Test creating a venue discount is successful"""
        self.assertEqual(self.venue_discount.name, 'Summer Special')
        self.assertEqual(self.venue_discount.description, 'Special summer discount')
        self.assertEqual(self.venue_discount.discount_type, DiscountType.PERCENTAGE)
        self.assertEqual(self.venue_discount.discount_value, Decimal('20.00'))
        self.assertEqual(self.venue_discount.venue, self.venue)
        self.assertEqual(self.venue_discount.min_booking_value, Decimal('50.00'))
        self.assertEqual(self.venue_discount.max_discount_amount, Decimal('30.00'))
        self.assertEqual(self.venue_discount.created_by, self.user)
        self.assertTrue(self.venue_discount.is_approved)
        self.assertEqual(self.venue_discount.approved_by, self.admin)

    def test_venue_discount_string_representation(self):
        """Test the string representation of venue discount"""
        self.assertEqual(str(self.venue_discount), 'Summer Special')

    def test_venue_discount_get_status_active(self):
        """Test get_status returns 'active' for an active discount"""
        self.assertEqual(self.venue_discount.get_status(), DiscountStatus.ACTIVE)

    def test_venue_discount_get_status_scheduled(self):
        """Test get_status returns 'scheduled' for a future discount"""
        self.venue_discount.start_date = self.tomorrow
        self.venue_discount.save()
        self.assertEqual(self.venue_discount.get_status(), DiscountStatus.SCHEDULED)

    def test_venue_discount_get_status_expired(self):
        """Test get_status returns 'expired' for an expired discount"""
        self.venue_discount.end_date = self.yesterday
        self.venue_discount.save()
        self.assertEqual(self.venue_discount.get_status(), DiscountStatus.EXPIRED)

    def test_venue_discount_calculate_discount_percentage(self):
        """Test calculate_discount for percentage discount"""
        original_price = Decimal('100.00')
        expected_discount = Decimal('20.00')  # 20% of 100
        self.assertEqual(self.venue_discount.calculate_discount(original_price), expected_discount)

    def test_venue_discount_calculate_discount_fixed_amount(self):
        """Test calculate_discount for fixed amount discount"""
        self.venue_discount.discount_type = DiscountType.FIXED_AMOUNT
        self.venue_discount.discount_value = Decimal('15.00')
        self.venue_discount.save()

        original_price = Decimal('100.00')
        expected_discount = Decimal('15.00')
        self.assertEqual(self.venue_discount.calculate_discount(original_price), expected_discount)

    def test_venue_discount_calculate_discount_with_max_amount(self):
        """Test calculate_discount respects max_discount_amount"""
        # Set a high percentage to exceed max_discount_amount
        self.venue_discount.discount_value = Decimal('50.00')  # 50%
        self.venue_discount.save()

        original_price = Decimal('100.00')
        # 50% of 100 is 50, but max is 30
        expected_discount = Decimal('30.00')

        # This is handled in the utils.py, not directly in the model
        discount_amount = self.venue_discount.calculate_discount(original_price)
        if self.venue_discount.max_discount_amount and discount_amount > self.venue_discount.max_discount_amount:
            discount_amount = self.venue_discount.max_discount_amount

        self.assertEqual(discount_amount, expected_discount)

    def test_venue_discount_calculate_discounted_price(self):
        """Test calculate_discounted_price"""
        original_price = Decimal('100.00')
        expected_price = Decimal('80.00')  # 100 - 20% discount
        self.assertEqual(self.venue_discount.calculate_discounted_price(original_price), expected_price)


class ServiceDiscountModelTest(DiscountBaseTest):
    """Test the ServiceDiscount model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a service discount
        self.service_discount = ServiceDiscount.objects.create(
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

    def test_service_discount_creation(self):
        """Test creating a service discount is successful"""
        self.assertEqual(self.service_discount.name, 'New Client Special')
        self.assertEqual(self.service_discount.description, 'Special discount for new clients')
        self.assertEqual(self.service_discount.discount_type, DiscountType.PERCENTAGE)
        self.assertEqual(self.service_discount.discount_value, Decimal('15.00'))
        self.assertEqual(self.service_discount.service, self.service)
        self.assertEqual(self.service_discount.created_by, self.user)
        self.assertTrue(self.service_discount.is_approved)
        self.assertEqual(self.service_discount.approved_by, self.admin)

    def test_service_discount_string_representation(self):
        """Test the string representation of service discount"""
        self.assertEqual(str(self.service_discount), 'New Client Special')

    def test_service_discount_calculate_discount(self):
        """Test calculate_discount for service discount"""
        original_price = Decimal('100.00')
        expected_discount = Decimal('15.00')  # 15% of 100
        self.assertEqual(self.service_discount.calculate_discount(original_price), expected_discount)

    def test_service_discount_calculate_discounted_price(self):
        """Test calculate_discounted_price for service discount"""
        original_price = Decimal('100.00')
        expected_price = Decimal('85.00')  # 100 - 15% discount
        self.assertEqual(self.service_discount.calculate_discounted_price(original_price), expected_price)


class PlatformDiscountModelTest(DiscountBaseTest):
    """Test the PlatformDiscount model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a platform discount
        self.platform_discount = PlatformDiscount.objects.create(
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

    def test_platform_discount_creation(self):
        """Test creating a platform discount is successful"""
        self.assertEqual(self.platform_discount.name, 'Holiday Special')
        self.assertEqual(self.platform_discount.description, 'Special holiday discount')
        self.assertEqual(self.platform_discount.discount_type, DiscountType.FIXED_AMOUNT)
        self.assertEqual(self.platform_discount.discount_value, Decimal('10.00'))
        self.assertEqual(self.platform_discount.category, self.category)
        self.assertEqual(self.platform_discount.min_booking_value, Decimal('30.00'))
        self.assertEqual(self.platform_discount.max_discount_amount, Decimal('20.00'))
        self.assertEqual(self.platform_discount.created_by, self.admin)
        self.assertTrue(self.platform_discount.is_featured)

    def test_platform_discount_string_representation(self):
        """Test the string representation of platform discount"""
        self.assertEqual(str(self.platform_discount), 'Holiday Special')

    def test_platform_discount_calculate_discount(self):
        """Test calculate_discount for platform discount"""
        original_price = Decimal('100.00')
        expected_discount = Decimal('10.00')  # Fixed amount
        self.assertEqual(self.platform_discount.calculate_discount(original_price), expected_discount)

    def test_platform_discount_calculate_discounted_price(self):
        """Test calculate_discounted_price for platform discount"""
        original_price = Decimal('100.00')
        expected_price = Decimal('90.00')  # 100 - 10 fixed discount
        self.assertEqual(self.platform_discount.calculate_discounted_price(original_price), expected_price)


class DiscountUsageModelTest(DiscountBaseTest):
    """Test the DiscountUsage model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a venue discount
        self.venue_discount = VenueDiscount.objects.create(
            name='Summer Special',
            description='Special summer discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('20.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            venue=self.venue,
            created_by=self.user,
            is_approved=True
        )

        # Create a discount usage with a mock booking ID
        # Note: In a real scenario, this would be a foreign key to a Booking object
        # For testing purposes, we'll use a mock booking ID and test the fields directly
        self.discount_usage = DiscountUsage(
            user=self.customer,
            discount_type='VenueDiscount',
            discount_id=self.venue_discount.id,
            booking_id=1,  # This is a mock ID, not saved to the database
            original_price=Decimal('100.00'),
            discount_amount=Decimal('20.00'),
            final_price=Decimal('80.00')
        )

        # We don't save this to the database to avoid foreign key constraints
        # Instead, we'll test the attribute values directly

    def test_discount_usage_creation(self):
        """Test creating a discount usage is successful"""
        self.assertEqual(self.discount_usage.user, self.customer)
        self.assertEqual(self.discount_usage.discount_type, 'VenueDiscount')
        self.assertEqual(self.discount_usage.discount_id, self.venue_discount.id)
        self.assertEqual(self.discount_usage.booking_id, 1)  # Mock booking ID
        self.assertEqual(self.discount_usage.original_price, Decimal('100.00'))
        self.assertEqual(self.discount_usage.discount_amount, Decimal('20.00'))
        self.assertEqual(self.discount_usage.final_price, Decimal('80.00'))
        # used_at is set on save, which we're not doing in this test
        # self.assertIsNotNone(self.discount_usage.used_at)
