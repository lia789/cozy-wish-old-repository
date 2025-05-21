from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability
from booking_cart_app.utils import (
    get_cart_items, get_cart_total, clear_cart, 
    create_booking_from_cart, check_service_availability,
    get_upcoming_bookings, get_past_bookings
)

User = get_user_model()

class UtilsTest(TestCase):
    """Test the utility functions in the booking_cart_app"""
    
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
        
        # Create a past booking
        self.past_booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='completed'
        )
        
        # Create a past booking item
        self.past_booking_item = BookingItem.objects.create(
            booking=self.past_booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() - timedelta(days=7),
            time_slot=timezone.now().time().replace(hour=10, minute=0)
        )
    
    def test_get_cart_items(self):
        """Test the get_cart_items function"""
        # Get cart items for the customer
        cart_items = get_cart_items(self.customer)
        
        # Check result
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0], self.cart_item)
        
        # Get cart items for a user with no cart items
        cart_items = get_cart_items(self.provider)
        self.assertEqual(len(cart_items), 0)
    
    def test_get_cart_total(self):
        """Test the get_cart_total function"""
        # Get cart total for the customer
        total = get_cart_total(self.customer)
        
        # Check result
        self.assertEqual(total, Decimal("100.00"))
        
        # Add another cart item
        CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=2,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time().replace(hour=11, minute=0),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Get updated cart total
        total = get_cart_total(self.customer)
        self.assertEqual(total, Decimal("300.00"))
        
        # Get cart total for a user with no cart items
        total = get_cart_total(self.provider)
        self.assertEqual(total, Decimal("0.00"))
    
    def test_clear_cart(self):
        """Test the clear_cart function"""
        # Clear the customer's cart
        clear_cart(self.customer)
        
        # Check that the cart is empty
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)
    
    def test_create_booking_from_cart(self):
        """Test the create_booking_from_cart function"""
        # Create a booking from the customer's cart
        booking = create_booking_from_cart(self.customer, "Test notes")
        
        # Check that the booking was created
        self.assertIsNotNone(booking)
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(booking.venue, self.venue)
        self.assertEqual(booking.total_price, Decimal("100.00"))
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.notes, "Test notes")
        
        # Check that a booking item was created
        booking_items = BookingItem.objects.filter(booking=booking)
        self.assertEqual(booking_items.count(), 1)
        self.assertEqual(booking_items[0].service, self.service)
        self.assertEqual(booking_items[0].service_title, self.service.title)
        self.assertEqual(booking_items[0].service_price, self.service.price)
        self.assertEqual(booking_items[0].quantity, 1)
        
        # Check that the cart was cleared
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 1)
    
    def test_check_service_availability(self):
        """Test the check_service_availability function"""
        # Check availability for a valid date and time
        is_available, message = check_service_availability(
            self.service,
            timezone.now().date() + timedelta(days=1),
            timezone.now().time().replace(hour=10, minute=0),
            1
        )
        self.assertTrue(is_available)
        self.assertEqual(message, "")
        
        # Check availability for a past date
        is_available, message = check_service_availability(
            self.service,
            timezone.now().date() - timedelta(days=1),
            timezone.now().time().replace(hour=10, minute=0),
            1
        )
        self.assertFalse(is_available)
        self.assertIn("past", message)
        
        # Check availability for a fully booked service
        self.availability.current_bookings = self.availability.max_bookings
        self.availability.is_available = False
        self.availability.save()
        
        is_available, message = check_service_availability(
            self.service,
            timezone.now().date() + timedelta(days=1),
            timezone.now().time().replace(hour=10, minute=0),
            1
        )
        self.assertFalse(is_available)
        self.assertIn("fully booked", message)
        
        # Check availability for a service with limited availability
        self.availability.current_bookings = 2
        self.availability.is_available = True
        self.availability.save()
        
        is_available, message = check_service_availability(
            self.service,
            timezone.now().date() + timedelta(days=1),
            timezone.now().time().replace(hour=10, minute=0),
            2
        )
        self.assertFalse(is_available)
        self.assertIn("Only 1 slots available", message)
    
    def test_get_upcoming_bookings(self):
        """Test the get_upcoming_bookings function"""
        # Get upcoming bookings for the customer
        upcoming_bookings = get_upcoming_bookings(self.customer)
        
        # Check result
        self.assertEqual(len(upcoming_bookings), 1)
        self.assertEqual(upcoming_bookings[0], self.booking)
    
    def test_get_past_bookings(self):
        """Test the get_past_bookings function"""
        # Get past bookings for the customer
        past_bookings = get_past_bookings(self.customer)
        
        # Check result
        self.assertEqual(len(past_bookings), 1)
        self.assertEqual(past_bookings[0], self.past_booking)
