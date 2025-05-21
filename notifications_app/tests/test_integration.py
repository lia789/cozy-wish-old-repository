from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)
from notifications_app.utils import create_notification, create_system_announcement
from booking_cart_app.models import Booking
from venues_app.models import Venue
from review_app.models import Review, ReviewResponse

User = get_user_model()


class NotificationIntegrationTest(TestCase):
    """Integration tests for the notifications_app"""
    
    def setUp(self):
        """Set up test data"""
        # Create client
        self.client = Client()
        
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
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            description='Test venue description',
            owner=self.provider
        )
        
        # Create notification categories
        self.booking_category = NotificationCategory.objects.create(
            name='Booking',
            description='Booking notifications',
            icon='fa-calendar',
            color='primary'
        )
        
        self.review_category = NotificationCategory.objects.create(
            name='Review',
            description='Review notifications',
            icon='fa-star',
            color='warning'
        )
        
        self.announcement_category = NotificationCategory.objects.create(
            name='Announcement',
            description='System announcements',
            icon='fa-bullhorn',
            color='info'
        )
    
    def test_booking_notification_flow(self):
        """Test the complete flow for booking notifications"""
        # Create a booking
        booking = Booking.objects.create(
            booking_id='12345678-1234-5678-1234-567812345678',
            user=self.customer,
            venue=self.venue,
            status='pending',
            total_price=100.00
        )
        
        # Check that notifications were created for both customer and provider
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__category=self.booking_category
        ).first()
        
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__category=self.booking_category
        ).first()
        
        self.assertIsNotNone(customer_notification)
        self.assertIsNotNone(provider_notification)
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # View notifications list
        response = self.client.get(reverse('notifications_app:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        
        # View notification detail
        response = self.client.get(
            reverse('notifications_app:notification_detail', args=[customer_notification.notification.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Check that the notification is now marked as read
        customer_notification.refresh_from_db()
        self.assertTrue(customer_notification.is_read)
        
        # Update booking status to cancelled
        booking.status = 'cancelled'
        booking.save()
        
        # Check that new notifications were created
        customer_notifications = UserNotification.objects.filter(
            user=self.customer,
            notification__category=self.booking_category,
            is_read=False
        )
        
        provider_notifications = UserNotification.objects.filter(
            user=self.provider,
            notification__category=self.booking_category,
            is_read=False
        )
        
        self.assertEqual(customer_notifications.count(), 1)
        self.assertEqual(provider_notifications.count(), 1)
        
        # View updated notifications list
        response = self.client.get(reverse('notifications_app:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].paginator.count, 1)  # Only unread
        
        # Mark all as read
        response = self.client.post(reverse('notifications_app:mark_all_notifications_read'))
        self.assertRedirects(response, reverse('notifications_app:notification_list'))
        
        # Check that all notifications are now read
        unread_count = UserNotification.objects.filter(
            user=self.customer,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)
    
    def test_review_notification_flow(self):
        """Test the complete flow for review notifications"""
        # Create a review
        review = Review.objects.create(
            user=self.customer,
            venue=self.venue,
            rating=4,
            comment='Great service!'
        )
        
        # Check that a notification was created for the provider
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__category=self.review_category
        ).first()
        
        self.assertIsNotNone(provider_notification)
        
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')
        
        # View notifications list
        response = self.client.get(reverse('notifications_app:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        
        # View notification detail
        response = self.client.get(
            reverse('notifications_app:notification_detail', args=[provider_notification.notification.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Check that the notification is now marked as read
        provider_notification.refresh_from_db()
        self.assertTrue(provider_notification.is_read)
        
        # Create a review response
        response = ReviewResponse.objects.create(
            review=review,
            response_text='Thank you for your review!'
        )
        
        # Check that a notification was created for the customer
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__category=self.review_category
        ).first()
        
        self.assertIsNotNone(customer_notification)
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # View notifications list
        response = self.client.get(reverse('notifications_app:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].paginator.count, 1)  # Only unread
    
    def test_notification_preferences_flow(self):
        """Test the complete flow for notification preferences"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # View preferences page
        response = self.client.get(reverse('notifications_app:notification_preferences'))
        self.assertEqual(response.status_code, 200)
        
        # Check that preferences were created for all categories
        self.assertEqual(len(response.context['preferences']), 3)  # 3 categories
        
        # Update preferences
        response = self.client.post(reverse('notifications_app:notification_preferences'), {
            f'preference_{self.booking_category.id}_channel': 'email',
            f'preference_{self.booking_category.id}_is_enabled': 'on',
            f'preference_{self.review_category.id}_channel': 'none',
            f'preference_{self.review_category.id}_is_enabled': '',  # Unchecked
            f'preference_{self.announcement_category.id}_channel': 'both',
            f'preference_{self.announcement_category.id}_is_enabled': 'on'
        })
        
        # Should redirect to preferences page
        self.assertRedirects(response, reverse('notifications_app:notification_preferences'))
        
        # Check that the preferences were updated
        booking_pref = NotificationPreference.objects.get(
            user=self.customer,
            category=self.booking_category
        )
        self.assertEqual(booking_pref.channel, 'email')
        self.assertTrue(booking_pref.is_enabled)
        
        review_pref = NotificationPreference.objects.get(
            user=self.customer,
            category=self.review_category
        )
        self.assertEqual(review_pref.channel, 'none')
        self.assertFalse(review_pref.is_enabled)
        
        # Create a new review (should not create a notification due to preferences)
        review = Review.objects.create(
            user=self.provider,  # Provider reviewing customer's venue (hypothetical)
            venue=self.venue,    # Just for testing
            rating=5,
            comment='Excellent customer!'
        )
        
        # Check that no notification was created for the customer
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__category=self.review_category
        ).first()
        
        self.assertIsNone(customer_notification)
    
    def test_admin_notification_flow(self):
        """Test the complete flow for admin notifications"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # View admin dashboard
        response = self.client.get(reverse('notifications_app:admin_notification_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Create a system announcement
        response = self.client.post(reverse('notifications_app:admin_create_announcement'), {
            'title': 'System Maintenance',
            'message': 'The system will be down for maintenance on Saturday.',
            'priority': 'medium',
            'expires_in_days': 7
        })
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('notifications_app:admin_notification_dashboard'))
        
        # Check that the announcement was created
        announcement = Notification.objects.filter(
            title='System Maintenance',
            is_system_wide=True
        ).first()
        
        self.assertIsNotNone(announcement)
        
        # View admin notification list
        response = self.client.get(reverse('notifications_app:admin_notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        
        # View notification detail
        response = self.client.get(
            reverse('notifications_app:admin_notification_detail', args=[announcement.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Deactivate the notification
        response = self.client.post(
            reverse('notifications_app:admin_deactivate_notification', args=[announcement.id])
        )
        
        # Should redirect to admin notification list
        self.assertRedirects(response, reverse('notifications_app:admin_notification_list'))
        
        # Check that the notification is now inactive
        announcement.refresh_from_db()
        self.assertFalse(announcement.is_active)
    
    def test_notification_dropdown_flow(self):
        """Test the notification dropdown flow"""
        # Create notifications for the customer
        for i in range(3):
            create_notification(
                category_name='Booking',
                title=f'Notification {i}',
                message=f'This is notification {i}',
                users=[self.customer],
                priority='medium'
            )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get unread notifications via AJAX
        response = self.client.get(
            reverse('notifications_app:get_unread_notifications'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['unread_count'], 3)
        self.assertEqual(len(data['notifications']), 3)
        
        # Mark all as read via AJAX
        response = self.client.post(
            reverse('notifications_app:mark_all_notifications_read'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)
        self.assertEqual(data['unread_count'], 0)
        
        # Get unread notifications again (should be empty)
        response = self.client.get(
            reverse('notifications_app:get_unread_notifications'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['unread_count'], 0)
        self.assertEqual(len(data['notifications']), 0)
