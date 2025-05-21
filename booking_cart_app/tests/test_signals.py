from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class SignalsTest(TestCase):
    """Test the signals in the booking_cart_app"""
    
    def setUp(self):
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
    
    def test_booking_item_creation_signal(self):
        """Test that creating a booking item increments the service availability"""
        # Create a booking
        booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a booking item
        booking_item = BookingItem.objects.create(
            booking=booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=self.availability.date,
            time_slot=self.availability.time_slot
        )
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 1)
    
    def test_booking_item_deletion_signal(self):
        """Test that deleting a booking item decrements the service availability"""
        # Create a booking
        booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a booking item
        booking_item = BookingItem.objects.create(
            booking=booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=self.availability.date,
            time_slot=self.availability.time_slot
        )
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 1)
        
        # Delete the booking item
        booking_item.delete()
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 0)
    
    def test_booking_cancellation_signal(self):
        """Test that cancelling a booking decrements the service availability"""
        # Create a booking
        booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a booking item
        booking_item = BookingItem.objects.create(
            booking=booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=self.availability.date,
            time_slot=self.availability.time_slot
        )
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 1)
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 0)
    
    def test_cart_item_expiration_signal(self):
        """Test that expired cart items are automatically deleted"""
        # Create a cart item that expires in the past
        cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        # Run the cleanup command (this would normally be done by a cron job)
        from django.core.management import call_command
        call_command('cleanup_expired_cart_items')
        
        # Check that the cart item was deleted
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
