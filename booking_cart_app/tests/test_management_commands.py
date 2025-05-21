from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command
from decimal import Decimal
from datetime import timedelta
from io import StringIO

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class ManagementCommandsTest(TestCase):
    """Test the management commands in the booking_cart_app"""
    
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
        
        # Create an expired cart item
        self.expired_cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        
        # Create a non-expired cart item
        self.active_cart_item = CartItem.objects.create(
            user=self.customer,
            service=self.service,
            quantity=2,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time().replace(hour=11),
            expires_at=timezone.now() + timedelta(hours=23)  # Not expired
        )
        
        # Create a booking that needs to be auto-completed
        self.past_booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a past booking item
        self.past_booking_item = BookingItem.objects.create(
            booking=self.past_booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() - timedelta(days=1),
            time_slot=timezone.now().time()
        )
        
        # Create a future booking
        self.future_booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='confirmed'
        )
        
        # Create a future booking item
        self.future_booking_item = BookingItem.objects.create(
            booking=self.future_booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() + timedelta(days=7),
            time_slot=timezone.now().time()
        )
    
    def test_cleanup_expired_cart_items_command(self):
        """Test the cleanup_expired_cart_items command"""
        # Capture command output
        out = StringIO()
        
        # Run the command
        call_command('cleanup_expired_cart_items', stdout=out)
        
        # Check that the expired cart item was deleted
        self.assertFalse(CartItem.objects.filter(id=self.expired_cart_item.id).exists())
        
        # Check that the non-expired cart item was not deleted
        self.assertTrue(CartItem.objects.filter(id=self.active_cart_item.id).exists())
        
        # Check command output
        self.assertIn("Deleted 1 expired cart items", out.getvalue())
    
    def test_auto_complete_bookings_command(self):
        """Test the auto_complete_bookings command"""
        # Capture command output
        out = StringIO()
        
        # Run the command
        call_command('auto_complete_bookings', stdout=out)
        
        # Check that the past booking was auto-completed
        self.past_booking.refresh_from_db()
        self.assertEqual(self.past_booking.status, 'completed')
        
        # Check that the future booking was not auto-completed
        self.future_booking.refresh_from_db()
        self.assertEqual(self.future_booking.status, 'confirmed')
        
        # Check command output
        self.assertIn("Auto-completed 1 bookings", out.getvalue())
    
    def test_generate_booking_report_command(self):
        """Test the generate_booking_report command"""
        # Capture command output
        out = StringIO()
        
        # Run the command
        call_command('generate_booking_report', stdout=out)
        
        # Check command output
        self.assertIn("Booking Report", out.getvalue())
        self.assertIn("Total Bookings: 2", out.getvalue())
        self.assertIn("Confirmed: 2", out.getvalue())
