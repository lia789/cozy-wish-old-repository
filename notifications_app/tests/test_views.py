from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)
from notifications_app.utils import create_notification, create_system_announcement

User = get_user_model()


class NotificationViewTestBase(TestCase):
    """Base class for notification view tests"""
    
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
        
        # Create notifications for the customer
        self.notification1 = create_notification(
            category_name='Booking',
            title='Booking Confirmed',
            message='Your booking has been confirmed.',
            users=[self.customer],
            priority='medium'
        )
        
        self.notification2 = create_notification(
            category_name='Review',
            title='New Review Response',
            message='A service provider has responded to your review.',
            users=[self.customer],
            priority='low'
        )
        
        # Create notifications for the provider
        self.notification3 = create_notification(
            category_name='Booking',
            title='New Booking',
            message='You have a new booking.',
            users=[self.provider],
            priority='high'
        )
        
        # Create a system announcement
        self.announcement = create_system_announcement(
            title='System Maintenance',
            message='The system will be down for maintenance on Saturday.',
            expires_in_days=7
        )
        
        # URLs
        self.notification_list_url = reverse('notifications_app:notification_list')
        self.notification_detail_url = lambda id: reverse('notifications_app:notification_detail', args=[id])
        self.mark_read_url = lambda id: reverse('notifications_app:mark_notification_read', args=[id])
        self.mark_unread_url = lambda id: reverse('notifications_app:mark_notification_unread', args=[id])
        self.delete_notification_url = lambda id: reverse('notifications_app:delete_notification', args=[id])
        self.mark_all_read_url = reverse('notifications_app:mark_all_notifications_read')
        self.preferences_url = reverse('notifications_app:notification_preferences')
        self.unread_url = reverse('notifications_app:get_unread_notifications')
        
        # Admin URLs
        self.admin_dashboard_url = reverse('notifications_app:admin_notification_dashboard')
        self.admin_create_announcement_url = reverse('notifications_app:admin_create_announcement')
        self.admin_manage_categories_url = reverse('notifications_app:admin_manage_categories')
        self.admin_create_category_url = reverse('notifications_app:admin_create_category')
        self.admin_edit_category_url = lambda id: reverse('notifications_app:admin_edit_category', args=[id])
        self.admin_delete_category_url = lambda id: reverse('notifications_app:admin_delete_category', args=[id])
        self.admin_notification_list_url = reverse('notifications_app:admin_notification_list')
        self.admin_notification_detail_url = lambda id: reverse('notifications_app:admin_notification_detail', args=[id])
        self.admin_deactivate_notification_url = lambda id: reverse('notifications_app:admin_deactivate_notification', args=[id])


class NotificationListViewTest(NotificationViewTestBase):
    """Test the notification list view"""
    
    def test_login_required(self):
        """Test that login is required to access the view"""
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_customer_can_view_notifications(self):
        """Test that a customer can view their notifications"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.notification_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/notification_list.html')
        
        # Check that the customer's notifications are in the context
        self.assertEqual(response.context['notifications'].paginator.count, 2)
        
        # Check that the notifications are the correct ones
        notification_ids = [n.notification.id for n in response.context['notifications']]
        self.assertIn(self.notification1.id, notification_ids)
        self.assertIn(self.notification2.id, notification_ids)
    
    def test_provider_can_view_notifications(self):
        """Test that a service provider can view their notifications"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.notification_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/notification_list.html')
        
        # Check that the provider's notifications are in the context
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        
        # Check that the notification is the correct one
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification3.id)
    
    def test_filter_by_read_status(self):
        """Test filtering notifications by read status"""
        # Mark one notification as read
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        user_notification.mark_as_read()
        
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get unread notifications only
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification2.id)
        
        # Get all notifications (including read)
        response = self.client.get(f"{self.notification_list_url}?show_read=true")
        self.assertEqual(response.context['notifications'].paginator.count, 2)
    
    def test_filter_by_category(self):
        """Test filtering notifications by category"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Filter by booking category
        response = self.client.get(f"{self.notification_list_url}?category={self.booking_category.id}")
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification1.id)
        
        # Filter by review category
        response = self.client.get(f"{self.notification_list_url}?category={self.review_category.id}")
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification2.id)
    
    def test_search_notifications(self):
        """Test searching notifications"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Search for 'booking'
        response = self.client.get(f"{self.notification_list_url}?search=booking")
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification1.id)
        
        # Search for 'review'
        response = self.client.get(f"{self.notification_list_url}?search=review")
        self.assertEqual(response.context['notifications'].paginator.count, 1)
        self.assertEqual(response.context['notifications'][0].notification.id, self.notification2.id)
        
        # Search for something that doesn't exist
        response = self.client.get(f"{self.notification_list_url}?search=nonexistent")
        self.assertEqual(response.context['notifications'].paginator.count, 0)


class NotificationDetailViewTest(NotificationViewTestBase):
    """Test the notification detail view"""
    
    def test_login_required(self):
        """Test that login is required to access the view"""
        response = self.client.get(self.notification_detail_url(self.notification1.id))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_customer_can_view_own_notification(self):
        """Test that a customer can view their own notification"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.notification_detail_url(self.notification1.id))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/notification_detail.html')
        
        # Check that the notification is in the context
        self.assertEqual(response.context['notification'].notification.id, self.notification1.id)
        
        # Check that the notification is marked as read
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        self.assertTrue(user_notification.is_read)
    
    def test_customer_cannot_view_others_notification(self):
        """Test that a customer cannot view another user's notification"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.notification_detail_url(self.notification3.id))
        
        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)
    
    def test_provider_can_view_own_notification(self):
        """Test that a service provider can view their own notification"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.notification_detail_url(self.notification3.id))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/notification_detail.html')
        
        # Check that the notification is in the context
        self.assertEqual(response.context['notification'].notification.id, self.notification3.id)


class NotificationActionViewsTest(NotificationViewTestBase):
    """Test the notification action views (mark as read/unread, delete)"""
    
    def test_mark_notification_read(self):
        """Test marking a notification as read"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure the notification is unread
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        user_notification.is_read = False
        user_notification.read_at = None
        user_notification.save()
        
        # Mark as read
        response = self.client.post(self.mark_read_url(self.notification1.id))
        
        # Should redirect to notification list
        self.assertRedirects(response, self.notification_list_url)
        
        # Check that the notification is now read
        user_notification.refresh_from_db()
        self.assertTrue(user_notification.is_read)
        self.assertIsNotNone(user_notification.read_at)
    
    def test_mark_notification_read_ajax(self):
        """Test marking a notification as read via AJAX"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure the notification is unread
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        user_notification.is_read = False
        user_notification.read_at = None
        user_notification.save()
        
        # Mark as read via AJAX
        response = self.client.post(
            self.mark_read_url(self.notification1.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'success': True, 'unread_count': 1}  # One other unread notification
        )
        
        # Check that the notification is now read
        user_notification.refresh_from_db()
        self.assertTrue(user_notification.is_read)
    
    def test_mark_notification_unread(self):
        """Test marking a notification as unread"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure the notification is read
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        user_notification.mark_as_read()
        
        # Mark as unread
        response = self.client.post(self.mark_unread_url(self.notification1.id))
        
        # Should redirect to notification list
        self.assertRedirects(response, self.notification_list_url)
        
        # Check that the notification is now unread
        user_notification.refresh_from_db()
        self.assertFalse(user_notification.is_read)
        self.assertIsNone(user_notification.read_at)
    
    def test_delete_notification(self):
        """Test deleting a notification"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Delete the notification
        response = self.client.post(self.delete_notification_url(self.notification1.id))
        
        # Should redirect to notification list
        self.assertRedirects(response, self.notification_list_url)
        
        # Check that the notification is now deleted (soft delete)
        user_notification = UserNotification.objects.get(
            user=self.customer,
            notification=self.notification1
        )
        self.assertTrue(user_notification.is_deleted)
        self.assertIsNotNone(user_notification.deleted_at)
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure all notifications are unread
        UserNotification.objects.filter(user=self.customer).update(
            is_read=False,
            read_at=None
        )
        
        # Mark all as read
        response = self.client.post(self.mark_all_read_url)
        
        # Should redirect to notification list
        self.assertRedirects(response, self.notification_list_url)
        
        # Check that all notifications are now read
        unread_count = UserNotification.objects.filter(
            user=self.customer,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)
    
    def test_mark_all_notifications_read_ajax(self):
        """Test marking all notifications as read via AJAX"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure all notifications are unread
        UserNotification.objects.filter(user=self.customer).update(
            is_read=False,
            read_at=None
        )
        
        # Mark all as read via AJAX
        response = self.client.post(
            self.mark_all_read_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'success': True, 'count': 2, 'unread_count': 0}
        )
        
        # Check that all notifications are now read
        unread_count = UserNotification.objects.filter(
            user=self.customer,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)


class NotificationPreferencesViewTest(NotificationViewTestBase):
    """Test the notification preferences view"""
    
    def test_login_required(self):
        """Test that login is required to access the view"""
        response = self.client.get(self.preferences_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_get_preferences_page(self):
        """Test getting the preferences page"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Get the preferences page
        response = self.client.get(self.preferences_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/notification_preferences.html')
        
        # Check that the preferences are in the context
        self.assertIn('preferences', response.context)
        self.assertEqual(len(response.context['preferences']), 3)  # 3 categories
    
    def test_update_preferences(self):
        """Test updating notification preferences"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Submit the form to update preferences
        response = self.client.post(self.preferences_url, {
            f'preference_{self.booking_category.id}_channel': 'email',
            f'preference_{self.booking_category.id}_is_enabled': 'on',
            f'preference_{self.review_category.id}_channel': 'none',
            f'preference_{self.review_category.id}_is_enabled': '',  # Unchecked
            f'preference_{self.announcement_category.id}_channel': 'both',
            f'preference_{self.announcement_category.id}_is_enabled': 'on'
        })
        
        # Should redirect to preferences page
        self.assertRedirects(response, self.preferences_url)
        
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
        
        announcement_pref = NotificationPreference.objects.get(
            user=self.customer,
            category=self.announcement_category
        )
        self.assertEqual(announcement_pref.channel, 'both')
        self.assertTrue(announcement_pref.is_enabled)


class GetUnreadNotificationsViewTest(NotificationViewTestBase):
    """Test the get_unread_notifications view"""
    
    def test_login_required(self):
        """Test that login is required to access the view"""
        response = self.client.get(self.unread_url)
        self.assertEqual(response.status_code, 400)  # Bad request (not AJAX)
    
    def test_ajax_required(self):
        """Test that AJAX is required to access the view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Try to access without AJAX
        response = self.client.get(self.unread_url)
        self.assertEqual(response.status_code, 400)  # Bad request
    
    def test_get_unread_notifications(self):
        """Test getting unread notifications via AJAX"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Make sure all notifications are unread
        UserNotification.objects.filter(user=self.customer).update(
            is_read=False,
            read_at=None
        )
        
        # Get unread notifications via AJAX
        response = self.client.get(
            self.unread_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['unread_count'], 2)
        self.assertEqual(len(data['notifications']), 2)
        self.assertEqual(data['more_url'], self.notification_list_url)
        
        # Check that the notifications are the correct ones
        notification_titles = [n['title'] for n in data['notifications']]
        self.assertIn('Booking Confirmed', notification_titles)
        self.assertIn('New Review Response', notification_titles)


class AdminNotificationViewsTest(NotificationViewTestBase):
    """Test the admin notification views"""
    
    def test_admin_required(self):
        """Test that admin access is required for admin views"""
        # Login as customer (non-admin)
        self.client.login(username='customer@example.com', password='testpass123')
        
        # Try to access admin dashboard
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access admin notification list
        response = self.client.get(self.admin_notification_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard(self):
        """Test the admin notification dashboard"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Access the dashboard
        response = self.client.get(self.admin_dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/dashboard.html')
        
        # Check that the dashboard data is in the context
        self.assertIn('total_notifications', response.context)
        self.assertIn('active_notifications', response.context)
        self.assertIn('system_wide_notifications', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('recent_notifications', response.context)
        
        # Check the counts
        self.assertEqual(response.context['total_notifications'], 4)  # 3 user notifications + 1 system announcement
        self.assertEqual(response.context['system_wide_notifications'], 1)  # 1 system announcement
    
    def test_admin_create_announcement(self):
        """Test creating a system announcement"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Get the form
        response = self.client.get(self.admin_create_announcement_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/announcement_form.html')
        
        # Submit the form
        response = self.client.post(self.admin_create_announcement_url, {
            'title': 'New Announcement',
            'message': 'This is a new system-wide announcement',
            'priority': 'high',
            'expires_in_days': 14
        })
        
        # Should redirect to dashboard
        self.assertRedirects(response, self.admin_dashboard_url)
        
        # Check that the announcement was created
        self.assertTrue(
            Notification.objects.filter(
                title='New Announcement',
                is_system_wide=True
            ).exists()
        )
    
    def test_admin_manage_categories(self):
        """Test the manage categories view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Access the categories page
        response = self.client.get(self.admin_manage_categories_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/category_list.html')
        
        # Check that the categories are in the context
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 3)
    
    def test_admin_create_category(self):
        """Test creating a notification category"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Get the form
        response = self.client.get(self.admin_create_category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/category_form.html')
        
        # Submit the form
        response = self.client.post(self.admin_create_category_url, {
            'name': 'New Category',
            'description': 'This is a new notification category',
            'icon': 'fa-bell',
            'color': 'success'
        })
        
        # Should redirect to manage categories
        self.assertRedirects(response, self.admin_manage_categories_url)
        
        # Check that the category was created
        self.assertTrue(
            NotificationCategory.objects.filter(name='New Category').exists()
        )
    
    def test_admin_edit_category(self):
        """Test editing a notification category"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Get the form
        response = self.client.get(self.admin_edit_category_url(self.booking_category.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/category_form.html')
        
        # Submit the form
        response = self.client.post(self.admin_edit_category_url(self.booking_category.id), {
            'name': 'Updated Booking',
            'description': 'Updated booking notifications',
            'icon': 'fa-calendar-alt',
            'color': 'success'
        })
        
        # Should redirect to manage categories
        self.assertRedirects(response, self.admin_manage_categories_url)
        
        # Check that the category was updated
        self.booking_category.refresh_from_db()
        self.assertEqual(self.booking_category.name, 'Updated Booking')
        self.assertEqual(self.booking_category.description, 'Updated booking notifications')
        self.assertEqual(self.booking_category.icon, 'fa-calendar-alt')
        self.assertEqual(self.booking_category.color, 'success')
    
    def test_admin_delete_category(self):
        """Test deleting a notification category"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Create a new category to delete
        category = NotificationCategory.objects.create(
            name='Category to Delete',
            description='This category will be deleted'
        )
        
        # Delete the category
        response = self.client.post(self.admin_delete_category_url(category.id))
        
        # Should redirect to manage categories
        self.assertRedirects(response, self.admin_manage_categories_url)
        
        # Check that the category was deleted
        self.assertFalse(
            NotificationCategory.objects.filter(id=category.id).exists()
        )
    
    def test_admin_notification_list(self):
        """Test the admin notification list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Access the notification list
        response = self.client.get(self.admin_notification_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/notification_list.html')
        
        # Check that all notifications are in the context
        self.assertIn('notifications', response.context)
        self.assertEqual(response.context['notifications'].paginator.count, 4)
    
    def test_admin_notification_detail(self):
        """Test the admin notification detail view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Access the notification detail
        response = self.client.get(self.admin_notification_detail_url(self.notification1.id))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications_app/admin/notification_detail.html')
        
        # Check that the notification is in the context
        self.assertIn('notification', response.context)
        self.assertEqual(response.context['notification'].id, self.notification1.id)
        
        # Check that user notifications are in the context
        self.assertIn('user_notifications', response.context)
        self.assertEqual(len(response.context['user_notifications']), 1)
    
    def test_admin_deactivate_notification(self):
        """Test deactivating a notification"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Deactivate the notification
        response = self.client.post(self.admin_deactivate_notification_url(self.notification1.id))
        
        # Should redirect to admin notification list
        self.assertRedirects(response, self.admin_notification_list_url)
        
        # Check that the notification is now inactive
        self.notification1.refresh_from_db()
        self.assertFalse(self.notification1.is_active)
