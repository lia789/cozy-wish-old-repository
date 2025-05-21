from django.test import TestCase, Client
from django.urls import reverse
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

class DiscountViewBaseTest(TestCase):
    """Base test class for discount views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

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
            owner=self.provider,
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

        # Create discounts
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
            created_by=self.provider,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

        self.service_discount = ServiceDiscount.objects.create(
            name='New Client Special',
            description='Special discount for new clients',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('15.00'),
            start_date=self.yesterday,
            end_date=self.next_week,
            service=self.service,
            created_by=self.provider,
            is_approved=True,
            approved_by=self.admin,
            approved_at=self.yesterday
        )

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


class CustomerDiscountViewsTest(DiscountViewBaseTest):
    """Test the customer-facing discount views"""

    def test_featured_discounts_view(self):
        """Test the featured discounts view"""
        self.client.login(email='customer@example.com', password='testpass123')
        url = reverse('discount_app:featured_discounts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/customer/featured_discounts.html')
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')
        self.assertContains(response, 'Holiday Special')

    def test_venue_discounts_view(self):
        """Test the venue discounts view"""
        self.client.login(email='customer@example.com', password='testpass123')
        url = reverse('discount_app:venue_discounts', args=[self.venue.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/customer/venue_discounts.html')
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')

    def test_search_discounts_view(self):
        """Test the search discounts view"""
        self.client.login(email='customer@example.com', password='testpass123')
        url = reverse('discount_app:search_discounts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/customer/search_discounts.html')

        # Test with search parameters
        response = self.client.get(url, {'search': 'Special'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')
        self.assertContains(response, 'Holiday Special')

    def test_search_discounts_view_with_filters(self):
        """Test the search discounts view with filters"""
        self.client.login(email='customer@example.com', password='testpass123')
        url = reverse('discount_app:search_discounts')

        # Test with discount type filter
        response = self.client.get(url, {'discount_type': 'percentage'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')
        self.assertNotContains(response, 'Holiday Special')  # Fixed amount discount

        # Test with value range filter
        response = self.client.get(url, {'min_value': '15', 'max_value': '25'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summer Special')  # 20%
        self.assertContains(response, 'New Client Special')  # 15%
        self.assertNotContains(response, 'Holiday Special')  # $10 fixed amount


class ServiceProviderDiscountViewsTest(DiscountViewBaseTest):
    """Test the service provider discount views"""

    def test_discount_list_view(self):
        """Test the discount list view for service providers"""
        self.client.login(email='provider@example.com', password='testpass123')
        url = reverse('discount_app:service_provider_discounts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/service_provider/discount_list.html')
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')

    def test_create_venue_discount_view(self):
        """Test the create venue discount view"""
        self.client.login(email='provider@example.com', password='testpass123')
        url = reverse('discount_app:create_venue_discount')

        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/service_provider/discount_form.html')

        # Test POST request
        discount_data = {
            'name': 'Winter Special',
            'description': 'Special winter discount',
            'discount_type': 'percentage',
            'discount_value': '25.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'venue': self.venue.id,
            'min_booking_value': '50.00',
            'max_discount_amount': '30.00'
        }

        response = self.client.post(url, discount_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Check that the discount was created
        self.assertTrue(VenueDiscount.objects.filter(name='Winter Special').exists())

    def test_create_service_discount_view(self):
        """Test the create service discount view"""
        self.client.login(email='provider@example.com', password='testpass123')
        url = reverse('discount_app:create_service_discount')

        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/service_provider/discount_form.html')

        # Test POST request
        discount_data = {
            'name': 'Weekend Special',
            'description': 'Special weekend discount',
            'discount_type': 'percentage',
            'discount_value': '10.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'service': self.service.id
        }

        response = self.client.post(url, discount_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Check that the discount was created
        self.assertTrue(ServiceDiscount.objects.filter(name='Weekend Special').exists())

    def test_update_venue_discount_view(self):
        """Test the update venue discount view"""
        self.client.login(email='provider@example.com', password='testpass123')
        url = reverse('discount_app:edit_venue_discount', args=[self.venue_discount.id])

        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/service_provider/discount_form.html')

        # Test POST request
        updated_data = {
            'name': 'Updated Summer Special',
            'description': 'Updated special summer discount',
            'discount_type': 'percentage',
            'discount_value': '22.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'venue': self.venue.id,
            'min_booking_value': '55.00',
            'max_discount_amount': '35.00'
        }

        response = self.client.post(url, updated_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

        # Check that the discount was updated
        self.venue_discount.refresh_from_db()
        self.assertEqual(self.venue_discount.name, 'Updated Summer Special')
        self.assertEqual(self.venue_discount.discount_value, Decimal('22.00'))

    def test_delete_venue_discount_view(self):
        """Test the delete venue discount view"""
        self.client.login(email='provider@example.com', password='testpass123')
        url = reverse('discount_app:delete_discount', args=['venue', self.venue_discount.id])

        # Test GET request (confirmation page)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/service_provider/discount_confirm_delete.html')

        # Test POST request (actual deletion)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion

        # Check that the discount was deleted
        self.assertFalse(VenueDiscount.objects.filter(id=self.venue_discount.id).exists())


class AdminDiscountViewsTest(DiscountViewBaseTest):
    """Test the admin discount views"""

    def test_admin_discount_list_view(self):
        """Test the admin discount list view"""
        self.client.login(email='admin@example.com', password='testpass123')
        url = reverse('discount_app:admin_discount_list', args=['all'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/admin/discount_list.html')
        self.assertContains(response, 'Summer Special')
        self.assertContains(response, 'New Client Special')
        self.assertContains(response, 'Holiday Special')

    def test_admin_discount_detail_view(self):
        """Test the admin discount detail view"""
        self.client.login(email='admin@example.com', password='testpass123')

        # Test venue discount detail
        url = reverse('discount_app:admin_discount_detail', args=['venue', self.venue_discount.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/admin/discount_detail.html')
        self.assertContains(response, 'Summer Special')

        # Test service discount detail
        url = reverse('discount_app:admin_discount_detail', args=['service', self.service_discount.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Client Special')

        # Test platform discount detail
        url = reverse('discount_app:admin_discount_detail', args=['platform', self.platform_discount.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Holiday Special')

    def test_admin_create_platform_discount_view(self):
        """Test the admin create platform discount view"""
        self.client.login(email='admin@example.com', password='testpass123')
        url = reverse('discount_app:admin_create_platform_discount')

        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/admin/platform_discount_form.html')

        # Test POST request
        discount_data = {
            'name': 'New Year Special',
            'description': 'Special new year discount',
            'discount_type': 'percentage',
            'discount_value': '15.00',
            'start_date': self.tomorrow.strftime('%Y-%m-%dT%H:%M'),
            'end_date': self.next_week.strftime('%Y-%m-%dT%H:%M'),
            'category': self.category.id,
            'min_booking_value': '40.00',
            'max_discount_amount': '25.00',
            'is_featured': True
        }

        response = self.client.post(url, discount_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Check that the discount was created
        self.assertTrue(PlatformDiscount.objects.filter(name='New Year Special').exists())

    def test_admin_approve_discount_view(self):
        """Test the admin approve discount view"""
        # Create an unapproved discount
        unapproved_discount = VenueDiscount.objects.create(
            name='Pending Discount',
            description='Discount pending approval',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('30.00'),
            start_date=self.tomorrow,
            end_date=self.next_week,
            venue=self.venue,
            created_by=self.provider,
            is_approved=False
        )

        self.client.login(email='admin@example.com', password='testpass123')

        # Test approval
        approval_url = reverse('discount_app:admin_approve_discount', args=['venue', unapproved_discount.id])
        approval_data = {
            'is_approved': 'True',
            'rejection_reason': ''
        }

        response = self.client.post(approval_url, approval_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful approval

        # Check that the discount was approved
        unapproved_discount.refresh_from_db()
        self.assertTrue(unapproved_discount.is_approved)
        self.assertEqual(unapproved_discount.approved_by, self.admin)
        self.assertIsNotNone(unapproved_discount.approved_at)

    def test_admin_discount_dashboard_view(self):
        """Test the admin discount dashboard view"""
        self.client.login(email='admin@example.com', password='testpass123')
        url = reverse('discount_app:admin_discount_dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discount_app/admin/discount_dashboard.html')

        # Check that the dashboard contains statistics
        self.assertContains(response, 'Total Venue Discounts')
        self.assertContains(response, 'Total Service Discounts')
        self.assertContains(response, 'Total Platform Discounts')
