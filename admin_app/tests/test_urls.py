from django.test import SimpleTestCase
from django.urls import reverse, resolve
from admin_app import views

class AdminURLsTest(SimpleTestCase):
    """Test that URLs are correctly mapped to views"""

    # Authentication URLs
    def test_admin_login_url(self):
        """Test the admin login URL"""
        url = reverse('admin_app:admin_login')
        self.assertEqual(url, '/super-admin/login/')
        self.assertEqual(resolve(url).func, views.admin_login)

    def test_admin_logout_url(self):
        """Test the admin logout URL"""
        url = reverse('admin_app:admin_logout')
        self.assertEqual(url, '/super-admin/logout/')
        self.assertEqual(resolve(url).func, views.admin_logout)

    # Dashboard URL
    def test_admin_dashboard_url(self):
        """Test the admin dashboard URL"""
        url = reverse('admin_app:admin_dashboard')
        self.assertEqual(url, '/super-admin/')
        self.assertEqual(resolve(url).func, views.admin_dashboard)

    # User Management URLs
    def test_user_list_url(self):
        """Test the user list URL"""
        url = reverse('admin_app:user_list')
        self.assertEqual(url, '/super-admin/users/')
        self.assertEqual(resolve(url).func, views.user_list)

    def test_user_create_url(self):
        """Test the user create URL"""
        url = reverse('admin_app:user_create')
        self.assertEqual(url, '/super-admin/users/create/')
        self.assertEqual(resolve(url).func, views.user_create)

    def test_user_detail_url(self):
        """Test the user detail URL"""
        url = reverse('admin_app:user_detail', kwargs={'user_id': 1})
        self.assertEqual(url, '/super-admin/users/1/')
        self.assertEqual(resolve(url).func, views.user_detail)

    def test_user_edit_url(self):
        """Test the user edit URL"""
        url = reverse('admin_app:user_edit', kwargs={'user_id': 1})
        self.assertEqual(url, '/super-admin/users/1/edit/')
        self.assertEqual(resolve(url).func, views.user_edit)

    def test_user_delete_url(self):
        """Test the user delete URL"""
        url = reverse('admin_app:user_delete', kwargs={'user_id': 1})
        self.assertEqual(url, '/super-admin/users/1/delete/')
        self.assertEqual(resolve(url).func, views.user_delete)

    def test_user_bulk_actions_url(self):
        """Test the user bulk actions URL"""
        url = reverse('admin_app:user_bulk_actions')
        self.assertEqual(url, '/super-admin/users/bulk-actions/')
        self.assertEqual(resolve(url).func, views.user_bulk_actions)

    # Venue Management URLs
    def test_venue_list_url(self):
        """Test the venue list URL"""
        url = reverse('admin_app:venue_list')
        self.assertEqual(url, '/super-admin/venues/')
        self.assertEqual(resolve(url).func, views.venue_list)

    def test_venue_detail_url(self):
        """Test the venue detail URL"""
        url = reverse('admin_app:venue_detail', kwargs={'venue_id': 1})
        self.assertEqual(url, '/super-admin/venues/1/')
        self.assertEqual(resolve(url).func, views.venue_detail)

    def test_venue_approval_url(self):
        """Test the venue approval URL"""
        url = reverse('admin_app:venue_approval', kwargs={'venue_id': 1})
        self.assertEqual(url, '/super-admin/venues/1/approval/')
        self.assertEqual(resolve(url).func, views.venue_approval)

    def test_pending_venues_url(self):
        """Test the pending venues URL"""
        url = reverse('admin_app:pending_venues')
        self.assertEqual(url, '/super-admin/venues/pending/')
        self.assertEqual(resolve(url).func, views.pending_venues)

    # System Configuration URL
    def test_system_config_url(self):
        """Test the system config URL"""
        url = reverse('admin_app:system_config')
        self.assertEqual(url, '/super-admin/system/config/')
        self.assertEqual(resolve(url).func, views.system_config)

    # Audit Logs URLs
    def test_audit_log_list_url(self):
        """Test the audit log list URL"""
        url = reverse('admin_app:audit_log_list')
        self.assertEqual(url, '/super-admin/audit-logs/')
        self.assertEqual(resolve(url).func, views.audit_log_list)

    def test_audit_log_detail_url(self):
        """Test the audit log detail URL"""
        url = reverse('admin_app:audit_log_detail', kwargs={'log_id': 1})
        self.assertEqual(url, '/super-admin/audit-logs/1/')
        self.assertEqual(resolve(url).func, views.audit_log_detail)

    def test_export_audit_logs_url(self):
        """Test the export audit logs URL"""
        url = reverse('admin_app:export_audit_logs')
        self.assertEqual(url, '/super-admin/audit-logs/export/')
        self.assertEqual(resolve(url).func, views.export_audit_logs)

    # Security Monitoring URLs
    def test_security_event_list_url(self):
        """Test the security event list URL"""
        url = reverse('admin_app:security_event_list')
        self.assertEqual(url, '/super-admin/security/events/')
        self.assertEqual(resolve(url).func, views.security_event_list)

    def test_security_event_detail_url(self):
        """Test the security event detail URL"""
        url = reverse('admin_app:security_event_detail', kwargs={'event_id': 1})
        self.assertEqual(url, '/super-admin/security/events/1/')
        self.assertEqual(resolve(url).func, views.security_event_detail)

    def test_security_event_resolve_url(self):
        """Test the security event resolve URL"""
        url = reverse('admin_app:security_event_resolve', kwargs={'event_id': 1})
        self.assertEqual(url, '/super-admin/security/events/1/resolve/')
        self.assertEqual(resolve(url).func, views.security_event_resolve)

    # Task Management URLs
    def test_task_list_url(self):
        """Test the task list URL"""
        url = reverse('admin_app:task_list')
        self.assertEqual(url, '/super-admin/tasks/')
        self.assertEqual(resolve(url).func, views.task_list)

    def test_task_create_url(self):
        """Test the task create URL"""
        url = reverse('admin_app:task_create')
        self.assertEqual(url, '/super-admin/tasks/create/')
        self.assertEqual(resolve(url).func, views.task_create)

    def test_task_detail_url(self):
        """Test the task detail URL"""
        url = reverse('admin_app:task_detail', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/')
        self.assertEqual(resolve(url).func, views.task_detail)

    def test_task_edit_url(self):
        """Test the task edit URL"""
        url = reverse('admin_app:task_edit', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/edit/')
        self.assertEqual(resolve(url).func, views.task_edit)

    def test_task_delete_url(self):
        """Test the task delete URL"""
        url = reverse('admin_app:task_delete', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/delete/')
        self.assertEqual(resolve(url).func, views.task_delete)

    def test_task_update_status_url(self):
        """Test the task update status URL"""
        url = reverse('admin_app:task_update_status', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/update-status/')
        self.assertEqual(resolve(url).func, views.task_update_status)

    def test_task_mark_completed_url(self):
        """Test the task mark completed URL"""
        url = reverse('admin_app:task_mark_completed', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/mark-completed/')
        self.assertEqual(resolve(url).func, views.task_mark_completed)

    def test_task_mark_cancelled_url(self):
        """Test the task mark cancelled URL"""
        url = reverse('admin_app:task_mark_cancelled', kwargs={'task_id': 1})
        self.assertEqual(url, '/super-admin/tasks/1/mark-cancelled/')
        self.assertEqual(resolve(url).func, views.task_mark_cancelled)

    # Analytics URLs
    def test_analytics_dashboard_url(self):
        """Test the analytics dashboard URL"""
        url = reverse('admin_app:analytics_dashboard')
        self.assertEqual(url, '/super-admin/analytics/')
        self.assertEqual(resolve(url).func, views.analytics_dashboard)

    def test_user_report_url(self):
        """Test the user report URL"""
        url = reverse('admin_app:user_report')
        self.assertEqual(url, '/super-admin/analytics/users/')
        self.assertEqual(resolve(url).func, views.user_report)

    def test_booking_report_url(self):
        """Test the booking report URL"""
        url = reverse('admin_app:booking_report')
        self.assertEqual(url, '/super-admin/analytics/bookings/')
        self.assertEqual(resolve(url).func, views.booking_report)

    def test_revenue_report_url(self):
        """Test the revenue report URL"""
        url = reverse('admin_app:revenue_report')
        self.assertEqual(url, '/super-admin/analytics/revenue/')
        self.assertEqual(resolve(url).func, views.revenue_report)

    # Admin Preferences URL
    def test_admin_preferences_url(self):
        """Test the admin preferences URL"""
        url = reverse('admin_app:admin_preferences')
        self.assertEqual(url, '/super-admin/preferences/')
        self.assertEqual(resolve(url).func, views.admin_preferences)
