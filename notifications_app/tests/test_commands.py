from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import StringIO
from datetime import timedelta

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification
)

User = get_user_model()


class ImportNotificationsDummyDataCommandTest(TestCase):
    """Test the import_notifications_dummy_data management command"""

    def setUp(self):
        """Set up test data"""
        # Create users for testing
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            is_active=True
        )

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            is_active=True
        )

    def test_import_notifications_dummy_data(self):
        """Test importing notification dummy data"""
        # Capture command output
        out = StringIO()

        # Run the command
        call_command('import_notifications_dummy_data', stdout=out)

        # Check that data was loaded
        self.assertTrue(NotificationCategory.objects.exists())
        self.assertTrue(Notification.objects.exists())

        # Check command output
        output = out.getvalue()
        self.assertIn('Successfully imported notification dummy data', output)

    def test_import_notifications_dummy_data_clear(self):
        """Test importing notification dummy data with clear option"""
        # Create some initial data
        category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )

        notification = Notification.objects.create(
            category=category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        # Capture command output
        out = StringIO()

        # Run the command with clear option
        call_command('import_notifications_dummy_data', '--clear', stdout=out)

        # Check that initial data was cleared and new data was loaded
        self.assertFalse(Notification.objects.filter(id=notification.id).exists())
        self.assertFalse(NotificationCategory.objects.filter(id=category.id).exists())
        self.assertTrue(NotificationCategory.objects.exists())
        self.assertTrue(Notification.objects.exists())

        # Check command output
        output = out.getvalue()
        self.assertIn('Cleared existing notification data', output)
        self.assertIn('Successfully imported notification dummy data', output)


class LoadNotificationTestDataCommandTest(TestCase):
    """Test the load_notification_test_data management command"""

    def setUp(self):
        """Set up test data"""
        # Create users for testing
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            is_active=True
        )

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            is_active=True
        )

    def test_load_notification_test_data(self):
        """Test loading notification test data"""
        # Capture command output
        out = StringIO()

        # Run the command
        call_command('load_notification_test_data', stdout=out)

        # Check that data was loaded
        self.assertTrue(NotificationCategory.objects.exists())
        self.assertTrue(Notification.objects.exists())

        # Check command output
        output = out.getvalue()
        self.assertIn('Successfully loaded test data', output)

    def test_load_notification_test_data_clear(self):
        """Test loading notification test data with clear option"""
        # Create some initial data
        category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )

        notification = Notification.objects.create(
            category=category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )

        # Capture command output
        out = StringIO()

        # Run the command with clear option
        call_command('load_notification_test_data', '--clear', stdout=out)

        # Check that initial data was cleared and new data was loaded
        self.assertFalse(Notification.objects.filter(id=notification.id).exists())
        self.assertFalse(NotificationCategory.objects.filter(id=category.id).exists())
        self.assertTrue(NotificationCategory.objects.exists())
        self.assertTrue(Notification.objects.exists())

        # Check command output
        output = out.getvalue()
        self.assertIn('Cleared existing data', output)
        self.assertIn('Successfully loaded test data', output)


class CleanExpiredNotificationsCommandTest(TestCase):
    """Test the clean_expired_notifications management command"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True
        )

        # Create notification category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )

        # Set dates
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.last_week = self.now - timedelta(days=7)
        self.last_month = self.now - timedelta(days=30)

        # Create expired notifications
        self.expired1 = Notification.objects.create(
            category=self.category,
            title='Expired Notification 1',
            message='This notification expired yesterday',
            priority='low',
            created_at=self.last_week,
            expires_at=self.yesterday
        )

        self.expired2 = Notification.objects.create(
            category=self.category,
            title='Expired Notification 2',
            message='This notification expired last week',
            priority='medium',
            created_at=self.last_month,
            expires_at=self.last_week
        )

        # Create active notification
        self.active = Notification.objects.create(
            category=self.category,
            title='Active Notification',
            message='This notification is still active',
            priority='high',
            created_at=self.now,
            expires_at=self.now + timedelta(days=7)
        )

        # Create notification with no expiry
        self.no_expiry = Notification.objects.create(
            category=self.category,
            title='No Expiry Notification',
            message='This notification never expires',
            priority='medium',
            created_at=self.now,
            expires_at=None
        )

        # Create user notifications
        UserNotification.objects.create(
            user=self.user,
            notification=self.expired1
        )

        UserNotification.objects.create(
            user=self.user,
            notification=self.expired2
        )

        UserNotification.objects.create(
            user=self.user,
            notification=self.active
        )

        UserNotification.objects.create(
            user=self.user,
            notification=self.no_expiry
        )

    def test_clean_expired_notifications(self):
        """Test that the command deactivates expired notifications"""
        # Capture command output
        out = StringIO()

        # Run the command
        call_command('clean_expired_notifications', stdout=out)

        # Check that expired notifications are now inactive
        self.expired1.refresh_from_db()
        self.expired2.refresh_from_db()
        self.active.refresh_from_db()
        self.no_expiry.refresh_from_db()

        self.assertFalse(self.expired1.is_active)
        self.assertFalse(self.expired2.is_active)
        self.assertTrue(self.active.is_active)
        self.assertTrue(self.no_expiry.is_active)

        # Check command output
        output = out.getvalue()
        self.assertIn('Deactivated 2 expired notifications', output)

    def test_clean_expired_notifications_dry_run(self):
        """Test that the command with dry-run option doesn't change anything"""
        # Capture command output
        out = StringIO()

        # Run the command with dry-run option
        call_command('clean_expired_notifications', '--dry-run', stdout=out)

        # Check that no notifications were deactivated
        self.expired1.refresh_from_db()
        self.expired2.refresh_from_db()

        self.assertTrue(self.expired1.is_active)
        self.assertTrue(self.expired2.is_active)

        # Check command output
        output = out.getvalue()
        self.assertIn('Would deactivate 2 expired notifications', output)
        self.assertIn('Dry run - no changes made', output)
