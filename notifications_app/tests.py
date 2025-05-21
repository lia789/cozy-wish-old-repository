from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from .models import NotificationCategory, Notification, UserNotification, NotificationPreference
from .utils import create_notification, get_user_notifications, mark_all_as_read, create_system_announcement

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            is_active=True
        )

        # Create a notification category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description',
            icon='fa-bell',
            color='primary'
        )

        # Set dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)

    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium',
            created_at=self.now,
            expires_at=self.tomorrow
        )

        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.priority, 'medium')
        self.assertEqual(notification.category, self.category)
        self.assertFalse(notification.is_expired())

    def test_notification_expiration(self):
        """Test notification expiration"""
        # Create an expired notification
        expired_notification = Notification.objects.create(
            category=self.category,
            title='Expired Notification',
            message='This notification has expired',
            priority='low',
            created_at=self.yesterday - timedelta(days=1),
            expires_at=self.yesterday
        )

        # Create a non-expired notification
        active_notification = Notification.objects.create(
            category=self.category,
            title='Active Notification',
            message='This notification is still active',
            priority='high',
            created_at=self.now,
            expires_at=self.tomorrow
        )

        # Create a notification with no expiration
        no_expiry_notification = Notification.objects.create(
            category=self.category,
            title='No Expiry Notification',
            message='This notification never expires',
            priority='medium',
            created_at=self.now,
            expires_at=None
        )

        self.assertTrue(expired_notification.is_expired())
        self.assertFalse(active_notification.is_expired())
        self.assertFalse(no_expiry_notification.is_expired())

    def test_user_notification_creation(self):
        """Test creating a user notification"""
        notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        user_notification = UserNotification.objects.create(
            user=self.user,
            notification=notification
        )

        self.assertEqual(user_notification.user, self.user)
        self.assertEqual(user_notification.notification, notification)
        self.assertFalse(user_notification.is_read)
        self.assertIsNone(user_notification.read_at)
        self.assertFalse(user_notification.is_deleted)
        self.assertIsNone(user_notification.deleted_at)

    def test_mark_as_read(self):
        """Test marking a notification as read"""
        notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        user_notification = UserNotification.objects.create(
            user=self.user,
            notification=notification
        )

        # Mark as read
        user_notification.mark_as_read()

        # Refresh from database
        user_notification.refresh_from_db()

        self.assertTrue(user_notification.is_read)
        self.assertIsNotNone(user_notification.read_at)

    def test_mark_as_unread(self):
        """Test marking a notification as unread"""
        notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        user_notification = UserNotification.objects.create(
            user=self.user,
            notification=notification,
            is_read=True,
            read_at=self.now
        )

        # Mark as unread
        user_notification.mark_as_unread()

        # Refresh from database
        user_notification.refresh_from_db()

        self.assertFalse(user_notification.is_read)
        self.assertIsNone(user_notification.read_at)

    def test_delete_notification(self):
        """Test soft deleting a notification"""
        notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        user_notification = UserNotification.objects.create(
            user=self.user,
            notification=notification
        )

        # Delete notification
        user_notification.delete_notification()

        # Refresh from database
        user_notification.refresh_from_db()

        self.assertTrue(user_notification.is_deleted)
        self.assertIsNotNone(user_notification.deleted_at)

    def test_notification_preference_creation(self):
        """Test creating a notification preference"""
        preference = NotificationPreference.objects.create(
            user=self.user,
            category=self.category,
            channel='both',
            is_enabled=True
        )

        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.category, self.category)
        self.assertEqual(preference.channel, 'both')
        self.assertTrue(preference.is_enabled)


class NotificationUtilsTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            is_active=True
        )

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            is_active=True
        )

        # Create notification categories
        self.category1 = NotificationCategory.objects.create(
            name='Test Category 1',
            description='Test description 1'
        )

        self.category2 = NotificationCategory.objects.create(
            name='Test Category 2',
            description='Test description 2'
        )

    def test_create_notification(self):
        """Test creating a notification with the utility function"""
        notification = create_notification(
            category_name='Test Category 1',
            title='Test Notification',
            message='This is a test notification',
            users=[self.user1, self.user2],
            priority='medium'
        )

        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.category, self.category1)

        # Check that user notifications were created
        user_notifications = UserNotification.objects.filter(notification=notification)
        self.assertEqual(user_notifications.count(), 2)

        # Check that both users received the notification
        self.assertTrue(UserNotification.objects.filter(user=self.user1, notification=notification).exists())
        self.assertTrue(UserNotification.objects.filter(user=self.user2, notification=notification).exists())

    def test_get_user_notifications(self):
        """Test getting user notifications"""
        # Create notifications for user1
        notification1 = create_notification(
            category_name='Test Category 1',
            title='Notification 1',
            message='This is notification 1',
            users=[self.user1],
            priority='low'
        )

        notification2 = create_notification(
            category_name='Test Category 2',
            title='Notification 2',
            message='This is notification 2',
            users=[self.user1],
            priority='high'
        )

        # Create a notification for user2
        notification3 = create_notification(
            category_name='Test Category 1',
            title='Notification 3',
            message='This is notification 3',
            users=[self.user2],
            priority='medium'
        )

        # Mark notification1 as read
        user_notification1 = UserNotification.objects.get(user=self.user1, notification=notification1)
        user_notification1.mark_as_read()

        # Get unread notifications for user1
        unread_notifications = get_user_notifications(self.user1, include_read=False)
        self.assertEqual(unread_notifications.count(), 1)
        self.assertEqual(unread_notifications[0].notification, notification2)

        # Get all notifications for user1
        all_notifications = get_user_notifications(self.user1, include_read=True)
        self.assertEqual(all_notifications.count(), 2)

    def test_mark_all_as_read(self):
        """Test marking all notifications as read"""
        # Create multiple notifications for user1
        for i in range(5):
            create_notification(
                category_name='Test Category 1',
                title=f'Notification {i}',
                message=f'This is notification {i}',
                users=[self.user1],
                priority='medium'
            )

        # Check that all notifications are unread
        unread_count_before = UserNotification.objects.filter(user=self.user1, is_read=False).count()
        self.assertEqual(unread_count_before, 5)

        # Mark all as read
        count = mark_all_as_read(self.user1)

        # Check that all notifications are now read
        unread_count_after = UserNotification.objects.filter(user=self.user1, is_read=False).count()
        self.assertEqual(unread_count_after, 0)
        self.assertEqual(count, 5)

    def test_create_system_announcement(self):
        """Test creating a system-wide announcement"""
        announcement = create_system_announcement(
            title='System Announcement',
            message='This is a system-wide announcement',
            expires_in_days=7
        )

        self.assertEqual(announcement.title, 'System Announcement')
        self.assertEqual(announcement.message, 'This is a system-wide announcement')
        self.assertEqual(announcement.category.name, 'Announcement')
        self.assertTrue(announcement.is_system_wide)
        self.assertIsNotNone(announcement.expires_at)


class NotificationViewTests(TestCase):
    def setUp(self):
        # Create a client
        self.client = Client()

        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password123',
            is_active=True
        )

        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='password123',
            is_active=True,
            is_staff=True
        )

        # Create notification categories
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )

        # Create notifications for the user
        self.notification1 = create_notification(
            category_name='Test Category',
            title='Notification 1',
            message='This is notification 1',
            users=[self.user],
            priority='medium'
        )

        self.notification2 = create_notification(
            category_name='Test Category',
            title='Notification 2',
            message='This is notification 2',
            users=[self.user],
            priority='high'
        )

        # Create a system announcement
        self.announcement = create_system_announcement(
            title='System Announcement',
            message='This is a system-wide announcement',
            expires_in_days=7
        )

    def test_notification_list_view(self):
        """Test the notification list view"""
        # Login as user
        self.client.login(username='user@example.com', password='password123')

        # Access the notification list view
        response = self.client.get(reverse('notifications_app:notification_list'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the notifications are in the context
        self.assertIn('notifications', response.context)
        self.assertEqual(response.context['notifications'].paginator.count, 2)

    def test_notification_detail_view(self):
        """Test the notification detail view"""
        # Login as user
        self.client.login(username='user@example.com', password='password123')

        # Get the user notification
        user_notification = UserNotification.objects.get(user=self.user, notification=self.notification1)

        # Access the notification detail view
        response = self.client.get(reverse('notifications_app:notification_detail', args=[self.notification1.id]))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the notification is in the context
        self.assertIn('notification', response.context)
        self.assertEqual(response.context['notification'].notification, self.notification1)

        # Check that the notification is marked as read
        user_notification.refresh_from_db()
        self.assertTrue(user_notification.is_read)

    def test_mark_notification_read(self):
        """Test marking a notification as read"""
        # Login as user
        self.client.login(username='user@example.com', password='password123')

        # Get the user notification
        user_notification = UserNotification.objects.get(user=self.user, notification=self.notification1)

        # Make sure it's unread
        user_notification.is_read = False
        user_notification.read_at = None
        user_notification.save()

        # Mark as read
        response = self.client.post(reverse('notifications_app:mark_notification_read', args=[self.notification1.id]))

        # Check that the response redirects to the notification list
        self.assertRedirects(response, reverse('notifications_app:notification_list'))

        # Check that the notification is marked as read
        user_notification.refresh_from_db()
        self.assertTrue(user_notification.is_read)
        self.assertIsNotNone(user_notification.read_at)

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Login as user
        self.client.login(username='user@example.com', password='password123')

        # Make sure all notifications are unread
        UserNotification.objects.filter(user=self.user).update(is_read=False, read_at=None)

        # Mark all as read
        response = self.client.post(reverse('notifications_app:mark_all_notifications_read'))

        # Check that the response redirects to the notification list
        self.assertRedirects(response, reverse('notifications_app:notification_list'))

        # Check that all notifications are marked as read
        unread_count = UserNotification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)

    def test_notification_preferences_view(self):
        """Test the notification preferences view"""
        # Login as user
        self.client.login(username='user@example.com', password='password123')

        # Access the notification preferences view
        response = self.client.get(reverse('notifications_app:notification_preferences'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the preferences are in the context
        self.assertIn('preferences', response.context)
        self.assertEqual(len(response.context['preferences']), 1)  # One category

        # Check that a preference was created for the user
        preference = NotificationPreference.objects.get(user=self.user, category=self.category)
        self.assertEqual(preference.channel, 'both')  # Default value
        self.assertTrue(preference.is_enabled)  # Default value

    def test_admin_notification_dashboard(self):
        """Test the admin notification dashboard"""
        # Login as admin
        self.client.login(username='admin@example.com', password='password123')

        # Access the admin notification dashboard
        response = self.client.get(reverse('notifications_app:admin_notification_dashboard'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the dashboard data is in the context
        self.assertIn('total_notifications', response.context)
        self.assertIn('active_notifications', response.context)
        self.assertIn('system_wide_notifications', response.context)
        self.assertIn('active_announcements', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('recent_notifications', response.context)

    def test_admin_create_announcement(self):
        """Test creating a system announcement"""
        # Login as admin
        self.client.login(username='admin@example.com', password='password123')

        # Get the form
        response = self.client.get(reverse('notifications_app:admin_create_announcement'))
        self.assertEqual(response.status_code, 200)

        # Submit the form
        response = self.client.post(reverse('notifications_app:admin_create_announcement'), {
            'title': 'New Announcement',
            'message': 'This is a new system-wide announcement',
            'priority': 'high',
            'expires_in_days': 14
        })

        # Check that the response redirects to the dashboard
        self.assertRedirects(response, reverse('notifications_app:admin_notification_dashboard'))

        # Check that the announcement was created
        self.assertTrue(Notification.objects.filter(title='New Announcement', is_system_wide=True).exists())
