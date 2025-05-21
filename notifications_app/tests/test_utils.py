from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, MagicMock
from datetime import timedelta

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)
from notifications_app.utils import (
    create_notification, should_notify_user, send_notification_email,
    get_user_notifications, get_unread_count, mark_all_as_read,
    create_system_announcement, notify_new_booking, notify_booking_cancellation,
    notify_new_review, notify_review_response, notify_service_provider_approval,
    notify_service_provider_rejection, notify_booking_status_changed
)
from venues_app.models import Venue
from booking_cart_app.models import Booking
from review_app.models import Review, ReviewResponse
from accounts_app.models import ServiceProviderProfile

User = get_user_model()


class NotificationUtilsBaseTest(TestCase):
    """Base class for notification utils tests"""
    
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
        
        # Create service provider profile
        self.provider_profile = ServiceProviderProfile.objects.create(
            user=self.provider,
            business_name='Test Business',
            business_description='Test description',
            is_approved=True
        )
        
        # Create notification categories
        self.booking_category = NotificationCategory.objects.create(
            name='Booking',
            description='Booking notifications'
        )
        
        self.review_category = NotificationCategory.objects.create(
            name='Review',
            description='Review notifications'
        )
        
        self.account_category = NotificationCategory.objects.create(
            name='Account',
            description='Account notifications'
        )
        
        self.announcement_category = NotificationCategory.objects.create(
            name='Announcement',
            description='System announcements'
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            description='Test venue description',
            owner=self.provider
        )


class CreateNotificationTest(NotificationUtilsBaseTest):
    """Test the create_notification utility function"""
    
    def test_create_notification_basic(self):
        """Test creating a basic notification"""
        notification = create_notification(
            category_name='Booking',
            title='Test Notification',
            message='This is a test notification',
            users=[self.customer],
            priority='medium'
        )
        
        # Check notification was created correctly
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.category, self.booking_category)
        self.assertEqual(notification.priority, 'medium')
        self.assertFalse(notification.is_system_wide)
        
        # Check user notification was created
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=notification
        )
        self.assertFalse(user_notification.is_read)
    
    def test_create_notification_multiple_users(self):
        """Test creating a notification for multiple users"""
        notification = create_notification(
            category_name='Booking',
            title='Multi-User Notification',
            message='This notification is for multiple users',
            users=[self.customer, self.provider],
            priority='high'
        )
        
        # Check user notifications were created for both users
        self.assertTrue(
            UserNotification.objects.filter(
                user=self.customer,
                notification=notification
            ).exists()
        )
        
        self.assertTrue(
            UserNotification.objects.filter(
                user=self.provider,
                notification=notification
            ).exists()
        )
    
    def test_create_notification_with_related_object(self):
        """Test creating a notification with a related object"""
        notification = create_notification(
            category_name='Booking',
            title='Venue Notification',
            message='This notification is related to a venue',
            users=[self.customer],
            priority='low',
            related_object=self.venue
        )
        
        # Check related object was set correctly
        self.assertEqual(notification.content_object, self.venue)
        self.assertEqual(
            notification.content_type,
            ContentType.objects.get_for_model(Venue)
        )
        self.assertEqual(notification.object_id, self.venue.id)
    
    def test_create_notification_with_expiry(self):
        """Test creating a notification with an expiry date"""
        expires_at = timezone.now() + timedelta(days=7)
        
        notification = create_notification(
            category_name='Booking',
            title='Expiring Notification',
            message='This notification will expire',
            users=[self.customer],
            priority='medium',
            expires_at=expires_at
        )
        
        # Check expiry date was set correctly
        self.assertEqual(notification.expires_at, expires_at)
    
    def test_create_notification_system_wide(self):
        """Test creating a system-wide notification"""
        notification = create_notification(
            category_name='Announcement',
            title='System Announcement',
            message='This is a system-wide announcement',
            priority='high',
            is_system_wide=True
        )
        
        # Check system-wide flag was set correctly
        self.assertTrue(notification.is_system_wide)
    
    def test_create_notification_new_category(self):
        """Test creating a notification with a new category"""
        notification = create_notification(
            category_name='New Category',
            title='New Category Notification',
            message='This notification has a new category',
            users=[self.customer],
            priority='medium'
        )
        
        # Check new category was created
        self.assertTrue(
            NotificationCategory.objects.filter(name='New Category').exists()
        )
        
        # Check notification uses the new category
        new_category = NotificationCategory.objects.get(name='New Category')
        self.assertEqual(notification.category, new_category)
    
    @patch('notifications_app.utils.send_notification_email')
    def test_create_notification_respects_preferences(self, mock_send_email):
        """Test that notification creation respects user preferences"""
        # Create a preference to disable notifications for this category
        NotificationPreference.objects.create(
            user=self.customer,
            category=self.booking_category,
            channel='none',
            is_enabled=False
        )
        
        # Create a notification
        notification = create_notification(
            category_name='Booking',
            title='Ignored Notification',
            message='This notification should be ignored',
            users=[self.customer],
            priority='medium'
        )
        
        # Check that no user notification was created
        self.assertFalse(
            UserNotification.objects.filter(
                user=self.customer,
                notification=notification
            ).exists()
        )
        
        # Check that no email was sent
        mock_send_email.assert_not_called()


class ShouldNotifyUserTest(NotificationUtilsBaseTest):
    """Test the should_notify_user utility function"""
    
    def test_should_notify_user_default(self):
        """Test default notification behavior (no preferences set)"""
        # By default, users should be notified
        self.assertTrue(should_notify_user(self.customer, self.booking_category, 'in_app'))
        self.assertTrue(should_notify_user(self.customer, self.booking_category, 'email'))
    
    def test_should_notify_user_with_preferences(self):
        """Test notification behavior with preferences set"""
        # Create preferences
        NotificationPreference.objects.create(
            user=self.customer,
            category=self.booking_category,
            channel='in_app',  # Only in-app, not email
            is_enabled=True
        )
        
        NotificationPreference.objects.create(
            user=self.customer,
            category=self.review_category,
            channel='both',  # Both in-app and email
            is_enabled=True
        )
        
        NotificationPreference.objects.create(
            user=self.customer,
            category=self.account_category,
            channel='email',  # Only email, not in-app
            is_enabled=True
        )
        
        NotificationPreference.objects.create(
            user=self.customer,
            category=self.announcement_category,
            channel='none',  # No notifications
            is_enabled=False
        )
        
        # Check in-app notifications
        self.assertTrue(should_notify_user(self.customer, self.booking_category, 'in_app'))
        self.assertTrue(should_notify_user(self.customer, self.review_category, 'in_app'))
        self.assertFalse(should_notify_user(self.customer, self.account_category, 'in_app'))
        self.assertFalse(should_notify_user(self.customer, self.announcement_category, 'in_app'))
        
        # Check email notifications
        self.assertFalse(should_notify_user(self.customer, self.booking_category, 'email'))
        self.assertTrue(should_notify_user(self.customer, self.review_category, 'email'))
        self.assertTrue(should_notify_user(self.customer, self.account_category, 'email'))
        self.assertFalse(should_notify_user(self.customer, self.announcement_category, 'email'))


class SendNotificationEmailTest(NotificationUtilsBaseTest):
    """Test the send_notification_email utility function"""
    
    @patch('notifications_app.utils.send_mail')
    def test_send_notification_email(self, mock_send_mail):
        """Test sending a notification email"""
        # Create a notification
        notification = Notification.objects.create(
            category=self.booking_category,
            title='Email Notification',
            message='This is a notification that should be emailed',
            priority='medium'
        )
        
        # Send the email
        result = send_notification_email(self.customer, notification)
        
        # Check that send_mail was called with the correct arguments
        mock_send_mail.assert_called_once()
        args = mock_send_mail.call_args[0]
        
        self.assertEqual(args[0], 'CozyWish: Email Notification')  # Subject
        self.assertIn('This is a notification that should be emailed', args[1])  # Message
        self.assertEqual(args[3], [self.customer.email])  # Recipient
        
        # Check that the function returned True (success)
        self.assertTrue(result)
    
    @patch('notifications_app.utils.send_mail', side_effect=Exception('Test exception'))
    def test_send_notification_email_failure(self, mock_send_mail):
        """Test handling of email sending failures"""
        # Create a notification
        notification = Notification.objects.create(
            category=self.booking_category,
            title='Failed Email',
            message='This email should fail to send',
            priority='medium'
        )
        
        # Try to send the email (should fail)
        result = send_notification_email(self.customer, notification)
        
        # Check that send_mail was called
        mock_send_mail.assert_called_once()
        
        # Check that the function returned False (failure)
        self.assertFalse(result)


class GetUserNotificationsTest(NotificationUtilsBaseTest):
    """Test the get_user_notifications utility function"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create notifications for the customer
        self.notification1 = create_notification(
            category_name='Booking',
            title='Notification 1',
            message='This is notification 1',
            users=[self.customer],
            priority='low'
        )
        
        self.notification2 = create_notification(
            category_name='Review',
            title='Notification 2',
            message='This is notification 2',
            users=[self.customer],
            priority='medium'
        )
        
        self.notification3 = create_notification(
            category_name='Account',
            title='Notification 3',
            message='This is notification 3',
            users=[self.customer],
            priority='high'
        )
        
        # Create a notification for the provider
        self.notification4 = create_notification(
            category_name='Booking',
            title='Provider Notification',
            message='This is a notification for the provider',
            users=[self.provider],
            priority='medium'
        )
        
        # Mark notification1 as read
        user_notification1 = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        user_notification1.mark_as_read()
        
        # Mark notification3 as deleted
        user_notification3 = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification3
        )
        user_notification3.delete_notification()
    
    def test_get_user_notifications_unread_only(self):
        """Test getting only unread notifications for a user"""
        notifications = get_user_notifications(self.customer, include_read=False)
        
        # Should only include notification2 (unread and not deleted)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications[0].notification, self.notification2)
    
    def test_get_user_notifications_include_read(self):
        """Test getting both read and unread notifications for a user"""
        notifications = get_user_notifications(self.customer, include_read=True)
        
        # Should include notification1 (read) and notification2 (unread)
        self.assertEqual(notifications.count(), 2)
        
        # Check that both notifications are included
        notification_ids = [n.notification.id for n in notifications]
        self.assertIn(self.notification1.id, notification_ids)
        self.assertIn(self.notification2.id, notification_ids)
    
    def test_get_user_notifications_include_deleted(self):
        """Test getting deleted notifications for a user"""
        notifications = get_user_notifications(
            self.customer,
            include_read=True,
            include_deleted=True
        )
        
        # Should include all three notifications
        self.assertEqual(notifications.count(), 3)
        
        # Check that all notifications are included
        notification_ids = [n.notification.id for n in notifications]
        self.assertIn(self.notification1.id, notification_ids)
        self.assertIn(self.notification2.id, notification_ids)
        self.assertIn(self.notification3.id, notification_ids)
    
    def test_get_user_notifications_ordering(self):
        """Test that notifications are ordered by created_at in descending order"""
        notifications = get_user_notifications(
            self.customer,
            include_read=True,
            include_deleted=True
        )
        
        # Notifications should be ordered by created_at in descending order
        self.assertEqual(notifications[0].notification, self.notification3)
        self.assertEqual(notifications[1].notification, self.notification2)
        self.assertEqual(notifications[2].notification, self.notification1)


class GetUnreadCountTest(NotificationUtilsBaseTest):
    """Test the get_unread_count utility function"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create notifications for the customer
        for i in range(5):
            create_notification(
                category_name='Booking',
                title=f'Notification {i}',
                message=f'This is notification {i}',
                users=[self.customer],
                priority='medium'
            )
        
        # Mark 2 notifications as read
        user_notifications = UserNotification.objects.filter(user=self.customer)[:2]
        for un in user_notifications:
            un.mark_as_read()
        
        # Mark 1 notification as deleted
        user_notification = UserNotification.objects.filter(user=self.customer)[2]
        user_notification.delete_notification()
    
    def test_get_unread_count(self):
        """Test getting the count of unread notifications"""
        # Should be 2 unread notifications (5 total - 2 read - 1 deleted)
        count = get_unread_count(self.customer)
        self.assertEqual(count, 2)


class MarkAllAsReadTest(NotificationUtilsBaseTest):
    """Test the mark_all_as_read utility function"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create notifications for the customer
        for i in range(5):
            create_notification(
                category_name='Booking',
                title=f'Notification {i}',
                message=f'This is notification {i}',
                users=[self.customer],
                priority='medium'
            )
        
        # Create notifications for the provider
        for i in range(3):
            create_notification(
                category_name='Booking',
                title=f'Provider Notification {i}',
                message=f'This is provider notification {i}',
                users=[self.provider],
                priority='medium'
            )
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read for a user"""
        # Initially all notifications are unread
        unread_before = UserNotification.objects.filter(
            user=self.customer,
            is_read=False
        ).count()
        self.assertEqual(unread_before, 5)
        
        # Mark all as read
        count = mark_all_as_read(self.customer)
        
        # Check that all notifications are now read
        unread_after = UserNotification.objects.filter(
            user=self.customer,
            is_read=False
        ).count()
        self.assertEqual(unread_after, 0)
        self.assertEqual(count, 5)
        
        # Check that provider's notifications are still unread
        provider_unread = UserNotification.objects.filter(
            user=self.provider,
            is_read=False
        ).count()
        self.assertEqual(provider_unread, 3)


class CreateSystemAnnouncementTest(NotificationUtilsBaseTest):
    """Test the create_system_announcement utility function"""
    
    def test_create_system_announcement(self):
        """Test creating a system-wide announcement"""
        announcement = create_system_announcement(
            title='System Announcement',
            message='This is a system-wide announcement',
            expires_in_days=7
        )
        
        # Check announcement properties
        self.assertEqual(announcement.title, 'System Announcement')
        self.assertEqual(announcement.message, 'This is a system-wide announcement')
        self.assertEqual(announcement.category.name, 'Announcement')
        self.assertTrue(announcement.is_system_wide)
        
        # Check expiry date (should be ~7 days from now)
        now = timezone.now()
        self.assertIsNotNone(announcement.expires_at)
        
        # Allow for a small time difference due to test execution time
        expiry_delta = announcement.expires_at - now
        self.assertGreaterEqual(expiry_delta.days, 6)
        self.assertLessEqual(expiry_delta.days, 7)


class NotificationEventTest(NotificationUtilsBaseTest):
    """Test the notification event utility functions"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create a booking
        self.booking = Booking.objects.create(
            booking_id='12345678-1234-5678-1234-567812345678',
            user=self.customer,
            venue=self.venue,
            status='pending',
            total_price=100.00
        )
        
        # Create a review
        self.review = Review.objects.create(
            user=self.customer,
            venue=self.venue,
            rating=4,
            comment='Great service!'
        )
        
        # Create a review response
        self.response = ReviewResponse.objects.create(
            review=self.review,
            response_text='Thank you for your review!'
        )
    
    def test_notify_new_booking(self):
        """Test notification for a new booking"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Trigger notification
        notify_new_booking(self.booking)
        
        # Check that notifications were created for both customer and provider
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__title__contains='Booking Confirmed'
        ).first()
        
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__title__contains='New Booking Received'
        ).first()
        
        self.assertIsNotNone(customer_notification)
        self.assertIsNotNone(provider_notification)
        
        # Check notification content
        self.assertIn(str(self.booking.booking_id), customer_notification.notification.message)
        self.assertIn(str(self.booking.booking_id), provider_notification.notification.message)
        
        # Check related object
        self.assertEqual(
            customer_notification.notification.content_object,
            self.booking
        )
        self.assertEqual(
            provider_notification.notification.content_object,
            self.booking
        )
    
    def test_notify_booking_cancellation(self):
        """Test notification for a booking cancellation"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Update booking status
        self.booking.status = 'cancelled'
        self.booking.save()
        
        # Trigger notification
        notify_booking_cancellation(self.booking)
        
        # Check that notifications were created for both customer and provider
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__title__contains='Booking Cancelled'
        ).first()
        
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__title__contains='Booking Cancelled'
        ).first()
        
        self.assertIsNotNone(customer_notification)
        self.assertIsNotNone(provider_notification)
    
    def test_notify_new_review(self):
        """Test notification for a new review"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Trigger notification
        notify_new_review(self.review)
        
        # Check that notification was created for the provider
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__title__contains='New Review Received'
        ).first()
        
        self.assertIsNotNone(provider_notification)
        self.assertIn('4-star review', provider_notification.notification.message)
    
    def test_notify_review_response(self):
        """Test notification for a review response"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Trigger notification
        notify_review_response(self.review, self.response)
        
        # Check that notification was created for the customer
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__title__contains='Response to Your Review'
        ).first()
        
        self.assertIsNotNone(customer_notification)
        self.assertIn(self.venue.name, customer_notification.notification.message)
    
    def test_notify_service_provider_approval(self):
        """Test notification for service provider approval"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Trigger notification
        notify_service_provider_approval(self.provider_profile)
        
        # Check that notification was created for the provider
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__title__contains='Account Approved'
        ).first()
        
        self.assertIsNotNone(provider_notification)
        self.assertIn('approved', provider_notification.notification.message)
    
    def test_notify_service_provider_rejection(self):
        """Test notification for service provider rejection"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Trigger notification
        notify_service_provider_rejection(self.provider_profile, 'Incomplete information')
        
        # Check that notification was created for the provider
        provider_notification = UserNotification.objects.filter(
            user=self.provider,
            notification__title__contains='Account Not Approved'
        ).first()
        
        self.assertIsNotNone(provider_notification)
        self.assertIn('not approved', provider_notification.notification.message)
        self.assertIn('Incomplete information', provider_notification.notification.message)
    
    def test_notify_booking_status_changed(self):
        """Test notification for booking status change"""
        # Clear existing notifications
        Notification.objects.all().delete()
        UserNotification.objects.all().delete()
        
        # Update booking status
        old_status = 'pending'
        self.booking.status = 'confirmed'
        self.booking.save()
        
        # Trigger notification
        notify_booking_status_changed(self.booking, old_status)
        
        # Check that notification was created for the customer
        customer_notification = UserNotification.objects.filter(
            user=self.customer,
            notification__title__contains='Booking Status Updated'
        ).first()
        
        self.assertIsNotNone(customer_notification)
        self.assertIn(str(self.booking.booking_id), customer_notification.notification.message)
        self.assertIn('confirmed', customer_notification.notification.message)
