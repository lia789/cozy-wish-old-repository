from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class CartItemModelTest(TestCase):
    """Test the CartItem model"""
    
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
        
        # Create a cart item
        self.cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
    
    def test_cart_item_creation(self):
        """Test creating a cart item is successful"""
        self.assertEqual(self.cart_item.user, self.customer)
        self.assertEqual(self.cart_item.service, self.service)
        self.assertEqual(self.cart_item.quantity, 1)
        self.assertIsNotNone(self.cart_item.date)
        self.assertIsNotNone(self.cart_item.time_slot)
        self.assertIsNotNone(self.cart_item.added_at)
        self.assertIsNotNone(self.cart_item.expires_at)
    
    def test_cart_item_str(self):
        """Test the string representation of a cart item"""
        expected_str = f"{self.customer.email} - {self.service.title} - {self.cart_item.date} {self.cart_item.time_slot}"
        self.assertEqual(str(self.cart_item), expected_str)
    
    def test_cart_item_expiration(self):
        """Test cart item expiration"""
        # Item should not be expired
        self.assertFalse(self.cart_item.is_expired())
        
        # Set expiration to the past
        self.cart_item.expires_at = timezone.now() - timedelta(hours=1)
        self.cart_item.save()
        
        # Item should be expired
        self.assertTrue(self.cart_item.is_expired())
    
    def test_cart_item_get_total_price(self):
        """Test calculating the total price of a cart item"""
        # Regular price
        self.assertEqual(self.cart_item.get_total_price(), Decimal("100.00"))
        
        # Increase quantity
        self.cart_item.quantity = 2
        self.cart_item.save()
        self.assertEqual(self.cart_item.get_total_price(), Decimal("200.00"))
        
        # Add discounted price to service
        self.service.discounted_price = Decimal("80.00")
        self.service.save()
        self.assertEqual(self.cart_item.get_total_price(), Decimal("160.00"))
    
    def test_cart_item_unique_constraint(self):
        """Test that a user cannot have duplicate cart items for the same service, date, and time"""
        # Try to create a duplicate cart item
        with self.assertRaises(Exception):
            CartItem.objects.create(
                user=self.customer,
                service=self.service,
                quantity=1,
                date=self.cart_item.date,
                time_slot=self.cart_item.time_slot,
                expires_at=timezone.now() + timedelta(hours=24)
            )
    
    def test_cart_item_auto_expiration(self):
        """Test that a cart item automatically sets expiration time if not provided"""
        # Create a cart item without specifying expires_at
        new_cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time().replace(hour=10)  # Different time to avoid unique constraint
        )
        
        # Check that expires_at was automatically set
        self.assertIsNotNone(new_cart_item.expires_at)
        
        # Should be approximately 24 hours from now
        time_diff = new_cart_item.expires_at - timezone.now()
        self.assertTrue(timedelta(hours=23) < time_diff < timedelta(hours=25))


class BookingModelTest(TestCase):
    """Test the Booking model"""
    
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
    
    def test_booking_creation(self):
        """Test creating a booking is successful"""
        self.assertEqual(self.booking.user, self.customer)
        self.assertEqual(self.booking.venue, self.venue)
        self.assertEqual(self.booking.total_price, Decimal("100.00"))
        self.assertEqual(self.booking.status, 'confirmed')
        self.assertIsNotNone(self.booking.booking_id)
        self.assertIsNotNone(self.booking.booking_date)
        self.assertIsNotNone(self.booking.last_status_change)
    
    def test_booking_str(self):
        """Test the string representation of a booking"""
        expected_str = f"Booking {self.booking.booking_id} - {self.customer.email}"
        self.assertEqual(str(self.booking), expected_str)
    
    def test_get_earliest_service_datetime(self):
        """Test getting the earliest service datetime for a booking"""
        # Get the earliest service datetime
        earliest_datetime = self.booking.get_earliest_service_datetime()
        
        # Should be a timezone-aware datetime
        self.assertIsNotNone(earliest_datetime)
        self.assertTrue(timezone.is_aware(earliest_datetime))
        
        # Should match the booking item's date and time
        expected_datetime = timezone.make_aware(
            timezone.datetime.combine(self.booking_item.date, self.booking_item.time_slot)
        )
        self.assertEqual(earliest_datetime, expected_datetime)
        
        # Test with no booking items
        self.booking_item.delete()
        self.assertIsNone(self.booking.get_earliest_service_datetime())
    
    def test_can_cancel(self):
        """Test checking if a booking can be cancelled"""
        # Booking is confirmed and more than 6 hours in the future, so should be cancellable
        self.assertTrue(self.booking.can_cancel())
        
        # Change status to cancelled
        self.booking.status = 'cancelled'
        self.booking.save()
        self.assertFalse(self.booking.can_cancel())
        
        # Change status back to confirmed
        self.booking.status = 'confirmed'
        self.booking.save()
        
        # Change booking item date to the past
        self.booking_item.date = timezone.now().date() - timedelta(days=1)
        self.booking_item.save()
        self.assertFalse(self.booking.can_cancel())
    
    def test_cancel(self):
        """Test cancelling a booking"""
        # Cancel the booking
        reason = "Changed my mind"
        result = self.booking.cancel(reason)
        
        # Should return True and update the booking
        self.assertTrue(result)
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.booking.cancellation_reason, reason)
        
        # Try to cancel again
        result = self.booking.cancel("Another reason")
        self.assertFalse(result)  # Should fail because already cancelled
    
    def test_is_upcoming(self):
        """Test checking if a booking is upcoming"""
        # Booking is confirmed and in the future, so should be upcoming
        self.assertTrue(self.booking.is_upcoming())
        
        # Change status to cancelled
        self.booking.status = 'cancelled'
        self.booking.save()
        self.assertFalse(self.booking.is_upcoming())
        
        # Change status back to confirmed
        self.booking.status = 'confirmed'
        self.booking.save()
        
        # Change booking item date to the past
        self.booking_item.date = timezone.now().date() - timedelta(days=1)
        self.booking_item.save()
        self.assertFalse(self.booking.is_upcoming())
    
    def test_is_past_due(self):
        """Test checking if a booking is past due"""
        # Booking is in the future, so should not be past due
        self.assertFalse(self.booking.is_past_due())
        
        # Change booking item date to the past
        self.booking_item.date = timezone.now().date() - timedelta(days=1)
        self.booking_item.save()
        self.assertTrue(self.booking.is_past_due())
        
        # Change status to completed
        self.booking.status = 'completed'
        self.booking.save()
        self.assertFalse(self.booking.is_past_due())
    
    def test_file_dispute(self):
        """Test filing a dispute for a booking"""
        # File a dispute
        reason = "Service not as described"
        result = self.booking.file_dispute(reason)
        
        # Should return True and update the booking
        self.assertTrue(result)
        self.assertEqual(self.booking.status, 'disputed')
        self.assertEqual(self.booking.dispute_reason, reason)
        
        # Try to file another dispute
        result = self.booking.file_dispute("Another reason")
        self.assertFalse(result)  # Should fail because already disputed


class BookingItemModelTest(TestCase):
    """Test the BookingItem model"""
    
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
    
    def test_booking_item_creation(self):
        """Test creating a booking item is successful"""
        self.assertEqual(self.booking_item.booking, self.booking)
        self.assertEqual(self.booking_item.service, self.service)
        self.assertEqual(self.booking_item.service_title, self.service.title)
        self.assertEqual(self.booking_item.service_price, self.service.price)
        self.assertEqual(self.booking_item.quantity, 1)
        self.assertIsNotNone(self.booking_item.date)
        self.assertIsNotNone(self.booking_item.time_slot)
    
    def test_booking_item_str(self):
        """Test the string representation of a booking item"""
        expected_str = f"{self.service.title} - {self.booking_item.date} {self.booking_item.time_slot}"
        self.assertEqual(str(self.booking_item), expected_str)
    
    def test_get_total_price(self):
        """Test calculating the total price of a booking item"""
        # Regular price
        self.assertEqual(self.booking_item.get_total_price(), Decimal("100.00"))
        
        # Increase quantity
        self.booking_item.quantity = 2
        self.booking_item.save()
        self.assertEqual(self.booking_item.get_total_price(), Decimal("200.00"))


class ServiceAvailabilityModelTest(TestCase):
    """Test the ServiceAvailability model"""
    
    def setUp(self):
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
        
        # Create a service availability
        self.availability = ServiceAvailability.objects.create(
            service=self.service,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            max_bookings=3,
            current_bookings=0,
            is_available=True
        )
    
    def test_service_availability_creation(self):
        """Test creating a service availability is successful"""
        self.assertEqual(self.availability.service, self.service)
        self.assertIsNotNone(self.availability.date)
        self.assertIsNotNone(self.availability.time_slot)
        self.assertEqual(self.availability.max_bookings, 3)
        self.assertEqual(self.availability.current_bookings, 0)
        self.assertTrue(self.availability.is_available)
    
    def test_service_availability_str(self):
        """Test the string representation of a service availability"""
        expected_str = f"{self.service.title} - {self.availability.date} {self.availability.time_slot}"
        self.assertEqual(str(self.availability), expected_str)
    
    def test_is_fully_booked(self):
        """Test checking if a service is fully booked"""
        # Not fully booked initially
        self.assertFalse(self.availability.is_fully_booked())
        
        # Set current bookings to max
        self.availability.current_bookings = self.availability.max_bookings
        self.availability.save()
        self.assertTrue(self.availability.is_fully_booked())
        
        # Reset current bookings but set is_available to False
        self.availability.current_bookings = 0
        self.availability.is_available = False
        self.availability.save()
        self.assertTrue(self.availability.is_fully_booked())
    
    def test_increment_bookings(self):
        """Test incrementing the number of bookings"""
        # Increment bookings
        result = self.availability.increment_bookings()
        self.assertTrue(result)
        self.assertEqual(self.availability.current_bookings, 1)
        self.assertTrue(self.availability.is_available)
        
        # Increment to max
        self.availability.increment_bookings()
        self.availability.increment_bookings()
        self.assertEqual(self.availability.current_bookings, 3)
        self.assertFalse(self.availability.is_available)
        
        # Try to increment beyond max
        result = self.availability.increment_bookings()
        self.assertFalse(result)
        self.assertEqual(self.availability.current_bookings, 3)
    
    def test_decrement_bookings(self):
        """Test decrementing the number of bookings"""
        # Set current bookings to max
        self.availability.current_bookings = self.availability.max_bookings
        self.availability.is_available = False
        self.availability.save()
        
        # Decrement bookings
        result = self.availability.decrement_bookings()
        self.assertTrue(result)
        self.assertEqual(self.availability.current_bookings, 2)
        self.assertTrue(self.availability.is_available)
        
        # Decrement to zero
        self.availability.decrement_bookings()
        self.availability.decrement_bookings()
        self.assertEqual(self.availability.current_bookings, 0)
        
        # Try to decrement below zero
        result = self.availability.decrement_bookings()
        self.assertFalse(result)
        self.assertEqual(self.availability.current_bookings, 0)
