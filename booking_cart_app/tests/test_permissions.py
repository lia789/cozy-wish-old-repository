from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class PermissionsTest(TestCase):
    """Test the permissions in the booking_cart_app"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
        # Create a customer user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create another customer user
        self.other_customer = User.objects.create_user(
            email='other_customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create a provider user
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create another provider user
        self.other_provider = User.objects.create_user(
            email='other_provider@example.com',
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
        
        # Create another venue
        self.other_venue = Venue.objects.create(
            owner=self.other_provider,
            name="Other Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="456",
            street_name="Main St",
            about="Another luxury spa in the heart of the city.",
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
        
        # Create another service
        self.other_service = Service.objects.create(
            venue=self.other_venue,
            title="Deep Tissue Massage",
            short_description="A deep tissue massage.",
            price=Decimal("120.00"),
            duration=60,
            is_active=True
        )
        
        # Create a cart item
        self.cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
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
            time_slot=timezone.now().time()
        )
        
        # Create service availability
        self.availability = ServiceAvailability.objects.create(
            service=self.service,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            max_bookings=3,
            current_bookings=0,
            is_available=True
        )
        
        # URLs
        self.cart_url = reverse('booking_cart_app:cart')
        self.update_cart_item_url = reverse('booking_cart_app:update_cart_item', args=[self.cart_item.id])
        self.remove_from_cart_url = reverse('booking_cart_app:remove_from_cart', args=[self.cart_item.id])
        self.booking_detail_url = reverse('booking_cart_app:booking_detail', args=[self.booking.booking_id])
        self.cancel_booking_url = reverse('booking_cart_app:cancel_booking', args=[self.booking.booking_id])
        self.provider_booking_list_url = reverse('booking_cart_app:provider_booking_list')
        self.provider_booking_detail_url = reverse('booking_cart_app:provider_booking_detail', args=[self.booking.booking_id])
        self.provider_service_availability_url = reverse('booking_cart_app:provider_service_availability', args=[self.service.id])
        self.admin_booking_list_url = reverse('booking_cart_app:admin_booking_list')
    
    def test_customer_permissions(self):
        """Test that customers can only access their own resources"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Customer can access their own cart
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        
        # Customer can update their own cart item
        response = self.client.post(self.update_cart_item_url, {'quantity': 2})
        self.assertRedirects(response, self.cart_url)
        
        # Customer can remove their own cart item
        response = self.client.get(self.remove_from_cart_url)
        self.assertRedirects(response, self.cart_url)
        
        # Customer can view their own booking
        response = self.client.get(self.booking_detail_url)
        self.assertEqual(response.status_code, 200)
        
        # Customer can cancel their own booking
        response = self.client.get(self.cancel_booking_url)
        self.assertEqual(response.status_code, 200)
        
        # Customer cannot access provider views
        response = self.client.get(self.provider_booking_list_url)
        self.assertRedirects(response, reverse('venues_app:home'))
        
        # Customer cannot access admin views
        response = self.client.get(self.admin_booking_list_url)
        self.assertRedirects(response, reverse('venues_app:home'))
        
        # Logout and login as other customer
        self.client.logout()
        self.client.login(username='other_customer@example.com', password='testpass123')
        
        # Other customer cannot view another customer's booking
        response = self.client.get(self.booking_detail_url)
        self.assertEqual(response.status_code, 404)
        
        # Other customer cannot cancel another customer's booking
        response = self.client.get(self.cancel_booking_url)
        self.assertEqual(response.status_code, 404)
    
    def test_provider_permissions(self):
        """Test that providers can only access their own resources"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')
        
        # Provider can access their own booking list
        response = self.client.get(self.provider_booking_list_url)
        self.assertEqual(response.status_code, 200)
        
        # Provider can view bookings for their venue
        response = self.client.get(self.provider_booking_detail_url)
        self.assertEqual(response.status_code, 200)
        
        # Provider can access their own service availability
        response = self.client.get(self.provider_service_availability_url)
        self.assertEqual(response.status_code, 200)
        
        # Provider cannot access customer views
        response = self.client.get(self.cart_url)
        self.assertRedirects(response, reverse('venues_app:home'))
        
        # Provider cannot access admin views
        response = self.client.get(self.admin_booking_list_url)
        self.assertRedirects(response, reverse('venues_app:home'))
        
        # Logout and login as other provider
        self.client.logout()
        self.client.login(username='other_provider@example.com', password='testpass123')
        
        # Other provider cannot view bookings for another provider's venue
        response = self.client.get(self.provider_booking_detail_url)
        self.assertEqual(response.status_code, 404)
        
        # Other provider cannot access another provider's service availability
        response = self.client.get(self.provider_service_availability_url)
        self.assertEqual(response.status_code, 404)
    
    def test_admin_permissions(self):
        """Test that admins can access all resources"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Admin can access admin views
        response = self.client.get(self.admin_booking_list_url)
        self.assertEqual(response.status_code, 200)
        
        # Admin can access provider views
        response = self.client.get(self.provider_booking_list_url)
        self.assertEqual(response.status_code, 200)
        
        # Admin can access customer views
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
