from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

from venues_app.models import (
    Category, Venue, Service, VenueImage, OpeningHours, FAQ, TeamMember
)
from venues_app.forms import (
    VenueSearchForm, VenueFilterForm, ReviewForm, VenueForm, ServiceForm,
    VenueImageForm, OpeningHoursForm, FAQForm, TeamMemberForm
)

User = get_user_model()


class VenueSearchFormTest(TestCase):
    """Test the VenueSearchForm."""

    def test_search_form_valid(self):
        """Test that the form is valid with valid data."""
        form_data = {
            'search_query': 'spa',
            'location': 'New York',
        }
        form = VenueSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_empty(self):
        """Test that the form is valid with empty data."""
        form_data = {}
        form = VenueSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class VenueFilterFormTest(TestCase):
    """Test the VenueFilterForm."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa"
        )

    def test_filter_form_valid(self):
        """Test that the form is valid with valid data."""
        form_data = {
            'category': self.category.id,
            'venue_type': 'all',
            'rating': '4',
        }
        form = VenueFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_filter_form_empty(self):
        """Test that the form is valid with empty data."""
        form_data = {}
        form = VenueFilterForm(data=form_data)
        self.assertTrue(form.is_valid())


class ReviewFormTest(TestCase):
    """Test the ReviewForm."""

    def test_review_form_valid(self):
        """Test that the form is valid with valid data."""
        form_data = {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.',
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        """Test that the form is invalid with invalid rating."""
        form_data = {
            'rating': 6,  # Invalid rating (should be 1-5)
            'comment': 'Great experience!',
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_form_missing_comment(self):
        """Test that the form is invalid without a comment."""
        form_data = {
            'rating': 4,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)


class VenueFormTest(TestCase):
    """Test the VenueForm."""

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
        self.form_data = {
            'name': 'Luxury Spa',
            'category': self.category.id,
            'venue_type': 'all',
            'state': 'New York',
            'county': 'New York County',
            'city': 'New York',
            'street_number': '123',
            'street_name': 'Main St',
            'about': 'A luxury spa in the heart of the city.',
        }

    def test_venue_form_valid(self):
        """Test that the form is valid with valid data."""
        form = VenueForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_venue_form_missing_required_fields(self):
        """Test that the form is invalid without required fields."""
        # Remove required fields
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')
        invalid_data.pop('city')

        form = VenueForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('city', form.errors)

    def test_venue_form_invalid_city(self):
        """Test that the form is invalid without a city."""
        invalid_data = self.form_data.copy()
        invalid_data.pop('city')

        form = VenueForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('city', form.errors)


class ServiceFormTest(TestCase):
    """Test the ServiceForm."""

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
        self.form_data = {
            'title': 'Swedish Massage',
            'short_description': 'A relaxing full-body massage',
            'price': '99.99',
            'duration': 60,
            'is_active': True,
        }

    def test_service_form_valid(self):
        """Test that the form is valid with valid data."""
        form = ServiceForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_service_form_missing_required_fields(self):
        """Test that the form is invalid without required fields."""
        # Remove required fields
        invalid_data = self.form_data.copy()
        invalid_data.pop('title')
        invalid_data.pop('price')

        form = ServiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('price', form.errors)

    def test_service_form_invalid_price(self):
        """Test that the form is invalid with invalid price."""
        invalid_data = self.form_data.copy()
        invalid_data['price'] = 'not-a-price'

        form = ServiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_service_form_with_discounted_price(self):
        """Test the form with a discounted price."""
        data_with_discount = self.form_data.copy()
        data_with_discount['discounted_price'] = '79.99'

        form = ServiceForm(data=data_with_discount)
        self.assertTrue(form.is_valid())


class OpeningHoursFormTest(TestCase):
    """Test the OpeningHoursForm."""

    def setUp(self):
        """Set up test data."""
        self.form_data = {
            'day': 1,  # Monday
            'open_time': '09:00:00',
            'close_time': '17:00:00',
            'is_closed': False,
        }

    def test_opening_hours_form_valid(self):
        """Test that the form is valid with valid data."""
        form = OpeningHoursForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_opening_hours_form_closed_day(self):
        """Test the form with a closed day."""
        closed_data = {
            'day': 0,  # Sunday
            'open_time': '09:00:00',
            'close_time': '17:00:00',
            'is_closed': True,
        }
        form = OpeningHoursForm(data=closed_data)
        self.assertTrue(form.is_valid())

    def test_opening_hours_form_invalid_times(self):
        """Test that the form is invalid with invalid times."""
        invalid_data = self.form_data.copy()
        invalid_data['open_time'] = '18:00:00'  # Open time after close time

        form = OpeningHoursForm(data=invalid_data)
        self.assertFalse(form.is_valid())
