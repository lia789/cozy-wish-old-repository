from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from dashboard_app.models import DashboardPreference, DashboardWidget, UserWidget

User = get_user_model()


class DashboardPreferenceModelTest(TestCase):
    """Test the DashboardPreference model"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create preferences
        self.customer_preference = DashboardPreference.objects.create(
            user=self.customer,
            theme='dark',
            compact_view=True
        )
        
        self.provider_preference = DashboardPreference.objects.create(
            user=self.provider,
            theme='light',
            compact_view=False
        )
        
        self.admin_preference = DashboardPreference.objects.create(
            user=self.admin,
            theme='auto',
            compact_view=True
        )
    
    def test_dashboard_preference_creation(self):
        """Test creating a dashboard preference"""
        self.assertEqual(self.customer_preference.user, self.customer)
        self.assertEqual(self.customer_preference.theme, 'dark')
        self.assertTrue(self.customer_preference.compact_view)
        
        self.assertEqual(self.provider_preference.user, self.provider)
        self.assertEqual(self.provider_preference.theme, 'light')
        self.assertFalse(self.provider_preference.compact_view)
        
        self.assertEqual(self.admin_preference.user, self.admin)
        self.assertEqual(self.admin_preference.theme, 'auto')
        self.assertTrue(self.admin_preference.compact_view)
    
    def test_dashboard_preference_str(self):
        """Test the string representation of dashboard preference"""
        self.assertEqual(str(self.customer_preference), "customer@example.com's Dashboard Preferences")
        self.assertEqual(str(self.provider_preference), "provider@example.com's Dashboard Preferences")
        self.assertEqual(str(self.admin_preference), "admin@example.com's Dashboard Preferences")
    
    def test_dashboard_preference_unique_constraint(self):
        """Test that a user can only have one dashboard preference"""
        with self.assertRaises(IntegrityError):
            DashboardPreference.objects.create(
                user=self.customer,
                theme='light',
                compact_view=False
            )
    
    def test_dashboard_preference_default_values(self):
        """Test default values for dashboard preference"""
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123'
        )
        
        preference = DashboardPreference.objects.create(user=new_user)
        
        self.assertEqual(preference.theme, 'light')  # Default theme
        self.assertFalse(preference.compact_view)  # Default compact_view
    
    def test_dashboard_preference_update(self):
        """Test updating a dashboard preference"""
        self.customer_preference.theme = 'light'
        self.customer_preference.compact_view = False
        self.customer_preference.save()
        
        # Refresh from database
        self.customer_preference.refresh_from_db()
        
        self.assertEqual(self.customer_preference.theme, 'light')
        self.assertFalse(self.customer_preference.compact_view)


class DashboardWidgetModelTest(TestCase):
    """Test the DashboardWidget model"""
    
    def setUp(self):
        """Set up test data"""
        # Create widgets for different user types
        self.customer_widget = DashboardWidget.objects.create(
            name='Customer Stats',
            description='Shows customer statistics',
            widget_type='stats',
            template_name='dashboard_app/widgets/customer_stats.html',
            icon_class='fas fa-chart-bar',
            user_type='customer'
        )
        
        self.provider_widget = DashboardWidget.objects.create(
            name='Provider Revenue',
            description='Shows provider revenue',
            widget_type='chart',
            template_name='dashboard_app/widgets/provider_revenue.html',
            icon_class='fas fa-dollar-sign',
            user_type='provider'
        )
        
        self.admin_widget = DashboardWidget.objects.create(
            name='Admin Overview',
            description='Shows admin overview',
            widget_type='table',
            template_name='dashboard_app/widgets/admin_overview.html',
            icon_class='fas fa-table',
            user_type='admin'
        )
        
        self.all_widget = DashboardWidget.objects.create(
            name='Recent Activity',
            description='Shows recent activity',
            widget_type='list',
            template_name='dashboard_app/widgets/recent_activity.html',
            icon_class='fas fa-history',
            user_type='all'
        )
    
    def test_dashboard_widget_creation(self):
        """Test creating dashboard widgets"""
        self.assertEqual(self.customer_widget.name, 'Customer Stats')
        self.assertEqual(self.customer_widget.widget_type, 'stats')
        self.assertEqual(self.customer_widget.user_type, 'customer')
        self.assertTrue(self.customer_widget.is_active)
        
        self.assertEqual(self.provider_widget.name, 'Provider Revenue')
        self.assertEqual(self.provider_widget.widget_type, 'chart')
        self.assertEqual(self.provider_widget.user_type, 'provider')
        self.assertTrue(self.provider_widget.is_active)
        
        self.assertEqual(self.admin_widget.name, 'Admin Overview')
        self.assertEqual(self.admin_widget.widget_type, 'table')
        self.assertEqual(self.admin_widget.user_type, 'admin')
        self.assertTrue(self.admin_widget.is_active)
        
        self.assertEqual(self.all_widget.name, 'Recent Activity')
        self.assertEqual(self.all_widget.widget_type, 'list')
        self.assertEqual(self.all_widget.user_type, 'all')
        self.assertTrue(self.all_widget.is_active)
    
    def test_dashboard_widget_str(self):
        """Test the string representation of dashboard widget"""
        self.assertEqual(str(self.customer_widget), 'Customer Stats')
        self.assertEqual(str(self.provider_widget), 'Provider Revenue')
        self.assertEqual(str(self.admin_widget), 'Admin Overview')
        self.assertEqual(str(self.all_widget), 'Recent Activity')
    
    def test_dashboard_widget_deactivation(self):
        """Test deactivating a dashboard widget"""
        self.customer_widget.is_active = False
        self.customer_widget.save()
        
        # Refresh from database
        self.customer_widget.refresh_from_db()
        
        self.assertFalse(self.customer_widget.is_active)


class UserWidgetModelTest(TestCase):
    """Test the UserWidget model"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Widget 1',
            description='First widget',
            widget_type='stats',
            template_name='dashboard_app/widgets/widget1.html',
            icon_class='fas fa-chart-bar',
            user_type='all'
        )
        
        self.widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            description='Second widget',
            widget_type='chart',
            template_name='dashboard_app/widgets/widget2.html',
            icon_class='fas fa-chart-line',
            user_type='all'
        )
        
        self.widget3 = DashboardWidget.objects.create(
            name='Widget 3',
            description='Third widget',
            widget_type='table',
            template_name='dashboard_app/widgets/widget3.html',
            icon_class='fas fa-table',
            user_type='all'
        )
        
        # Create user widgets
        self.user_widget1 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )
        
        self.user_widget2 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget2,
            position=1,
            is_visible=True
        )
        
        self.user_widget3 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget3,
            position=2,
            is_visible=False
        )
    
    def test_user_widget_creation(self):
        """Test creating user widgets"""
        self.assertEqual(self.user_widget1.user, self.customer)
        self.assertEqual(self.user_widget1.widget, self.widget1)
        self.assertEqual(self.user_widget1.position, 0)
        self.assertTrue(self.user_widget1.is_visible)
        
        self.assertEqual(self.user_widget2.user, self.customer)
        self.assertEqual(self.user_widget2.widget, self.widget2)
        self.assertEqual(self.user_widget2.position, 1)
        self.assertTrue(self.user_widget2.is_visible)
        
        self.assertEqual(self.user_widget3.user, self.customer)
        self.assertEqual(self.user_widget3.widget, self.widget3)
        self.assertEqual(self.user_widget3.position, 2)
        self.assertFalse(self.user_widget3.is_visible)
    
    def test_user_widget_str(self):
        """Test the string representation of user widget"""
        self.assertEqual(str(self.user_widget1), "customer@example.com - Widget 1")
        self.assertEqual(str(self.user_widget2), "customer@example.com - Widget 2")
        self.assertEqual(str(self.user_widget3), "customer@example.com - Widget 3")
    
    def test_user_widget_ordering(self):
        """Test that user widgets are ordered by position"""
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets[0], self.user_widget1)
        self.assertEqual(user_widgets[1], self.user_widget2)
        self.assertEqual(user_widgets[2], self.user_widget3)
    
    def test_user_widget_unique_constraint(self):
        """Test that a user can only have one instance of each widget"""
        with self.assertRaises(IntegrityError):
            UserWidget.objects.create(
                user=self.customer,
                widget=self.widget1,
                position=3,
                is_visible=True
            )
    
    def test_user_widget_update(self):
        """Test updating a user widget"""
        self.user_widget1.position = 3
        self.user_widget1.is_visible = False
        self.user_widget1.save()
        
        # Refresh from database
        self.user_widget1.refresh_from_db()
        
        self.assertEqual(self.user_widget1.position, 3)
        self.assertFalse(self.user_widget1.is_visible)
    
    def test_user_widget_deletion_on_user_deletion(self):
        """Test that user widgets are deleted when the user is deleted"""
        # Count user widgets before deletion
        count_before = UserWidget.objects.filter(user=self.customer).count()
        self.assertEqual(count_before, 3)
        
        # Delete the user
        self.customer.delete()
        
        # Count user widgets after deletion
        count_after = UserWidget.objects.filter(user=self.customer).count()
        self.assertEqual(count_after, 0)
    
    def test_user_widget_deletion_on_widget_deletion(self):
        """Test that user widgets are deleted when the widget is deleted"""
        # Count user widgets before deletion
        count_before = UserWidget.objects.filter(widget=self.widget1).count()
        self.assertEqual(count_before, 1)
        
        # Delete the widget
        self.widget1.delete()
        
        # Count user widgets after deletion
        count_after = UserWidget.objects.filter(widget=self.widget1).count()
        self.assertEqual(count_after, 0)
