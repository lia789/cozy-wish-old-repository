from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.utils import timezone

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)
from notifications_app.admin import (
    NotificationCategoryAdmin, NotificationAdmin, UserNotificationAdmin, NotificationPreferenceAdmin
)

User = get_user_model()


class MockRequest:
    """Mock request for admin testing"""
    def __init__(self, user=None):
        self.user = user


class NotificationAdminTest(TestCase):
    """Test the Django admin for notifications_app"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create client and login
        self.client = Client()
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Create notification category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description',
            icon='fa-bell',
            color='primary'
        )
        
        # Create notification
        self.notification = Notification.objects.create(
            category=self.category,
            title='Test Notification',
            message='This is a test notification',
            priority='medium',
            created_at=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Create user notification
        self.user_notification = UserNotification.objects.create(
            user=self.user,
            notification=self.notification
        )
        
        # Create notification preference
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            category=self.category,
            channel='both',
            is_enabled=True
        )
        
        # Create admin site
        self.site = AdminSite()
        
        # Create admin classes
        self.category_admin = NotificationCategoryAdmin(NotificationCategory, self.site)
        self.notification_admin = NotificationAdmin(Notification, self.site)
        self.user_notification_admin = UserNotificationAdmin(UserNotification, self.site)
        self.preference_admin = NotificationPreferenceAdmin(NotificationPreference, self.site)
    
    def test_category_admin_list_display(self):
        """Test the list_display for NotificationCategoryAdmin"""
        self.assertEqual(
            self.category_admin.list_display,
            ('name', 'description', 'icon', 'color')
        )
    
    def test_notification_admin_list_display(self):
        """Test the list_display for NotificationAdmin"""
        self.assertEqual(
            self.notification_admin.list_display,
            ('title', 'category', 'priority', 'created_at', 'expires_at', 'is_system_wide', 'is_active')
        )
    
    def test_user_notification_admin_list_display(self):
        """Test the list_display for UserNotificationAdmin"""
        self.assertEqual(
            self.user_notification_admin.list_display,
            ('user', 'notification', 'is_read', 'read_at', 'is_deleted', 'deleted_at')
        )
    
    def test_preference_admin_list_display(self):
        """Test the list_display for NotificationPreferenceAdmin"""
        self.assertEqual(
            self.preference_admin.list_display,
            ('user', 'category', 'channel', 'is_enabled')
        )
    
    def test_admin_category_changelist(self):
        """Test the category changelist view"""
        url = reverse('admin:notifications_app_notificationcategory_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
    
    def test_admin_notification_changelist(self):
        """Test the notification changelist view"""
        url = reverse('admin:notifications_app_notification_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
    
    def test_admin_user_notification_changelist(self):
        """Test the user notification changelist view"""
        url = reverse('admin:notifications_app_usernotification_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user@example.com')
        self.assertContains(response, 'Test Notification')
    
    def test_admin_preference_changelist(self):
        """Test the preference changelist view"""
        url = reverse('admin:notifications_app_notificationpreference_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user@example.com')
        self.assertContains(response, 'Test Category')
    
    def test_admin_category_change(self):
        """Test the category change view"""
        url = reverse('admin:notifications_app_notificationcategory_change', args=[self.category.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertContains(response, 'Test description')
    
    def test_admin_notification_change(self):
        """Test the notification change view"""
        url = reverse('admin:notifications_app_notification_change', args=[self.notification.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
        self.assertContains(response, 'This is a test notification')
    
    def test_admin_user_notification_change(self):
        """Test the user notification change view"""
        url = reverse('admin:notifications_app_usernotification_change', args=[self.user_notification.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user@example.com')
        self.assertContains(response, 'Test Notification')
    
    def test_admin_preference_change(self):
        """Test the preference change view"""
        url = reverse('admin:notifications_app_notificationpreference_change', args=[self.preference.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user@example.com')
        self.assertContains(response, 'Test Category')
