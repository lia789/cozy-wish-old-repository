from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class AdminTest(TestCase):
    """Test the admin configuration for the booking_cart_app"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
        # Create an admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
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
        
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
    
    def test_cart_item_admin(self):
        """Test the CartItem admin page"""
        # Get the CartItem admin page
        url = reverse('admin:booking_cart_app_cartitem_changelist')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cart_item.user.email)
        self.assertContains(response, self.cart_item.service.title)
    
    def test_booking_admin(self):
        """Test the Booking admin page"""
        # Get the Booking admin page
        url = reverse('admin:booking_cart_app_booking_changelist')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.booking_id)
        self.assertContains(response, self.booking.user.email)
        self.assertContains(response, self.booking.venue.name)
    
    def test_booking_item_admin(self):
        """Test the BookingItem admin page"""
        # Get the BookingItem admin page
        url = reverse('admin:booking_cart_app_bookingitem_changelist')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking_item.service_title)
        self.assertContains(response, str(self.booking_item.service_price))
    
    def test_service_availability_admin(self):
        """Test the ServiceAvailability admin page"""
        # Get the ServiceAvailability admin page
        url = reverse('admin:booking_cart_app_serviceavailability_changelist')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.title)
        self.assertContains(response, str(self.availability.date))
        self.assertContains(response, str(self.availability.time_slot))
    
    def test_booking_detail_admin(self):
        """Test the Booking detail admin page"""
        # Get the Booking detail admin page
        url = reverse('admin:booking_cart_app_booking_change', args=[self.booking.id])
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.booking_id)
        self.assertContains(response, self.booking.user.email)
        self.assertContains(response, self.booking.venue.name)
        self.assertContains(response, str(self.booking.total_price))
        self.assertContains(response, self.booking.status)
    
    def test_service_availability_detail_admin(self):
        """Test the ServiceAvailability detail admin page"""
        # Get the ServiceAvailability detail admin page
        url = reverse('admin:booking_cart_app_serviceavailability_change', args=[self.availability.id])
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.title)
        self.assertContains(response, str(self.availability.date))
        self.assertContains(response, str(self.availability.time_slot))
        self.assertContains(response, str(self.availability.max_bookings))
        self.assertContains(response, str(self.availability.current_bookings))
