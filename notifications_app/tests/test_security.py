from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification
)
from notifications_app.utils import create_notification

User = get_user_model()


class NotificationSecurityTest(TestCase):
    """Test security aspects of the notifications_app"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='testpass123',
            is_active=True,
            is_customer=True
        )
        
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
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
        
        # Create notification category
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        # Create notifications for each user
        self.notification1 = create_notification(
            category_name='Test Category',
            title='Customer1 Notification',
            message='This is a notification for customer1',
            users=[self.customer1],
            priority='medium'
        )
        
        self.notification2 = create_notification(
            category_name='Test Category',
            title='Customer2 Notification',
            message='This is a notification for customer2',
            users=[self.customer2],
            priority='medium'
        )
        
        self.notification3 = create_notification(
            category_name='Test Category',
            title='Provider Notification',
            message='This is a notification for the provider',
            users=[self.provider],
            priority='medium'
        )
        
        # Create client
        self.client = Client()
        
        # URLs
        self.notification_list_url = reverse('notifications_app:notification_list')
        self.notification_detail_url = lambda id: reverse('notifications_app:notification_detail', args=[id])
        self.mark_read_url = lambda id: reverse('notifications_app:mark_notification_read', args=[id])
        self.mark_unread_url = lambda id: reverse('notifications_app:mark_notification_unread', args=[id])
        self.delete_notification_url = lambda id: reverse('notifications_app:delete_notification', args=[id])
        self.preferences_url = reverse('notifications_app:notification_preferences')
        
        # Admin URLs
        self.admin_dashboard_url = reverse('notifications_app:admin_notification_dashboard')
        self.admin_notification_list_url = reverse('notifications_app:admin_notification_list')
        self.admin_notification_detail_url = lambda id: reverse('notifications_app:admin_notification_detail', args=[id])
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access notification views"""
        # Try to access notification list
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
        
        # Try to access notification detail
        response = self.client.get(self.notification_detail_url(self.notification1.id))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
        
        # Try to mark notification as read
        response = self.client.post(self.mark_read_url(self.notification1.id))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
        
        # Try to access preferences
        response = self.client.get(self.preferences_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
        
        # Try to access admin dashboard
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_notification_access_control(self):
        """Test that users can only access their own notifications"""
        # Login as customer1
        self.client.login(username='customer1@example.com', password='testpass123')
        
        # Try to access customer1's notification (should succeed)
        response = self.client.get(self.notification_detail_url(self.notification1.id))
        self.assertEqual(response.status_code, 200)
        
        # Try to access customer2's notification (should fail)
        response = self.client.get(self.notification_detail_url(self.notification2.id))
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Try to access provider's notification (should fail)
        response = self.client.get(self.notification_detail_url(self.notification3.id))
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Try to mark customer2's notification as read (should fail)
        response = self.client.post(self.mark_read_url(self.notification2.id))
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Check that customer2's notification is still unread
        user_notification2 = UserNotification.objects.get(
            user=self.customer2,
            notification=self.notification2
        )
        self.assertFalse(user_notification2.is_read)
    
    def test_admin_access_control(self):
        """Test that only admins can access admin views"""
        # Login as customer1 (non-admin)
        self.client.login(username='customer1@example.com', password='testpass123')
        
        # Try to access admin dashboard (should fail)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Try to access admin notification list (should fail)
        response = self.client.get(self.admin_notification_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Try to access admin notification detail (should fail)
        response = self.client.get(self.admin_notification_detail_url(self.notification1.id))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Try to access admin dashboard (should succeed)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        
        # Try to access admin notification list (should succeed)
        response = self.client.get(self.admin_notification_list_url)
        self.assertEqual(response.status_code, 200)
        
        # Try to access admin notification detail (should succeed)
        response = self.client.get(self.admin_notification_detail_url(self.notification1.id))
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_protection(self):
        """Test that CSRF protection is enforced"""
        # Login as customer1
        self.client.login(username='customer1@example.com', password='testpass123')
        
        # Try to mark notification as read without CSRF token (should fail)
        self.client.handler.enforce_csrf_checks = True
        response = self.client.post(self.mark_read_url(self.notification1.id))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Check that the notification is still unread
        user_notification1 = UserNotification.objects.get(
            user=self.customer1,
            notification=self.notification1
        )
        self.assertFalse(user_notification1.is_read)
    
    def test_method_not_allowed(self):
        """Test that views enforce HTTP method restrictions"""
        # Login as customer1
        self.client.login(username='customer1@example.com', password='testpass123')
        
        # Try to mark notification as read with GET (should fail)
        response = self.client.get(self.mark_read_url(self.notification1.id))
        self.assertEqual(response.status_code, 400)  # Bad request
        
        # Try to mark notification as unread with GET (should fail)
        response = self.client.get(self.mark_unread_url(self.notification1.id))
        self.assertEqual(response.status_code, 400)  # Bad request
        
        # Try to delete notification with GET (should fail)
        response = self.client.get(self.delete_notification_url(self.notification1.id))
        self.assertEqual(response.status_code, 400)  # Bad request
