from django.test import SimpleTestCase
from django.urls import reverse, resolve
from dashboard_app import views

class DashboardURLsTest(SimpleTestCase):
    """Test the URLs for the dashboard_app"""

    def test_dashboard_redirect_url(self):
        """Test the dashboard redirect URL"""
        url = reverse('dashboard_app:dashboard_redirect')
        self.assertEqual(url, '/dashboard/')
        self.assertEqual(resolve(url).func, views.dashboard_redirect)

    def test_dashboard_preferences_url(self):
        """Test the dashboard preferences URL"""
        url = reverse('dashboard_app:dashboard_preferences')
        self.assertEqual(url, '/dashboard/preferences/')
        self.assertEqual(resolve(url).func, views.dashboard_preferences)

    def test_add_widget_url(self):
        """Test the add widget URL"""
        url = reverse('dashboard_app:add_widget')
        self.assertEqual(url, '/dashboard/widgets/add/')
        self.assertEqual(resolve(url).func, views.add_widget)

    def test_remove_widget_url(self):
        """Test the remove widget URL"""
        url = reverse('dashboard_app:remove_widget', args=[1])
        self.assertEqual(url, '/dashboard/widgets/remove/1/')
        self.assertEqual(resolve(url).func, views.remove_widget)

    def test_reorder_widgets_url(self):
        """Test the reorder widgets URL"""
        url = reverse('dashboard_app:reorder_widgets')
        self.assertEqual(url, '/dashboard/widgets/reorder/')
        self.assertEqual(resolve(url).func, views.reorder_widgets)

    # Customer Dashboard URLs
    def test_customer_dashboard_url(self):
        """Test the customer dashboard URL"""
        url = reverse('dashboard_app:customer_dashboard')
        self.assertEqual(url, '/dashboard/customer/')
        self.assertEqual(resolve(url).func, views.customer_dashboard)

    def test_customer_booking_history_url(self):
        """Test the customer booking history URL"""
        url = reverse('dashboard_app:customer_booking_history')
        self.assertEqual(url, '/dashboard/customer/bookings/')
        self.assertEqual(resolve(url).func, views.customer_booking_history)

    def test_customer_active_bookings_url(self):
        """Test the customer active bookings URL"""
        url = reverse('dashboard_app:customer_active_bookings')
        self.assertEqual(url, '/dashboard/customer/active-bookings/')
        self.assertEqual(resolve(url).func, views.customer_active_bookings)

    def test_customer_favorite_venues_url(self):
        """Test the customer favorite venues URL"""
        url = reverse('dashboard_app:customer_favorite_venues')
        self.assertEqual(url, '/dashboard/customer/favorites/')
        self.assertEqual(resolve(url).func, views.customer_favorite_venues)

    def test_customer_profile_management_url(self):
        """Test the customer profile management URL"""
        url = reverse('dashboard_app:customer_profile_management')
        self.assertEqual(url, '/dashboard/customer/profile/')
        self.assertEqual(resolve(url).func, views.customer_profile_management)

    def test_customer_review_history_url(self):
        """Test the customer review history URL"""
        url = reverse('dashboard_app:customer_review_history')
        self.assertEqual(url, '/dashboard/customer/reviews/')
        self.assertEqual(resolve(url).func, views.customer_review_history)

    # Service Provider Dashboard URLs
    def test_provider_dashboard_url(self):
        """Test the provider dashboard URL"""
        url = reverse('dashboard_app:provider_dashboard')
        self.assertEqual(url, '/dashboard/provider/')
        self.assertEqual(resolve(url).func, views.provider_dashboard)

    def test_provider_todays_bookings_url(self):
        """Test the provider today's bookings URL"""
        url = reverse('dashboard_app:provider_todays_bookings')
        self.assertEqual(url, '/dashboard/provider/todays-bookings/')
        self.assertEqual(resolve(url).func, views.provider_todays_bookings)

    def test_provider_revenue_reports_url(self):
        """Test the provider revenue reports URL"""
        url = reverse('dashboard_app:provider_revenue_reports')
        self.assertEqual(url, '/dashboard/provider/revenue/')
        self.assertEqual(resolve(url).func, views.provider_revenue_reports)

    def test_provider_service_performance_url(self):
        """Test the provider service performance URL"""
        url = reverse('dashboard_app:provider_service_performance')
        self.assertEqual(url, '/dashboard/provider/service-performance/')
        self.assertEqual(resolve(url).func, views.provider_service_performance)

    def test_provider_discount_performance_url(self):
        """Test the provider discount performance URL"""
        url = reverse('dashboard_app:provider_discount_performance')
        self.assertEqual(url, '/dashboard/provider/discount-performance/')
        self.assertEqual(resolve(url).func, views.provider_discount_performance)

    def test_provider_team_management_url(self):
        """Test the provider team management URL"""
        url = reverse('dashboard_app:provider_team_management')
        self.assertEqual(url, '/dashboard/provider/team/')
        self.assertEqual(resolve(url).func, views.provider_team_management)

    # Admin Dashboard URLs
    def test_admin_dashboard_url(self):
        """Test the admin dashboard URL"""
        url = reverse('dashboard_app:admin_dashboard')
        self.assertEqual(url, '/dashboard/admin/')
        self.assertEqual(resolve(url).func, views.admin_dashboard)

    def test_admin_platform_overview_url(self):
        """Test the admin platform overview URL"""
        url = reverse('dashboard_app:admin_platform_overview')
        self.assertEqual(url, '/dashboard/admin/platform-overview/')
        self.assertEqual(resolve(url).func, views.admin_platform_overview)

    def test_admin_user_statistics_url(self):
        """Test the admin user statistics URL"""
        url = reverse('dashboard_app:admin_user_statistics')
        self.assertEqual(url, '/dashboard/admin/user-statistics/')
        self.assertEqual(resolve(url).func, views.admin_user_statistics)

    def test_admin_booking_analytics_url(self):
        """Test the admin booking analytics URL"""
        url = reverse('dashboard_app:admin_booking_analytics')
        self.assertEqual(url, '/dashboard/admin/booking-analytics/')
        self.assertEqual(resolve(url).func, views.admin_booking_analytics)

    def test_admin_revenue_tracking_url(self):
        """Test the admin revenue tracking URL"""
        url = reverse('dashboard_app:admin_revenue_tracking')
        self.assertEqual(url, '/dashboard/admin/revenue-tracking/')
        self.assertEqual(resolve(url).func, views.admin_revenue_tracking)

    def test_admin_system_health_url(self):
        """Test the admin system health URL"""
        url = reverse('dashboard_app:admin_system_health')
        self.assertEqual(url, '/dashboard/admin/system-health/')
        self.assertEqual(resolve(url).func, views.admin_system_health)
