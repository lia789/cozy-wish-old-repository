from django.test import TestCase, Client
from django.apps import apps
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from venues_app.models import Service, Venue
from .models import CartItem, Booking, BookingItem, ServiceAvailability
from datetime import timedelta

User = get_user_model()

class BookingCartAppTestCase(TestCase):
    def test_app_installed(self):
        """Test that the booking_cart_app is installed"""
        self.assertTrue(apps.is_installed('booking_cart_app'))

    def test_models_exist(self):
        """Test that the models exist"""
        from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability
        self.assertTrue(CartItem)
        self.assertTrue(Booking)
        self.assertTrue(BookingItem)
        self.assertTrue(ServiceAvailability)

class BookingCartAppFeatureTests(TestCase):
    def setUp(self):
        # Create users
        self.customer = User.objects.create_user(email='customer@example.com', password='testpass', is_customer=True)
        self.provider = User.objects.create_user(email='provider@example.com', password='testpass', is_service_provider=True)
        self.admin = User.objects.create_superuser(email='admin@example.com', password='testpass')
        # Create venue and service
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.provider,
            is_active=True,
            approval_status='approved',
            state='NY',
            county='New York',
            city='New York'
        )
        self.service = Service.objects.create(
            title='Test Service',
            venue=self.venue,
            price=100,
            duration=60,
            is_active=True
        )
        self.client = Client()

    def test_add_to_cart_and_expiration(self):
        self.client.login(email='customer@example.com', password='testpass')
        # Add to cart
        expires_at = timezone.now() + timedelta(hours=24)
        cart_item = CartItem.objects.create(user=self.customer, service=self.service, quantity=1, date=timezone.now().date(), time_slot=timezone.now().time(), expires_at=expires_at)
        self.assertEqual(CartItem.objects.count(), 1)
        # Simulate expiration
        cart_item.expires_at = timezone.now() - timedelta(hours=1)
        cart_item.save()
        self.assertTrue(cart_item.is_expired())

    def test_update_and_remove_cart_item(self):
        self.client.login(email='customer@example.com', password='testpass')
        cart_item = CartItem.objects.create(user=self.customer, service=self.service, quantity=1, date=timezone.now().date(), time_slot=timezone.now().time(), expires_at=timezone.now() + timedelta(hours=24))
        cart_item.quantity = 3
        cart_item.save()
        self.assertEqual(CartItem.objects.get(id=cart_item.id).quantity, 3)
        cart_item.delete()
        self.assertEqual(CartItem.objects.count(), 0)

    def test_checkout_creates_booking(self):
        self.client.login(email='customer@example.com', password='testpass')
        CartItem.objects.create(user=self.customer, service=self.service, quantity=2, date=timezone.now().date(), time_slot=timezone.now().time(), expires_at=timezone.now() + timedelta(hours=24))
        response = self.client.post(reverse('booking_cart_app:checkout'), {'notes': 'Test booking'})
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(BookingItem.objects.count(), 1)

    def test_booking_cancellation_within_allowed_time(self):
        self.client.login(email='customer@example.com', password='testpass')
        booking = Booking.objects.create(user=self.customer, venue=self.venue, total_price=100, status='confirmed')
        BookingItem.objects.create(booking=booking, service=self.service, service_title=self.service.title, service_price=100, quantity=1, date=timezone.now().date() + timedelta(days=1), time_slot=timezone.now().time())
        self.assertTrue(booking.can_cancel())
        response = self.client.post(reverse('booking_cart_app:cancel_booking', args=[booking.booking_id]), {'reason': 'Change of plans'})
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.cancellation_reason, 'Change of plans')

    def test_booking_cancellation_not_allowed(self):
        self.client.login(email='customer@example.com', password='testpass')
        booking = Booking.objects.create(user=self.customer, venue=self.venue, total_price=100, status='confirmed')
        BookingItem.objects.create(booking=booking, service=self.service, service_title=self.service.title, service_price=100, quantity=1, date=timezone.now().date(), time_slot=(timezone.now() + timedelta(minutes=10)).time())
        self.assertFalse(booking.can_cancel())
        response = self.client.post(reverse('booking_cart_app:cancel_booking', args=[booking.booking_id]), {'reason': 'Too late'})
        booking.refresh_from_db()
        self.assertNotEqual(booking.status, 'cancelled')

    def test_service_availability_management(self):
        self.client.login(email='provider@example.com', password='testpass')
        avail = ServiceAvailability.objects.create(service=self.service, date=timezone.now().date() + timedelta(days=1), time_slot=timezone.now().time(), max_bookings=5, current_bookings=0, is_available=True)
        self.assertTrue(avail.is_available)
        avail.increment_bookings()
        self.assertEqual(avail.current_bookings, 1)
        avail.decrement_bookings()
        self.assertEqual(avail.current_bookings, 0)

    def test_access_control(self):
        # Cart view as provider (should redirect)
        self.client.login(email='provider@example.com', password='testpass')
        response = self.client.get(reverse('booking_cart_app:cart'))
        self.assertEqual(response.status_code, 302)
        # Admin booking list as customer (should redirect)
        self.client.login(email='customer@example.com', password='testpass')
        response = self.client.get(reverse('booking_cart_app:admin_booking_list'))
        self.assertEqual(response.status_code, 302)

    def test_booking_list_and_detail_views(self):
        self.client.login(email='customer@example.com', password='testpass')
        booking = Booking.objects.create(user=self.customer, venue=self.venue, total_price=100, status='confirmed')
        BookingItem.objects.create(booking=booking, service=self.service, service_title=self.service.title, service_price=100, quantity=1, date=timezone.now().date() + timedelta(days=1), time_slot=timezone.now().time())
        response = self.client.get(reverse('booking_cart_app:booking_list'))
        self.assertContains(response, str(booking.booking_id))
        response = self.client.get(reverse('booking_cart_app:booking_detail', args=[booking.booking_id]))
        self.assertContains(response, self.service.title)
