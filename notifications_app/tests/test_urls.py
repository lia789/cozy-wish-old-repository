from django.test import SimpleTestCase
from django.urls import reverse, resolve
from notifications_app import views


class UrlsTest(SimpleTestCase):
    """Test the URLs for the notifications_app"""
    
    def test_notification_list_url(self):
        """Test the notification list URL"""
        url = reverse('notifications_app:notification_list')
        self.assertEqual(url, '/notifications/')
        self.assertEqual(resolve(url).func, views.notification_list)
    
    def test_notification_detail_url(self):
        """Test the notification detail URL"""
        url = reverse('notifications_app:notification_detail', args=[1])
        self.assertEqual(url, '/notifications/1/')
        self.assertEqual(resolve(url).func, views.notification_detail)
    
    def test_mark_notification_read_url(self):
        """Test the mark notification as read URL"""
        url = reverse('notifications_app:mark_notification_read', args=[1])
        self.assertEqual(url, '/notifications/1/read/')
        self.assertEqual(resolve(url).func, views.mark_notification_read)
    
    def test_mark_notification_unread_url(self):
        """Test the mark notification as unread URL"""
        url = reverse('notifications_app:mark_notification_unread', args=[1])
        self.assertEqual(url, '/notifications/1/unread/')
        self.assertEqual(resolve(url).func, views.mark_notification_unread)
    
    def test_delete_notification_url(self):
        """Test the delete notification URL"""
        url = reverse('notifications_app:delete_notification', args=[1])
        self.assertEqual(url, '/notifications/1/delete/')
        self.assertEqual(resolve(url).func, views.delete_notification)
    
    def test_mark_all_notifications_read_url(self):
        """Test the mark all notifications as read URL"""
        url = reverse('notifications_app:mark_all_notifications_read')
        self.assertEqual(url, '/notifications/mark-all-read/')
        self.assertEqual(resolve(url).func, views.mark_all_notifications_read)
    
    def test_notification_preferences_url(self):
        """Test the notification preferences URL"""
        url = reverse('notifications_app:notification_preferences')
        self.assertEqual(url, '/notifications/preferences/')
        self.assertEqual(resolve(url).func, views.notification_preferences)
    
    def test_get_unread_notifications_url(self):
        """Test the get unread notifications URL"""
        url = reverse('notifications_app:get_unread_notifications')
        self.assertEqual(url, '/notifications/unread/')
        self.assertEqual(resolve(url).func, views.get_unread_notifications)
    
    def test_admin_notification_dashboard_url(self):
        """Test the admin notification dashboard URL"""
        url = reverse('notifications_app:admin_notification_dashboard')
        self.assertEqual(url, '/notifications/admin/dashboard/')
        self.assertEqual(resolve(url).func, views.admin_notification_dashboard)
    
    def test_admin_create_announcement_url(self):
        """Test the admin create announcement URL"""
        url = reverse('notifications_app:admin_create_announcement')
        self.assertEqual(url, '/notifications/admin/announcement/create/')
        self.assertEqual(resolve(url).func, views.admin_create_announcement)
    
    def test_admin_manage_categories_url(self):
        """Test the admin manage categories URL"""
        url = reverse('notifications_app:admin_manage_categories')
        self.assertEqual(url, '/notifications/admin/categories/')
        self.assertEqual(resolve(url).func, views.admin_manage_categories)
    
    def test_admin_create_category_url(self):
        """Test the admin create category URL"""
        url = reverse('notifications_app:admin_create_category')
        self.assertEqual(url, '/notifications/admin/categories/create/')
        self.assertEqual(resolve(url).func, views.admin_create_category)
    
    def test_admin_edit_category_url(self):
        """Test the admin edit category URL"""
        url = reverse('notifications_app:admin_edit_category', args=[1])
        self.assertEqual(url, '/notifications/admin/categories/1/edit/')
        self.assertEqual(resolve(url).func, views.admin_edit_category)
    
    def test_admin_delete_category_url(self):
        """Test the admin delete category URL"""
        url = reverse('notifications_app:admin_delete_category', args=[1])
        self.assertEqual(url, '/notifications/admin/categories/1/delete/')
        self.assertEqual(resolve(url).func, views.admin_delete_category)
    
    def test_admin_notification_list_url(self):
        """Test the admin notification list URL"""
        url = reverse('notifications_app:admin_notification_list')
        self.assertEqual(url, '/notifications/admin/notifications/')
        self.assertEqual(resolve(url).func, views.admin_notification_list)
    
    def test_admin_notification_detail_url(self):
        """Test the admin notification detail URL"""
        url = reverse('notifications_app:admin_notification_detail', args=[1])
        self.assertEqual(url, '/notifications/admin/notifications/1/')
        self.assertEqual(resolve(url).func, views.admin_notification_detail)
    
    def test_admin_deactivate_notification_url(self):
        """Test the admin deactivate notification URL"""
        url = reverse('notifications_app:admin_deactivate_notification', args=[1])
        self.assertEqual(url, '/notifications/admin/notifications/1/deactivate/')
        self.assertEqual(resolve(url).func, views.admin_deactivate_notification)
    
    def test_test_view_url(self):
        """Test the test view URL"""
        url = reverse('notifications_app:test_view')
        self.assertEqual(url, '/notifications/test/')
        self.assertEqual(resolve(url).func, views.test_view)
