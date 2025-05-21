from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from decimal import Decimal

from venues_app.models import Venue, Service, Category
from .models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage
from .utils import get_applicable_discounts, get_best_discount, record_discount_usage

User = get_user_model()


class DiscountModelTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            is_active=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.user,
            approval_status='approved'
        )

        # Create a service
        self.service = Service.objects.create(
            title='Test Service',
            venue=self.venue,
            price=Decimal('100.00'),
            duration=60,
            is_active=True
        )

        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            is_active=True
        )

        # Set dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)

    def test_venue_discount_creation(self):
        """Test creating a venue discount"""
        discount = VenueDiscount.objects.create(
            name='Test Venue Discount',
            description='Test description',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user,
            is_approved=True
        )

        self.assertEqual(discount.name, 'Test Venue Discount')
        self.assertEqual(discount.discount_type, 'percentage')
        self.assertEqual(discount.discount_value, Decimal('20.00'))
        self.assertEqual(discount.venue, self.venue)
        self.assertTrue(discount.is_active())
        self.assertEqual(discount.get_status(), 'active')

    def test_service_discount_creation(self):
        """Test creating a service discount"""
        discount = ServiceDiscount.objects.create(
            name='Test Service Discount',
            description='Test description',
            discount_type='fixed_amount',
            discount_value=Decimal('15.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            service=self.service,
            created_by=self.user,
            is_approved=True
        )

        self.assertEqual(discount.name, 'Test Service Discount')
        self.assertEqual(discount.discount_type, 'fixed_amount')
        self.assertEqual(discount.discount_value, Decimal('15.00'))
        self.assertEqual(discount.service, self.service)
        self.assertTrue(discount.is_active())
        self.assertEqual(discount.get_status(), 'active')

    def test_platform_discount_creation(self):
        """Test creating a platform discount"""
        discount = PlatformDiscount.objects.create(
            name='Test Platform Discount',
            description='Test description',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            category=self.category,
            created_by=self.user,
            is_featured=True
        )

        self.assertEqual(discount.name, 'Test Platform Discount')
        self.assertEqual(discount.discount_type, 'percentage')
        self.assertEqual(discount.discount_value, Decimal('10.00'))
        self.assertEqual(discount.category, self.category)
        self.assertTrue(discount.is_active())
        self.assertEqual(discount.get_status(), 'active')
        self.assertTrue(discount.is_featured)

    def test_discount_status(self):
        """Test discount status based on dates"""
        # Active discount
        active_discount = VenueDiscount.objects.create(
            name='Active Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.yesterday,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user
        )

        # Scheduled discount
        scheduled_discount = VenueDiscount.objects.create(
            name='Scheduled Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.tomorrow,
            end_date=self.tomorrow + timedelta(days=1),
            venue=self.venue,
            created_by=self.user
        )

        # Expired discount
        expired_discount = VenueDiscount.objects.create(
            name='Expired Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.yesterday - timedelta(days=1),
            end_date=self.yesterday,
            venue=self.venue,
            created_by=self.user
        )

        self.assertEqual(active_discount.get_status(), 'active')
        self.assertEqual(scheduled_discount.get_status(), 'scheduled')
        self.assertEqual(expired_discount.get_status(), 'expired')

    def test_discount_calculation(self):
        """Test discount calculation"""
        # Percentage discount
        percentage_discount = VenueDiscount.objects.create(
            name='Percentage Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user
        )

        # Fixed amount discount
        fixed_discount = VenueDiscount.objects.create(
            name='Fixed Discount',
            discount_type='fixed_amount',
            discount_value=Decimal('15.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user
        )

        # Test percentage discount calculation
        original_price = Decimal('100.00')
        discount_amount = percentage_discount.calculate_discount(original_price)
        discounted_price = percentage_discount.calculate_discounted_price(original_price)

        self.assertEqual(discount_amount, Decimal('20.00'))
        self.assertEqual(discounted_price, Decimal('80.00'))

        # Test fixed amount discount calculation
        discount_amount = fixed_discount.calculate_discount(original_price)
        discounted_price = fixed_discount.calculate_discounted_price(original_price)

        self.assertEqual(discount_amount, Decimal('15.00'))
        self.assertEqual(discounted_price, Decimal('85.00'))


class DiscountUtilsTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            is_active=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.user,
            approval_status='approved'
        )

        # Create a service
        self.service = Service.objects.create(
            title='Test Service',
            venue=self.venue,
            price=Decimal('100.00'),
            duration=60,
            is_active=True
        )

        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            is_active=True
        )

        # Set dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)

        # Create discounts
        self.venue_discount = VenueDiscount.objects.create(
            name='Venue Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user,
            is_approved=True
        )

        self.service_discount = ServiceDiscount.objects.create(
            name='Service Discount',
            discount_type='percentage',
            discount_value=Decimal('25.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            service=self.service,
            created_by=self.user,
            is_approved=True
        )

        self.platform_discount = PlatformDiscount.objects.create(
            name='Platform Discount',
            discount_type='percentage',
            discount_value=Decimal('15.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            created_by=self.user,
            is_featured=True
        )

    def test_get_applicable_discounts(self):
        """Test getting applicable discounts for a service"""
        discounts = get_applicable_discounts(self.service)

        # Should return 3 discounts
        self.assertEqual(len(discounts), 3)

        # Should be sorted by final price (lowest first)
        self.assertEqual(discounts[0][0], self.service_discount)  # 25% off = $75
        self.assertEqual(discounts[1][0], self.venue_discount)    # 20% off = $80
        self.assertEqual(discounts[2][0], self.platform_discount) # 15% off = $85

    def test_get_best_discount(self):
        """Test getting the best discount for a service"""
        best_discount = get_best_discount(self.service)

        # Should return the service discount (25% off)
        self.assertEqual(best_discount[0], self.service_discount)
        self.assertEqual(best_discount[1], Decimal('25.00'))
        self.assertEqual(best_discount[2], Decimal('75.00'))


class DiscountViewTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            is_active=True
        )

        # Create an admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='password123',
            is_active=True,
            is_staff=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.user,
            approval_status='approved'
        )

        # Create a service
        self.service = Service.objects.create(
            title='Test Service',
            venue=self.venue,
            price=Decimal('100.00'),
            duration=60,
            is_active=True
        )

        # Set dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)

        # Create a discount
        self.discount = VenueDiscount.objects.create(
            name='Test Discount',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=self.now,
            end_date=self.tomorrow,
            venue=self.venue,
            created_by=self.user,
            is_approved=True
        )

    def test_test_view(self):
        """Test the test view"""
        response = self.client.get(reverse('discount_app:test_view'))
        self.assertEqual(response.status_code, 200)