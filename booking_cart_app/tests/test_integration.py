from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class IntegrationTest(TestCase):
    """Test the integration between different components of the booking_cart_app"""
    
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
    
    def test_complete_booking_flow(self):
        """Test the complete booking flow from adding to cart to booking confirmation"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Step 1: Add service to cart
        add_to_cart_url = reverse('booking_cart_app:add_to_cart', args=[self.service.id])
        data = {
            'date': (timezone.now().date() + timedelta(days=1)).isoformat(),
            'time_slot': '10:00',
            'quantity': 1
        }
        response = self.client.post(add_to_cart_url, data)
        self.assertRedirects(response, reverse('booking_cart_app:cart'))
        
        # Check that a cart item was created
        self.assertTrue(CartItem.objects.filter(
            user=self.customer,
            service=self.service,
            date=data['date'],
            time_slot=data['time_slot'],
            quantity=data['quantity']
        ).exists())
        
        # Step 2: View cart
        cart_url = reverse('booking_cart_app:cart')
        response = self.client.get(cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/cart.html')
        
        # Step 3: Proceed to checkout
        checkout_url = reverse('booking_cart_app:checkout')
        response = self.client.get(checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/checkout.html')
        
        # Step 4: Complete checkout
        data = {'notes': 'Please call me before the appointment.'}
        response = self.client.post(checkout_url, data)
        
        # Check that the booking was created
        booking = Booking.objects.filter(user=self.customer).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.venue, self.venue)
        self.assertEqual(booking.total_price, Decimal("100.00"))
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.notes, data['notes'])
        
        # Check that a booking item was created
        booking_item = BookingItem.objects.filter(booking=booking).first()
        self.assertIsNotNone(booking_item)
        self.assertEqual(booking_item.service, self.service)
        self.assertEqual(booking_item.service_title, self.service.title)
        self.assertEqual(booking_item.service_price, self.service.price)
        self.assertEqual(booking_item.quantity, 1)
        
        # Check that the cart was cleared
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 1)
        
        # Step 5: View booking confirmation
        booking_confirmation_url = reverse('booking_cart_app:booking_confirmation', args=[booking.booking_id])
        response = self.client.get(booking_confirmation_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/booking_confirmation.html')
        
        # Step 6: View booking list
        booking_list_url = reverse('booking_cart_app:booking_list')
        response = self.client.get(booking_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/booking_list.html')
        self.assertIn(booking, response.context['bookings'])
        
        # Step 7: View booking detail
        booking_detail_url = reverse('booking_cart_app:booking_detail', args=[booking.booking_id])
        response = self.client.get(booking_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/booking_detail.html')
        self.assertEqual(response.context['booking'], booking)
        
        # Step 8: Cancel booking
        cancel_booking_url = reverse('booking_cart_app:cancel_booking', args=[booking.booking_id])
        response = self.client.get(cancel_booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/cancel_booking.html')
        
        data = {'reason': 'Need to reschedule'}
        response = self.client.post(cancel_booking_url, data)
        self.assertRedirects(response, booking_list_url)
        
        # Check that the booking was cancelled
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.cancellation_reason, data['reason'])
        
        # Check that the service availability was updated
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.current_bookings, 0)
    
    def test_provider_booking_management_flow(self):
        """Test the provider booking management flow"""
        # Create a booking
        booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            total_price=Decimal("100.00"),
            status='pending'
        )
        
        # Create a booking item
        booking_item = BookingItem.objects.create(
            booking=booking,
            service=self.service,
            service_title=self.service.title,
            service_price=self.service.price,
            quantity=1,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time().replace(hour=10, minute=0)
        )
        
        # Update service availability
        self.availability.current_bookings = 1
        self.availability.save()
        
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')
        
        # Step 1: View booking list
        provider_booking_list_url = reverse('booking_cart_app:provider_booking_list')
        response = self.client.get(provider_booking_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/booking_list.html')
        self.assertIn(booking, response.context['bookings'])
        
        # Step 2: View booking detail
        provider_booking_detail_url = reverse('booking_cart_app:provider_booking_detail', args=[booking.booking_id])
        response = self.client.get(provider_booking_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/booking_detail.html')
        self.assertEqual(response.context['booking'], booking)
        
        # Step 3: Update booking status
        provider_update_booking_status_url = reverse('booking_cart_app:provider_update_booking_status', args=[booking.booking_id])
        response = self.client.get(provider_update_booking_status_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/update_booking_status.html')
        
        data = {'status': 'confirmed'}
        response = self.client.post(provider_update_booking_status_url, data)
        self.assertRedirects(response, provider_booking_detail_url)
        
        # Check that the booking status was updated
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        # Step 4: View service availability
        provider_service_availability_url = reverse('booking_cart_app:provider_service_availability', args=[self.service.id])
        response = self.client.get(provider_service_availability_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/service_availability.html')
        self.assertEqual(response.context['service'], self.service)
        self.assertIn(self.availability, response.context['availability_records'])
        
        # Step 5: Add new availability
        data = {
            'date': (timezone.now().date() + timedelta(days=2)).isoformat(),
            'time_slot': '11:00',
            'max_bookings': 5,
            'is_available': True
        }
        response = self.client.post(provider_service_availability_url, data)
        self.assertRedirects(response, provider_service_availability_url)
        
        # Check that a new availability record was created
        self.assertTrue(ServiceAvailability.objects.filter(
            service=self.service,
            date=data['date'],
            time_slot=data['time_slot'],
            max_bookings=data['max_bookings'],
            is_available=data['is_available']
        ).exists())
        
        # Step 6: View bulk availability
        provider_bulk_availability_url = reverse('booking_cart_app:provider_bulk_availability', args=[self.service.id])
        response = self.client.get(provider_bulk_availability_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_cart_app/provider/bulk_availability.html')
        self.assertEqual(response.context['service'], self.service)
