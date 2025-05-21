from django.test import TestCase
from django.template import Context, Template
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import Booking, BookingItem
from booking_cart_app.templatetags.booking_cart_tags import (
    booking_status_class, booking_status_icon, format_price, 
    get_discount_percentage, time_until_booking
)

class TemplateTagsTest(TestCase):
    """Test the template tags in the booking_cart_app"""
    
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(name="Spa")
        
        # Create a venue
        self.venue = Venue.objects.create(
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
            discounted_price=Decimal("80.00"),
            duration=60,
            is_active=True
        )
        
        # Create a booking
        self.booking = Booking.objects.create(
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
    
    def test_booking_status_class(self):
        """Test the booking_status_class template tag"""
        self.assertEqual(booking_status_class('pending'), 'warning')
        self.assertEqual(booking_status_class('confirmed'), 'success')
        self.assertEqual(booking_status_class('cancelled'), 'danger')
        self.assertEqual(booking_status_class('completed'), 'info')
        self.assertEqual(booking_status_class('disputed'), 'secondary')
        self.assertEqual(booking_status_class('unknown'), 'secondary')  # Default
    
    def test_booking_status_icon(self):
        """Test the booking_status_icon template tag"""
        self.assertEqual(booking_status_icon('pending'), 'fa-clock')
        self.assertEqual(booking_status_icon('confirmed'), 'fa-check')
        self.assertEqual(booking_status_icon('cancelled'), 'fa-times')
        self.assertEqual(booking_status_icon('completed'), 'fa-check-double')
        self.assertEqual(booking_status_icon('disputed'), 'fa-exclamation-triangle')
        self.assertEqual(booking_status_icon('unknown'), 'fa-question')  # Default
    
    def test_format_price(self):
        """Test the format_price template tag"""
        self.assertEqual(format_price(Decimal('100.00')), '$100.00')
        self.assertEqual(format_price(Decimal('100.50')), '$100.50')
        self.assertEqual(format_price(Decimal('0.00')), '$0.00')
        self.assertEqual(format_price(None), '$0.00')  # Default
    
    def test_get_discount_percentage(self):
        """Test the get_discount_percentage template tag"""
        self.assertEqual(get_discount_percentage(Decimal('100.00'), Decimal('80.00')), 20)
        self.assertEqual(get_discount_percentage(Decimal('100.00'), Decimal('50.00')), 50)
        self.assertEqual(get_discount_percentage(Decimal('100.00'), Decimal('100.00')), 0)
        self.assertEqual(get_discount_percentage(Decimal('0.00'), Decimal('0.00')), 0)
        self.assertEqual(get_discount_percentage(None, None), 0)  # Default
    
    def test_time_until_booking(self):
        """Test the time_until_booking template tag"""
        # Test with a future booking
        future_date = timezone.now() + timedelta(days=1, hours=2)
        self.assertIn('1 day', time_until_booking(future_date))
        
        # Test with a past booking
        past_date = timezone.now() - timedelta(days=1)
        self.assertEqual(time_until_booking(past_date), 'Booking has passed')
        
        # Test with a booking in the next hour
        soon_date = timezone.now() + timedelta(minutes=30)
        self.assertIn('minutes', time_until_booking(soon_date))
    
    def test_template_tags_in_template(self):
        """Test the template tags in a template"""
        # Create a template that uses the template tags
        template = Template(
            '{% load booking_cart_tags %}'
            '{{ booking.status|booking_status_class }}'
            '{{ booking.status|booking_status_icon }}'
            '{{ service.price|format_price }}'
            '{% get_discount_percentage service.price service.discounted_price %}'
        )
        
        # Render the template
        context = Context({'booking': self.booking, 'service': self.service})
        rendered = template.render(context)
        
        # Check the rendered output
        self.assertIn('success', rendered)  # booking_status_class
        self.assertIn('fa-check', rendered)  # booking_status_icon
        self.assertIn('$100.00', rendered)  # format_price
        self.assertIn('20', rendered)  # get_discount_percentage
