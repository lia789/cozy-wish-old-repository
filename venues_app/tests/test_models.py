from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal

from venues_app.models import (
    Category, Tag, Venue, VenueImage, OpeningHours,
    FAQ, Service, Review, TeamMember, USCity
)

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test the Category model."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa",
            is_active=True
        )

    def test_category_creation(self):
        """Test creating a category."""
        self.assertEqual(self.category.name, "Spa")
        self.assertEqual(self.category.description, "Relaxation and wellness services")
        self.assertEqual(self.category.icon_class, "fa-spa")
        self.assertTrue(self.category.is_active)
        self.assertTrue(self.category.slug)  # Slug should be auto-generated

    def test_category_str_method(self):
        """Test the string representation of a category."""
        self.assertEqual(str(self.category), "Spa")

    def test_slug_generation(self):
        """Test that slug is generated correctly."""
        self.assertEqual(self.category.slug, slugify(self.category.name))

    def test_unique_slug_constraint(self):
        """Test that slug must be unique."""
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            Category.objects.create(
                name="Spa",
                description="Another spa category",
                icon_class="fa-spa"
            )


class TagModelTest(TestCase):
    """Test the Tag model."""

    def setUp(self):
        """Set up test data."""
        self.tag = Tag.objects.create(
            name="Luxury"
        )

    def test_tag_creation(self):
        """Test creating a tag."""
        self.assertEqual(self.tag.name, "Luxury")
        self.assertTrue(self.tag.slug)  # Slug should be auto-generated

    def test_tag_str_method(self):
        """Test the string representation of a tag."""
        self.assertEqual(str(self.tag), "Luxury")

    def test_slug_generation(self):
        """Test that slug is generated correctly."""
        self.assertEqual(self.tag.slug, slugify(self.tag.name))

    def test_unique_slug_constraint(self):
        """Test that slug must be unique."""
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            Tag.objects.create(
                name="Luxury"
            )


class VenueModelTest(TestCase):
    """Test the Venue model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa"
        )
        self.venue = Venue.objects.create(
            owner=self.user,
            name="Luxury Spa",
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
        self.tag = Tag.objects.create(name="Luxury")
        self.venue.tags.add(self.tag)

    def test_venue_creation(self):
        """Test creating a venue."""
        self.assertEqual(self.venue.name, "Luxury Spa")
        self.assertEqual(self.venue.owner, self.user)
        self.assertEqual(self.venue.category, self.category)
        self.assertEqual(self.venue.venue_type, "all")
        self.assertEqual(self.venue.state, "New York")
        self.assertEqual(self.venue.city, "New York")
        self.assertEqual(self.venue.about, "A luxury spa in the heart of the city.")
        self.assertEqual(self.venue.approval_status, "approved")
        self.assertTrue(self.venue.slug)  # Slug should be auto-generated

    def test_venue_str_method(self):
        """Test the string representation of a venue."""
        self.assertEqual(str(self.venue), "Luxury Spa")

    def test_slug_generation(self):
        """Test that slug is generated correctly."""
        self.assertEqual(self.venue.slug, slugify(self.venue.name))

    def test_get_full_address(self):
        """Test the get_full_address method."""
        expected_address = "123 Main St, New York, New York"
        self.assertEqual(self.venue.get_full_address(), expected_address)

    def test_venue_tags(self):
        """Test that tags can be added to a venue."""
        self.assertEqual(self.venue.tags.count(), 1)
        self.assertEqual(self.venue.tags.first(), self.tag)


class ServiceModelTest(TestCase):
    """Test the Service model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa"
        )
        self.venue = Venue.objects.create(
            owner=self.user,
            name="Luxury Spa",
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
        self.service = Service.objects.create(
            venue=self.venue,
            title="Swedish Massage",
            short_description="A relaxing full-body massage",
            price=Decimal("99.99"),
            duration=60,
            is_active=True
        )

    def test_service_creation(self):
        """Test creating a service."""
        self.assertEqual(self.service.title, "Swedish Massage")
        self.assertEqual(self.service.venue, self.venue)
        self.assertEqual(self.service.short_description, "A relaxing full-body massage")
        self.assertEqual(self.service.price, Decimal("99.99"))
        self.assertEqual(self.service.duration, 60)
        self.assertTrue(self.service.is_active)
        self.assertTrue(self.service.slug)  # Slug should be auto-generated

    def test_service_str_method(self):
        """Test the string representation of a service."""
        self.assertEqual(str(self.service), "Swedish Massage - Luxury Spa")

    def test_slug_generation(self):
        """Test that slug is generated correctly."""
        self.assertEqual(self.service.slug, slugify(self.service.title))

    def test_discounted_price(self):
        """Test the discounted price functionality."""
        # Initially no discount
        self.assertIsNone(self.service.discounted_price)

        # Add a discount
        self.service.discounted_price = Decimal("79.99")
        self.service.save()

        # Refresh from DB
        self.service.refresh_from_db()
        self.assertEqual(self.service.discounted_price, Decimal("79.99"))

        # Test discount percentage
        expected_discount = 20  # 20% discount from 99.99 to 79.99
        self.assertEqual(self.service.get_discount_percentage(), expected_discount)


# Add more test classes for other models as needed
class OpeningHoursModelTest(TestCase):
    """Test the OpeningHours model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )
        self.venue = Venue.objects.create(
            owner=self.user,
            name="Luxury Spa",
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city.",
            approval_status="approved"
        )
        self.opening_hours = OpeningHours.objects.create(
            venue=self.venue,
            day=1,  # Monday
            open_time="09:00:00",
            close_time="17:00:00",
            is_closed=False
        )

    def test_opening_hours_creation(self):
        """Test creating opening hours."""
        self.assertEqual(self.opening_hours.venue, self.venue)
        self.assertEqual(self.opening_hours.day, 1)
        self.assertEqual(str(self.opening_hours.open_time), "09:00:00")
        self.assertEqual(str(self.opening_hours.close_time), "17:00:00")
        self.assertFalse(self.opening_hours.is_closed)

    def test_opening_hours_str_method(self):
        """Test the string representation of opening hours."""
        expected_str = f"Tuesday: 09:00 - 17:00"
        self.assertEqual(str(self.opening_hours), expected_str)

    def test_closed_day(self):
        """Test a closed day."""
        closed_hours = OpeningHours.objects.create(
            venue=self.venue,
            day=0,  # Sunday
            open_time="09:00:00",
            close_time="17:00:00",
            is_closed=True
        )
        self.assertTrue(closed_hours.is_closed)
        expected_str = f"Monday: Closed"
        self.assertEqual(str(closed_hours), expected_str)
