from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability
from booking_cart_app.forms import (
    AddToCartForm, UpdateCartItemForm, CheckoutForm,
    BookingCancellationForm, ServiceAvailabilityForm, DateRangeAvailabilityForm
)

User = get_user_model()

class CustomerViewsTest(TestCase):
    """Test the customer views in the booking_cart_app"""

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
            price=Decimal("100.00"),
            duration=60,
            is_active=True
        )

        # Create service availability
        self.availability = ServiceAvailability.objects.create(
            service=self.service,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0),
            max_bookings=3,
            current_bookings=0,
            is_available=True
        )

        # Create a cart item
        self.cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0),
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Create a booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )

        # Create a booking item
        self.booking_item = BookingItem.objects.create(
            booking=self.booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0)
        )

        # URLs
        self.add_to_cart_url = reverse('booking_cart_app:add_to_cart', args=[self.service.id])
        self.cart_url = reverse('booking_cart_app:cart')
        self.update_cart_item_url = reverse('booking_cart_app:update_cart_item', args=[self.cart_item.id])
        self.remove_from_cart_url = reverse('booking_cart_app:remove_from_cart', args=[self.cart_item.id])
        self.checkout_url = reverse('booking_cart_app:checkout')
        self.booking_confirmation_url = reverse('booking_cart_app:booking_confirmation', args=[self.booking.booking_id])
        self.booking_list_url = reverse('booking_cart_app:booking_list')
        self.booking_detail_url = reverse('booking_cart_app:booking_detail', args=[self.booking.booking_id])
        self.cancel_booking_url = reverse('booking_cart_app:cancel_booking', args=[self.booking.booking_id])

    def test_add_to_cart_view_get(self):
        """Test the add_to_cart view GET request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the add_to_cart page
        response = self.client.get(self.add_to_cart_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/add_to_cart.html')
        self.assertIn('form', response.context)
        self.assertIn('service', response.context)
        self.assertEqual(response.context['service'], self.service)

    def test_add_to_cart_view_post_valid(self):
        """Test the add_to_cart view POST request with valid data"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Delete existing cart item to avoid unique constraint violation
        self.cart_item.delete()

        # Post valid data
        data = {
            'date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'time_slot': '10:00',
            'quantity': 1
        }
        response = self.client.post(self.add_to_cart_url, data)

        # Check response
        self.assertRedirects(response, self.cart_url)

        # Check that a cart item was created
        self.assertTrue(CartItem.objects.filter(
            user=self.customer,
            service=self.service,
            date=data['date'],
            time_slot=data['time_slot'],
            quantity=data['quantity']
        ).exists())

    def test_add_to_cart_view_post_invalid(self):
        """Test the add_to_cart view POST request with invalid data"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Post invalid data (past date)
        data = {
            'date': (timezone.now().date() - timedelta(days=1)).isoformat(),
            'time_slot': '10:00',
            'quantity': 1
        }
        response = self.client.post(self.add_to_cart_url, data)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/add_to_cart.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_add_to_cart_view_not_customer(self):
        """Test the add_to_cart view when user is not a customer"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the add_to_cart page
        response = self.client.get(self.add_to_cart_url)

        # Should redirect to home
        self.assertRedirects(response, reverse('venues_app:home'))

    def test_cart_view(self):
        """Test the cart view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the cart page
        response = self.client.get(self.cart_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/cart.html')
        self.assertIn('cart_items', response.context)
        self.assertIn('total_price', response.context)
        self.assertEqual(len(response.context['cart_items']), 1)
        self.assertEqual(response.context['cart_items'][0], self.cart_item)

    def test_update_cart_item_view_post(self):
        """Test the update_cart_item view POST request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Post valid data
        data = {'quantity': 2}
        response = self.client.post(self.update_cart_item_url, data)

        # Check response
        self.assertRedirects(response, self.cart_url)

        # Check that the cart item was updated
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 2)

    def test_remove_from_cart_view(self):
        """Test the remove_from_cart view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the remove_from_cart page
        response = self.client.get(self.remove_from_cart_url)

        # Check response
        self.assertRedirects(response, self.cart_url)

        # Check that the cart item was deleted
        self.assertFalse(CartItem.objects.filter(id=self.cart_item.id).exists())

    def test_checkout_view_get(self):
        """Test the checkout view GET request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the checkout page
        response = self.client.get(self.checkout_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/checkout.html')
        self.assertIn('form', response.context)
        self.assertIn('venues', response.context)
        self.assertIn('total_price', response.context)

    def test_checkout_with_empty_cart(self):
        """Test the checkout view with an empty cart"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Empty the cart
        CartItem.objects.filter(user=self.customer).delete()

        # Try to access checkout page
        response = self.client.get(self.checkout_url)

        # Check response - should redirect to cart with error message
        self.assertRedirects(response, self.cart_url)

        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your cart is empty.")

    def test_booking_list_view(self):
        """Test the booking_list view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the booking_list page
        response = self.client.get(self.booking_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/booking_list.html')
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)
        self.assertEqual(response.context['bookings'][0], self.booking)

    def test_booking_detail_view(self):
        """Test the booking_detail view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the booking_detail page
        response = self.client.get(self.booking_detail_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/booking_detail.html')
        self.assertIn('booking', response.context)
        self.assertIn('booking_items', response.context)
        self.assertEqual(response.context['booking'], self.booking)
        self.assertEqual(len(response.context['booking_items']), 1)
        self.assertEqual(response.context['booking_items'][0], self.booking_item)

    def test_cancel_booking_view_get(self):
        """Test the cancel_booking view GET request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the cancel_booking page
        response = self.client.get(self.cancel_booking_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/cancel_booking.html')
        self.assertIn('form', response.context)
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'], self.booking)

    def test_cancel_booking_view_post(self):
        """Test the cancel_booking view POST request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Post valid data
        data = {'reason': 'Need to reschedule'}
        response = self.client.post(self.cancel_booking_url, data)

        # Check response
        self.assertRedirects(response, self.booking_list_url)

        # Check that the booking was cancelled
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.booking.cancellation_reason, data['reason'])


class ProviderViewsTest(TestCase):
    """Test the service provider views in the booking_cart_app"""

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
            price=Decimal("100.00"),
            duration=60,
            is_active=True
        )

        # Create service availability
        self.availability = ServiceAvailability.objects.create(
            service=self.service,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0),
            max_bookings=3,
            current_bookings=0,
            is_available=True
        )

        # Create a booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='pending'
        )

        # Create a booking item
        self.booking_item = BookingItem.objects.create(
            booking=self.booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0)
        )

        # URLs
        self.provider_booking_list_url = reverse('booking_cart_app:provider_booking_list')
        self.provider_booking_detail_url = reverse('booking_cart_app:provider_booking_detail', args=[self.booking.booking_id])
        self.provider_update_booking_status_url = reverse('booking_cart_app:provider_update_booking_status', args=[self.booking.booking_id])
        self.provider_service_availability_url = reverse('booking_cart_app:provider_service_availability', args=[self.service.id])
        self.provider_bulk_availability_url = reverse('booking_cart_app:provider_bulk_availability', args=[self.service.id])
        self.provider_delete_availability_url = reverse('booking_cart_app:provider_delete_availability', args=[self.availability.id])

    def test_provider_booking_list_view(self):
        """Test the provider_booking_list view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_booking_list page
        response = self.client.get(self.provider_booking_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/booking_list.html')
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)
        self.assertEqual(response.context['bookings'][0], self.booking)

    def test_provider_booking_detail_view(self):
        """Test the provider_booking_detail view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_booking_detail page
        response = self.client.get(self.provider_booking_detail_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/booking_detail.html')
        self.assertIn('booking', response.context)
        self.assertIn('booking_items', response.context)
        self.assertEqual(response.context['booking'], self.booking)
        self.assertEqual(len(response.context['booking_items']), 1)
        self.assertEqual(response.context['booking_items'][0], self.booking_item)

    def test_provider_update_booking_status_view_get(self):
        """Test the provider_update_booking_status view GET request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_update_booking_status page
        response = self.client.get(self.provider_update_booking_status_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/update_booking_status.html')
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'], self.booking)

    def test_provider_update_booking_status_view_post(self):
        """Test the provider_update_booking_status view POST request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Post valid data
        data = {'status': 'confirmed'}
        response = self.client.post(self.provider_update_booking_status_url, data)

        # Check response
        self.assertRedirects(response, self.provider_booking_detail_url)

        # Check that the booking status was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')

    def test_provider_service_availability_view_get(self):
        """Test the provider_service_availability view GET request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_service_availability page
        response = self.client.get(self.provider_service_availability_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/service_availability.html')
        self.assertIn('service', response.context)
        self.assertIn('form', response.context)
        self.assertIn('availability_records', response.context)
        self.assertEqual(response.context['service'], self.service)
        self.assertEqual(len(response.context['availability_records']), 1)
        self.assertEqual(response.context['availability_records'][0], self.availability)

    def test_provider_service_availability_view_post(self):
        """Test the provider_service_availability view POST request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Post valid data
        data = {
            'date': (timezone.now().date() + timedelta(days=2)).isoformat(),
            'time_slot': '11:00',
            'max_bookings': 5,
            'is_available': True
        }
        response = self.client.post(self.provider_service_availability_url, data)

        # Check response
        self.assertRedirects(response, self.provider_service_availability_url)

        # Check that a new availability record was created
        self.assertTrue(ServiceAvailability.objects.filter(
            service=self.service,
            date=data['date'],
            time_slot=data['time_slot'],
            max_bookings=data['max_bookings'],
            is_available=data['is_available']
        ).exists())

    def test_provider_bulk_availability_view_get(self):
        """Test the provider_bulk_availability view GET request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_bulk_availability page
        response = self.client.get(self.provider_bulk_availability_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/bulk_availability.html')
        self.assertIn('service', response.context)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['service'], self.service)

    def test_provider_delete_availability_view(self):
        """Test the provider_delete_availability view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider_delete_availability page
        response = self.client.get(self.provider_delete_availability_url)

        # Check response
        self.assertRedirects(response, self.provider_service_availability_url)

        # Check that the availability record was deleted
        self.assertFalse(ServiceAvailability.objects.filter(id=self.availability.id).exists())


class AdminViewsTest(TestCase):
    """Test the admin views in the booking_cart_app"""

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

        # Create an admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
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

        # Create a booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='pending'
        )

        # Create a booking item
        self.booking_item = BookingItem.objects.create(
            booking=self.booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0)
        )

        # URLs
        self.admin_booking_list_url = reverse('booking_cart_app:admin_booking_list')
        self.admin_booking_detail_url = reverse('booking_cart_app:admin_booking_detail', args=[self.booking.booking_id])
        self.admin_update_booking_status_url = reverse('booking_cart_app:admin_update_booking_status', args=[self.booking.booking_id])
        self.admin_booking_analytics_url = reverse('booking_cart_app:admin_booking_analytics')

    def test_admin_booking_list_view(self):
        """Test the admin_booking_list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin_booking_list page
        response = self.client.get(self.admin_booking_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/admin/booking_list.html')
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)
        self.assertEqual(response.context['bookings'][0], self.booking)

    def test_admin_booking_detail_view(self):
        """Test the admin_booking_detail view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin_booking_detail page
        response = self.client.get(self.admin_booking_detail_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/admin/booking_detail.html')
        self.assertIn('booking', response.context)
        self.assertIn('booking_items', response.context)
        self.assertEqual(response.context['booking'], self.booking)
        self.assertEqual(len(response.context['booking_items']), 1)
        self.assertEqual(response.context['booking_items'][0], self.booking_item)

    def test_admin_update_booking_status_view_get(self):
        """Test the admin_update_booking_status view GET request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin_update_booking_status page
        response = self.client.get(self.admin_update_booking_status_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/admin/update_booking_status.html')
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'], self.booking)

    def test_admin_update_booking_status_view_post(self):
        """Test the admin_update_booking_status view POST request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Post valid data
        data = {'status': 'confirmed'}
        response = self.client.post(self.admin_update_booking_status_url, data)

        # Check response
        self.assertRedirects(response, self.admin_booking_detail_url)

        # Check that the booking status was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')

    def test_admin_booking_analytics_view(self):
        """Test the admin_booking_analytics view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin_booking_analytics page
        response = self.client.get(self.admin_booking_analytics_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/admin/booking_analytics.html')
        self.assertIn('total_bookings', response.context)
        self.assertIn('bookings_by_status', response.context)
        self.assertIn('bookings_by_venue', response.context)
        self.assertIn('bookings_by_month', response.context)
        self.assertEqual(response.context['total_bookings'], 1)
