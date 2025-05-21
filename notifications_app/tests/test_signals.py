from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification
)
from booking_cart_app.models import Booking
from venues_app.models import Venue
from review_app.models import Review, ReviewResponse
from accounts_app.models import ServiceProviderProfile

User = get_user_model()


class BookingSignalTest(TestCase):
    """Test the booking signals"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_active=True,
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_active=True,
            is_service_provider=True
        )

        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            description='Test venue description',
            owner=self.provider
        )

        # Create notification category
        self.booking_category = NotificationCategory.objects.create(
            name='Booking',
            description='Booking notifications'
        )

    @patch('notifications_app.signals.notify_new_booking')
    def test_booking_creation_signal(self, mock_notify_new_booking):
        """Test that a signal is sent when a booking is created"""
        # Create a booking
        booking = Booking.objects.create(
            booking_id='12345678-1234-5678-1234-567812345678',
            user=self.customer,
            venue=self.venue,
            status='pending',
            total_price=100.00
        )

        # Check that the notify_new_booking function was called
        mock_notify_new_booking.assert_called_once_with(booking)

    @patch('notifications_app.signals.notify_booking_cancellation')
    def test_booking_cancellation_signal(self, mock_notify_booking_cancellation):
        """Test that a signal is sent when a booking is cancelled"""
        # Create a booking
        booking = Booking.objects.create(
            booking_id='12345678-1234-5678-1234-567812345678',
            user=self.customer,
            venue=self.venue,
            status='pending',
            total_price=100.00
        )

        # Reset the mock to clear the creation notification
        mock_notify_booking_cancellation.reset_mock()

        # Update the booking to cancelled
        booking._old_status = 'pending'  # Set the old status
        booking.status = 'cancelled'
        booking.save()

        # Check that the notify_booking_cancellation function was called
        mock_notify_booking_cancellation.assert_called_once_with(booking)

    @patch('notifications_app.signals.notify_booking_status_changed')
    def test_booking_status_change_signal(self, mock_notify_booking_status_changed):
        """Test that a signal is sent when a booking status changes"""
        # Create a booking
        booking = Booking.objects.create(
            booking_id='12345678-1234-5678-1234-567812345678',
            user=self.customer,
            venue=self.venue,
            status='pending',
            total_price=100.00
        )

        # Reset the mock to clear the creation notification
        mock_notify_booking_status_changed.reset_mock()

        # Update the booking to confirmed
        booking._old_status = 'pending'  # Set the old status
        booking.status = 'confirmed'
        booking.save()

        # Check that the notify_booking_status_changed function was called
        mock_notify_booking_status_changed.assert_called_once_with(booking, 'pending')


class ReviewSignalTest(TestCase):
    """Test the review signals"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_active=True,
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_active=True,
            is_service_provider=True
        )

        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            description='Test venue description',
            owner=self.provider
        )

        # Create notification category
        self.review_category = NotificationCategory.objects.create(
            name='Review',
            description='Review notifications'
        )

    @patch('notifications_app.signals.notify_new_review')
    def test_review_creation_signal(self, mock_notify_new_review):
        """Test that a signal is sent when a review is created"""
        # Create a review
        review = Review.objects.create(
            user=self.customer,
            venue=self.venue,
            rating=4,
            comment='Great service!'
        )

        # Check that the notify_new_review function was called
        mock_notify_new_review.assert_called_once_with(review)

    @patch('notifications_app.signals.notify_review_response')
    def test_review_response_signal(self, mock_notify_review_response):
        """Test that a signal is sent when a review response is created"""
        # Create a review
        review = Review.objects.create(
            user=self.customer,
            venue=self.venue,
            rating=4,
            comment='Great service!'
        )

        # Create a response
        response = ReviewResponse.objects.create(
            review=review,
            response_text='Thank you for your review!'
        )

        # Check that the notify_review_response function was called
        mock_notify_review_response.assert_called_once()
        args = mock_notify_review_response.call_args[0]
        self.assertEqual(args[0], review)
        self.assertEqual(args[1], response)


class ServiceProviderSignalTest(TestCase):
    """Test the service provider signals"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_active=True,
            is_service_provider=True
        )

        # Create notification category
        self.account_category = NotificationCategory.objects.create(
            name='Account',
            description='Account notifications'
        )

    @patch('notifications_app.signals.notify_service_provider_approval')
    def test_service_provider_approval_signal(self, mock_notify_service_provider_approval):
        """Test that a signal is sent when a service provider profile is created"""
        # Reset the mock to clear any calls from setup
        mock_notify_service_provider_approval.reset_mock()
        
        # Create a new service provider profile
        profile = ServiceProviderProfile.objects.create(
            user=self.provider
        )
        
        # Check that the notify_service_provider_approval function was called
        mock_notify_service_provider_approval.assert_called_once_with(profile)

    @patch('notifications_app.signals.notify_service_provider_rejection')
    def test_service_provider_rejection_signal(self, mock_notify_service_provider_rejection):
        """Test that a signal is sent when a service provider is rejected"""
        # Get the existing service provider profile
        profile = self.provider.provider_profile

        # Make sure it's in pending status
        profile.approval_status = 'pending'
        profile.save()

        # Reset the mock to clear any calls from creation
        mock_notify_service_provider_rejection.reset_mock()

        # Reject the service provider
        profile.approval_status = 'rejected'
        profile.rejection_reason = 'Incomplete information'
        profile.save()

        # Check that the notify_service_provider_rejection function was called
        mock_notify_service_provider_rejection.assert_called_once_with(profile, 'Incomplete information')
