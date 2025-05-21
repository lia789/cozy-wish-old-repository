from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount
from discount_app.forms import (
    VenueDiscountForm, ServiceDiscountForm, PlatformDiscountForm,
    DiscountFilterForm, DiscountApprovalForm
)

User = get_user_model()

class DiscountFormBaseTest(TestCase):
    """Base test class for discount forms"""

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

        # Set up dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)


class VenueDiscountFormTest(DiscountFormBaseTest):
    """Test the VenueDiscountForm"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Form data for venue discount
        self.form_data = {
            'name': 'Summer Special',
            'description': 'Special summer discount',
            'discount_type': 'percentage',
            'discount_value': '20.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'venue': self.venue.id,
            'min_booking_value': '50.00',
            'max_discount_amount': '30.00'
        }

    def test_venue_discount_form_valid(self):
        """Test that the form is valid with valid data"""
        form = VenueDiscountForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_venue_discount_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Remove required fields
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')
        invalid_data.pop('discount_value')

        form = VenueDiscountForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('discount_value', form.errors)

    def test_venue_discount_form_invalid_dates(self):
        """Test that the form is invalid when end_date is before start_date"""
        invalid_data = self.form_data.copy()
        invalid_data['start_date'] = self.next_week.strftime('%Y-%m-%dT%H:%M')
        invalid_data['end_date'] = self.tomorrow.strftime('%Y-%m-%dT%H:%M')

        form = VenueDiscountForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_venue_discount_form_invalid_percentage(self):
        """Test that the form is invalid when percentage is over 100"""
        invalid_data = self.form_data.copy()
        invalid_data['discount_value'] = '120.00'

        form = VenueDiscountForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('discount_value', form.errors)

    def test_venue_discount_form_save(self):
        """Test saving a form creates a venue discount with correct data"""
        form = VenueDiscountForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid())

        # Save the form without committing to the database
        discount = form.save(commit=False)
        discount.created_by = self.user
        discount.venue = self.venue  # Set the venue explicitly
        discount.save()

        # Check that the discount was created with correct data
        self.assertEqual(discount.name, 'Summer Special')
        self.assertEqual(discount.description, 'Special summer discount')
        self.assertEqual(discount.discount_type, 'percentage')
        self.assertEqual(discount.discount_value, Decimal('20.00'))
        self.assertEqual(discount.venue, self.venue)
        self.assertEqual(discount.min_booking_value, Decimal('50.00'))
        self.assertEqual(discount.max_discount_amount, Decimal('30.00'))
        self.assertEqual(discount.created_by, self.user)
        self.assertFalse(discount.is_approved)


class ServiceDiscountFormTest(DiscountFormBaseTest):
    """Test the ServiceDiscountForm"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Form data for service discount
        self.form_data = {
            'name': 'New Client Special',
            'description': 'Special discount for new clients',
            'discount_type': 'percentage',
            'discount_value': '15.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'service': self.service.id
        }

    def test_service_discount_form_valid(self):
        """Test that the form is valid with valid data"""
        form = ServiceDiscountForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_service_discount_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Remove required fields
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')
        invalid_data.pop('service')

        form = ServiceDiscountForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('service', form.errors)

    def test_service_discount_form_fixed_amount(self):
        """Test that the form is valid with fixed amount discount"""
        fixed_amount_data = self.form_data.copy()
        fixed_amount_data['discount_type'] = 'fixed_amount'
        fixed_amount_data['discount_value'] = '10.00'

        form = ServiceDiscountForm(data=fixed_amount_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_service_discount_form_save(self):
        """Test saving a form creates a service discount with correct data"""
        form = ServiceDiscountForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid())

        # Save the form without committing to the database
        discount = form.save(commit=False)
        discount.created_by = self.user
        discount.service = self.service  # Set the service explicitly
        discount.save()

        # Check that the discount was created with correct data
        self.assertEqual(discount.name, 'New Client Special')
        self.assertEqual(discount.description, 'Special discount for new clients')
        self.assertEqual(discount.discount_type, 'percentage')
        self.assertEqual(discount.discount_value, Decimal('15.00'))
        self.assertEqual(discount.service, self.service)
        self.assertEqual(discount.created_by, self.user)
        self.assertFalse(discount.is_approved)


class PlatformDiscountFormTest(DiscountFormBaseTest):
    """Test the PlatformDiscountForm"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create an admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )

        # Form data for platform discount
        self.form_data = {
            'name': 'Holiday Special',
            'description': 'Special holiday discount',
            'discount_type': 'fixed_amount',
            'discount_value': '10.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'category': self.category.id,
            'min_booking_value': '30.00',
            'max_discount_amount': '20.00',
            'is_featured': True
        }

    def test_platform_discount_form_valid(self):
        """Test that the form is valid with valid data"""
        form = PlatformDiscountForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_platform_discount_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Remove required fields
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')
        invalid_data.pop('discount_value')

        form = PlatformDiscountForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('discount_value', form.errors)

    def test_platform_discount_form_optional_category(self):
        """Test that the form is valid without a category (all categories)"""
        optional_data = self.form_data.copy()
        optional_data.pop('category')

        form = PlatformDiscountForm(data=optional_data)
        self.assertTrue(form.is_valid())

    def test_platform_discount_form_save(self):
        """Test saving a form creates a platform discount with correct data"""
        form = PlatformDiscountForm(data=self.form_data)
        self.assertTrue(form.is_valid())

        # Save the form without committing to the database
        discount = form.save(commit=False)
        discount.created_by = self.admin
        discount.save()

        # Check that the discount was created with correct data
        self.assertEqual(discount.name, 'Holiday Special')
        self.assertEqual(discount.description, 'Special holiday discount')
        self.assertEqual(discount.discount_type, 'fixed_amount')
        self.assertEqual(discount.discount_value, Decimal('10.00'))
        self.assertEqual(discount.category, self.category)
        self.assertEqual(discount.min_booking_value, Decimal('30.00'))
        self.assertEqual(discount.max_discount_amount, Decimal('20.00'))
        self.assertEqual(discount.created_by, self.admin)
        self.assertTrue(discount.is_featured)


class DiscountFilterFormTest(TestCase):
    """Test the DiscountFilterForm"""

    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'search': 'summer',
            'status': 'active',
            'discount_type': 'percentage',
            'min_value': '10.00',
            'max_value': '50.00'
        }

    def test_discount_filter_form_valid(self):
        """Test that the form is valid with valid data"""
        form = DiscountFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_discount_filter_form_empty(self):
        """Test that the form is valid with empty data (all filters optional)"""
        form = DiscountFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_discount_filter_form_partial(self):
        """Test that the form is valid with partial data"""
        partial_data = {
            'search': 'summer',
            'status': 'active'
        }
        form = DiscountFilterForm(data=partial_data)
        self.assertTrue(form.is_valid())


class DiscountApprovalFormTest(TestCase):
    """Test the DiscountApprovalForm"""

    def setUp(self):
        """Set up test data"""
        self.approve_data = {
            'is_approved': 'True',
            'rejection_reason': ''
        }

        self.reject_data = {
            'is_approved': 'False',
            'rejection_reason': 'Rejected due to policy violation'
        }

    def test_discount_approval_form_approve_valid(self):
        """Test that the form is valid with approve decision"""
        form = DiscountApprovalForm(data=self.approve_data)
        self.assertTrue(form.is_valid())

    def test_discount_approval_form_reject_valid(self):
        """Test that the form is valid with reject decision"""
        form = DiscountApprovalForm(data=self.reject_data)
        self.assertTrue(form.is_valid())

    def test_discount_approval_form_missing_decision(self):
        """Test that the form is invalid without a decision"""
        invalid_data = self.approve_data.copy()
        invalid_data.pop('is_approved')

        form = DiscountApprovalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('is_approved', form.errors)

    def test_discount_approval_form_invalid_decision(self):
        """Test that the form is invalid with an invalid decision"""
        invalid_data = self.approve_data.copy()
        invalid_data['is_approved'] = 'invalid'

        form = DiscountApprovalForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('is_approved', form.errors)
