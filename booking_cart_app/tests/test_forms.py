from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability
from booking_cart_app.forms import (
    AddToCartForm, UpdateCartItemForm, CheckoutForm,
    BookingCancellationForm, ServiceAvailabilityForm, DateRangeAvailabilityForm
)

User = get_user_model()

class AddToCartFormTest(TestCase):
    """Test the AddToCartForm"""
    
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
        
        # Valid form data
        self.valid_data = {
            'date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'time_slot': '10:00',
            'quantity': 1
        }
    
    def test_add_to_cart_form_valid(self):
        """Test that the form is valid with correct data"""
        form = AddToCartForm(
            service=self.service,
            user=self.customer,
            data=self.valid_data
        )
        self.assertTrue(form.is_valid())
    
    def test_add_to_cart_form_past_date(self):
        """Test that the form is invalid with a past date"""
        past_data = self.valid_data.copy()
        past_data['date'] = (timezone.now().date() - timedelta(days=1)).isoformat()
        
        form = AddToCartForm(
            service=self.service,
            user=self.customer,
            data=past_data
        )
        self.assertFalse(form.is_valid())
        self.assertIn('You cannot book a service in the past', str(form.errors))
    
    def test_add_to_cart_form_fully_booked(self):
        """Test that the form is invalid when the service is fully booked"""
        # Set the service as fully booked
        self.availability.current_bookings = self.availability.max_bookings
        self.availability.is_available = False
        self.availability.save()
        
        form = AddToCartForm(
            service=self.service,
            user=self.customer,
            data=self.valid_data
        )
        self.assertFalse(form.is_valid())
        self.assertIn('fully booked', str(form.errors))
    
    def test_add_to_cart_form_limited_availability(self):
        """Test that the form is invalid when trying to book more than available slots"""
        # Set the service with limited availability
        self.availability.current_bookings = 2
        self.availability.save()
        
        # Try to book 2 slots when only 1 is available
        limited_data = self.valid_data.copy()
        limited_data['quantity'] = 2
        
        form = AddToCartForm(
            service=self.service,
            user=self.customer,
            data=limited_data
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Only 1 slots available', str(form.errors))
    
    def test_add_to_cart_form_no_availability_record(self):
        """Test that the form creates a new availability record if none exists"""
        # Delete the existing availability record
        self.availability.delete()
        
        # Use a different time to avoid conflicts
        new_time_data = self.valid_data.copy()
        new_time_data['time_slot'] = '11:00'
        
        form = AddToCartForm(
            service=self.service,
            user=self.customer,
            data=new_time_data
        )
        self.assertTrue(form.is_valid())
        
        # Check that a new availability record was created
        new_availability = ServiceAvailability.objects.filter(
            service=self.service,
            date=timezone.now().date() + timedelta(days=1),
            time_slot='11:00:00'
        ).first()
        
        self.assertIsNotNone(new_availability)
        self.assertEqual(new_availability.max_bookings, 10)
        self.assertEqual(new_availability.current_bookings, 0)
        self.assertTrue(new_availability.is_available)


class UpdateCartItemFormTest(TestCase):
    """Test the UpdateCartItemForm"""
    
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
    
    def test_update_cart_item_form_valid(self):
        """Test that the form is valid with correct data"""
        form = UpdateCartItemForm(
            instance=self.cart_item,
            data={'quantity': 2}
        )
        self.assertTrue(form.is_valid())
    
    def test_update_cart_item_form_invalid_quantity(self):
        """Test that the form is invalid with an invalid quantity"""
        form = UpdateCartItemForm(
            instance=self.cart_item,
            data={'quantity': 0}  # Invalid quantity
        )
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        
        form = UpdateCartItemForm(
            instance=self.cart_item,
            data={'quantity': 6}  # Invalid quantity (max is 5)
        )
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)


class CheckoutFormTest(TestCase):
    """Test the CheckoutForm"""
    
    def test_checkout_form_valid(self):
        """Test that the form is valid with correct data"""
        form = CheckoutForm(data={'notes': 'Please call me before the appointment.'})
        self.assertTrue(form.is_valid())
    
    def test_checkout_form_empty_notes(self):
        """Test that the form is valid with empty notes"""
        form = CheckoutForm(data={'notes': ''})
        self.assertTrue(form.is_valid())


class BookingCancellationFormTest(TestCase):
    """Test the BookingCancellationForm"""
    
    def test_booking_cancellation_form_valid(self):
        """Test that the form is valid with correct data"""
        form = BookingCancellationForm(data={'reason': 'I need to reschedule.'})
        self.assertTrue(form.is_valid())
    
    def test_booking_cancellation_form_empty_reason(self):
        """Test that the form is valid with empty reason"""
        form = BookingCancellationForm(data={'reason': ''})
        self.assertTrue(form.is_valid())


class ServiceAvailabilityFormTest(TestCase):
    """Test the ServiceAvailabilityForm"""
    
    def setUp(self):
        # Valid form data
        self.valid_data = {
            'date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'time_slot': '10:00',
            'max_bookings': 3,
            'is_available': True
        }
    
    def test_service_availability_form_valid(self):
        """Test that the form is valid with correct data"""
        form = ServiceAvailabilityForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_service_availability_form_past_date(self):
        """Test that the form is invalid with a past date"""
        past_data = self.valid_data.copy()
        past_data['date'] = (timezone.now().date() - timedelta(days=1)).isoformat()
        
        form = ServiceAvailabilityForm(data=past_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cannot set availability for a past date', str(form.errors))
    
    def test_service_availability_form_invalid_max_bookings(self):
        """Test that the form is invalid with invalid max_bookings"""
        invalid_data = self.valid_data.copy()
        invalid_data['max_bookings'] = 0  # Invalid max_bookings
        
        form = ServiceAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('max_bookings', form.errors)
        
        invalid_data['max_bookings'] = 11  # Invalid max_bookings (max is 10)
        form = ServiceAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('max_bookings', form.errors)


class DateRangeAvailabilityFormTest(TestCase):
    """Test the DateRangeAvailabilityForm"""
    
    def setUp(self):
        # Valid form data
        self.valid_data = {
            'start_date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=7)).isoformat(),
            'start_time': '09:00',
            'end_time': '17:00',
            'interval': 60,
            'max_bookings': 3,
            'is_available': True
        }
    
    def test_date_range_availability_form_valid(self):
        """Test that the form is valid with correct data"""
        form = DateRangeAvailabilityForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_date_range_availability_form_past_start_date(self):
        """Test that the form is invalid with a past start date"""
        past_data = self.valid_data.copy()
        past_data['start_date'] = (timezone.now().date() - timedelta(days=1)).isoformat()
        
        form = DateRangeAvailabilityForm(data=past_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Start date cannot be in the past', str(form.errors))
    
    def test_date_range_availability_form_end_date_before_start_date(self):
        """Test that the form is invalid when end date is before start date"""
        invalid_data = self.valid_data.copy()
        invalid_data['end_date'] = (timezone.now().date()).isoformat()  # End date before start date
        
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('End date must be after start date', str(form.errors))
    
    def test_date_range_availability_form_end_time_before_start_time(self):
        """Test that the form is invalid when end time is before start time"""
        invalid_data = self.valid_data.copy()
        invalid_data['end_time'] = '08:00'  # End time before start time
        
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('End time must be after start time', str(form.errors))
    
    def test_date_range_availability_form_invalid_interval(self):
        """Test that the form is invalid with invalid interval"""
        invalid_data = self.valid_data.copy()
        invalid_data['interval'] = 10  # Invalid interval (min is 15)
        
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('interval', form.errors)
        
        invalid_data['interval'] = 150  # Invalid interval (max is 120)
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('interval', form.errors)
    
    def test_date_range_availability_form_invalid_max_bookings(self):
        """Test that the form is invalid with invalid max_bookings"""
        invalid_data = self.valid_data.copy()
        invalid_data['max_bookings'] = 0  # Invalid max_bookings
        
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('max_bookings', form.errors)
        
        invalid_data['max_bookings'] = 11  # Invalid max_bookings (max is 10)
        form = DateRangeAvailabilityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('max_bookings', form.errors)
