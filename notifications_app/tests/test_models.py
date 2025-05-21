from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)
from booking_cart_app.models import Booking
from venues_app.models import Venue

User = get_user_model()


class NotificationCategoryModelTest(TestCase):
    """Test the NotificationCategory model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description',
            icon='fa-bell',
            color='primary'
        )
    
    def test_category_creation(self):
        """Test creating a notification category"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.description, 'Test description')
        self.assertEqual(self.category.icon, 'fa-bell')
        self.assertEqual(self.category.color, 'primary')
        
        # Test string representation
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_category_ordering(self):
        """Test that categories are ordered by name"""
        # Create additional categories
        category_b = NotificationCategory.objects.create(
            name='B Category',
            description='B description'
        )
        
        category_a = NotificationCategory.objects.create(
            name='A Category',
            description='A description'
        )
        
        # Get all categories ordered by name
        categories = NotificationCategory.objects.all()
        
        # Check ordering
        self.assertEqual(categories[0].name, 'A Category')
        self.assertEqual(categories[1].name, 'B Category')
        self.assertEqual(categories[2].name, 'Test Category')


class NotificationModelTest(TestCase):
    """Test the Notification model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create a venue for related object testing
        self.venue = Venue.objects.create(
            name='Test Venue',
            description='Test venue description',
            owner=self.user
        )
        
        # Set dates
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.yesterday = self.now - timedelta(days=1)
        
        # Create a notification
        self.notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium',
            created_at=self.now,
            expires_at=self.tomorrow
        )
    
    def test_notification_creation(self):
        """Test creating a notification"""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.message, 'This is a test notification')
        self.assertEqual(self.notification.priority, 'medium')
        self.assertEqual(self.notification.category, self.category)
        self.assertFalse(self.notification.is_system_wide)
        self.assertTrue(self.notification.is_active)
        
        # Test string representation
        self.assertEqual(str(self.notification), 'Test Notification')
    
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
        self.assertFalse(self.notification.is_expired())  # Not expired yet
        self.assertFalse(no_expiry_notification.is_expired())  # No expiry date
    
    def test_notification_with_related_object(self):
        """Test notification with a related object"""
        # Create a notification with a related object
        content_type = ContentType.objects.get_for_model(Venue)
        
        notification_with_related = Notification.objects.create(
            category=self.category,
            title='Venue Notification',
            message='This notification is related to a venue',
            priority='high',
            content_type=content_type,
            object_id=self.venue.id
        )
        
        self.assertEqual(notification_with_related.content_object, self.venue)
        self.assertEqual(notification_with_related.content_type, content_type)
        self.assertEqual(notification_with_related.object_id, self.venue.id)
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at in descending order"""
        # Create additional notifications with different creation times
        older_notification = Notification.objects.create(
            category=self.category,
            title='Older Notification',
            message='This is an older notification',
            priority='low',
            created_at=self.yesterday
        )
        
        newer_notification = Notification.objects.create(
            category=self.category,
            title='Newer Notification',
            message='This is a newer notification',
            priority='high',
            created_at=self.now + timedelta(hours=1)
        )
        
        # Get all notifications
        notifications = Notification.objects.all()
        
        # Check ordering (newest first)
        self.assertEqual(notifications[0], newer_notification)
        self.assertEqual(notifications[1], self.notification)
        self.assertEqual(notifications[2], older_notification)


class UserNotificationModelTest(TestCase):
    """Test the UserNotification model"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
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
        
        # Create a category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        # Create a notification
        self.notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium'
        )
        
        # Create user notifications
        self.user_notification1 = UserNotification.objects.create(
            user=self.user1,
            notification=self.notification
        )
        
        self.user_notification2 = UserNotification.objects.create(
            user=self.user2,
            notification=self.notification,
            is_read=True,
            read_at=timezone.now()
        )
    
    def test_user_notification_creation(self):
        """Test creating a user notification"""
        self.assertEqual(self.user_notification1.user, self.user1)
        self.assertEqual(self.user_notification1.notification, self.notification)
        self.assertFalse(self.user_notification1.is_read)
        self.assertIsNone(self.user_notification1.read_at)
        self.assertFalse(self.user_notification1.is_deleted)
        self.assertIsNone(self.user_notification1.deleted_at)
        
        # Test string representation
        self.assertEqual(
            str(self.user_notification1), 
            f"{self.user1.email} - {self.notification.title}"
        )
    
    def test_mark_as_read(self):
        """Test marking a notification as read"""
        # Initially unread
        self.assertFalse(self.user_notification1.is_read)
        self.assertIsNone(self.user_notification1.read_at)
        
        # Mark as read
        self.user_notification1.mark_as_read()
        
        # Refresh from database
        self.user_notification1.refresh_from_db()
        
        # Should now be read
        self.assertTrue(self.user_notification1.is_read)
        self.assertIsNotNone(self.user_notification1.read_at)
        
        # Calling mark_as_read again should not change anything
        read_at = self.user_notification1.read_at
        self.user_notification1.mark_as_read()
        self.user_notification1.refresh_from_db()
        self.assertEqual(self.user_notification1.read_at, read_at)
    
    def test_mark_as_unread(self):
        """Test marking a notification as unread"""
        # Initially read
        self.assertTrue(self.user_notification2.is_read)
        self.assertIsNotNone(self.user_notification2.read_at)
        
        # Mark as unread
        self.user_notification2.mark_as_unread()
        
        # Refresh from database
        self.user_notification2.refresh_from_db()
        
        # Should now be unread
        self.assertFalse(self.user_notification2.is_read)
        self.assertIsNone(self.user_notification2.read_at)
        
        # Calling mark_as_unread again should not change anything
        self.user_notification2.mark_as_unread()
        self.user_notification2.refresh_from_db()
        self.assertFalse(self.user_notification2.is_read)
        self.assertIsNone(self.user_notification2.read_at)
    
    def test_delete_notification(self):
        """Test soft deleting a notification"""
        # Initially not deleted
        self.assertFalse(self.user_notification1.is_deleted)
        self.assertIsNone(self.user_notification1.deleted_at)
        
        # Delete notification
        self.user_notification1.delete_notification()
        
        # Refresh from database
        self.user_notification1.refresh_from_db()
        
        # Should now be deleted
        self.assertTrue(self.user_notification1.is_deleted)
        self.assertIsNotNone(self.user_notification1.deleted_at)
        
        # Calling delete_notification again should not change anything
        deleted_at = self.user_notification1.deleted_at
        self.user_notification1.delete_notification()
        self.user_notification1.refresh_from_db()
        self.assertEqual(self.user_notification1.deleted_at, deleted_at)
    
    def test_unique_together_constraint(self):
        """Test that a user can't have duplicate notifications"""
        # Try to create a duplicate user notification
        with self.assertRaises(Exception):
            UserNotification.objects.create(
                user=self.user1,
                notification=self.notification
            )


class NotificationPreferenceModelTest(TestCase):
    """Test the NotificationPreference model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create categories
        self.category1 = NotificationCategory.objects.create(
            name='Category 1',
            description='Description 1'
        )
        
        self.category2 = NotificationCategory.objects.create(
            name='Category 2',
            description='Description 2'
        )
        
        # Create preferences
        self.preference1 = NotificationPreference.objects.create(
            user=self.user,
            category=self.category1,
            channel='in_app',
            is_enabled=True
        )
        
        self.preference2 = NotificationPreference.objects.create(
            user=self.user,
            category=self.category2,
            channel='none',
            is_enabled=False
        )
    
    def test_preference_creation(self):
        """Test creating a notification preference"""
        self.assertEqual(self.preference1.user, self.user)
        self.assertEqual(self.preference1.category, self.category1)
        self.assertEqual(self.preference1.channel, 'in_app')
        self.assertTrue(self.preference1.is_enabled)
        
        self.assertEqual(self.preference2.user, self.user)
        self.assertEqual(self.preference2.category, self.category2)
        self.assertEqual(self.preference2.channel, 'none')
        self.assertFalse(self.preference2.is_enabled)
        
        # Test string representation
        self.assertEqual(
            str(self.preference1), 
            f"{self.user.email} - {self.category1.name} - In-App"
        )
    
    def test_unique_together_constraint(self):
        """Test that a user can't have duplicate preferences for the same category"""
        # Try to create a duplicate preference
        with self.assertRaises(Exception):
            NotificationPreference.objects.create(
                user=self.user,
                category=self.category1,
                channel='email',
                is_enabled=True
            )
    
    def test_preference_ordering(self):
        """Test that preferences are ordered by category name"""
        # Get all preferences for the user
        preferences = NotificationPreference.objects.filter(user=self.user)
        
        # Check ordering
        self.assertEqual(preferences[0].category, self.category1)  # Category 1
        self.assertEqual(preferences[1].category, self.category2)  # Category 2
