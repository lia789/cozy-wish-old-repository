from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import DashboardPreference, DashboardWidget, UserWidget

User = get_user_model()


class DashboardAppTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            is_customer=True
        )
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpassword',
            is_service_provider=True
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpassword',
            is_staff=True
        )
        
        # Create test widgets
        self.customer_widget = DashboardWidget.objects.create(
            name='Test Customer Widget',
            description='A test widget for customers',
            widget_type='stats',
            template_name='test_template.html',
            icon_class='fas fa-test',
            user_type='customer'
        )
        
        self.provider_widget = DashboardWidget.objects.create(
            name='Test Provider Widget',
            description='A test widget for providers',
            widget_type='stats',
            template_name='test_template.html',
            icon_class='fas fa-test',
            user_type='provider'
        )
        
        self.admin_widget = DashboardWidget.objects.create(
            name='Test Admin Widget',
            description='A test widget for admins',
            widget_type='stats',
            template_name='test_template.html',
            icon_class='fas fa-test',
            user_type='admin'
        )
        
        self.all_widget = DashboardWidget.objects.create(
            name='Test All Widget',
            description='A test widget for all users',
            widget_type='stats',
            template_name='test_template.html',
            icon_class='fas fa-test',
            user_type='all'
        )
    
    def test_dashboard_redirect(self):
        """Test that users are redirected to the appropriate dashboard"""
        # Customer redirect
        self.client.login(email='customer@example.com', password='testpassword')
        response = self.client.get(reverse('dashboard_app:dashboard_redirect'))
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))
        
        # Provider redirect
        self.client.login(email='provider@example.com', password='testpassword')
        response = self.client.get(reverse('dashboard_app:dashboard_redirect'))
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))
        
        # Admin redirect
        self.client.login(email='admin@example.com', password='testpassword')
        response = self.client.get(reverse('dashboard_app:dashboard_redirect'))
        self.assertRedirects(response, reverse('dashboard_app:admin_dashboard'))
    
    def test_dashboard_preference_model(self):
        """Test the DashboardPreference model"""
        # Create a preference
        preference = DashboardPreference.objects.create(
            user=self.customer,
            theme='dark',
            compact_view=True
        )
        
        # Check that the preference was created correctly
        self.assertEqual(preference.user, self.customer)
        self.assertEqual(preference.theme, 'dark')
        self.assertTrue(preference.compact_view)
        
        # Check string representation
        self.assertEqual(str(preference), f"{self.customer.email}'s Dashboard Preferences")
    
    def test_dashboard_widget_model(self):
        """Test the DashboardWidget model"""
        # Check that the widgets were created correctly
        self.assertEqual(self.customer_widget.user_type, 'customer')
        self.assertEqual(self.provider_widget.user_type, 'provider')
        self.assertEqual(self.admin_widget.user_type, 'admin')
        self.assertEqual(self.all_widget.user_type, 'all')
        
        # Check string representation
        self.assertEqual(str(self.customer_widget), 'Test Customer Widget')
    
    def test_user_widget_model(self):
        """Test the UserWidget model"""
        # Create a user widget
        user_widget = UserWidget.objects.create(
            user=self.customer,
            widget=self.customer_widget,
            position=0,
            is_visible=True
        )
        
        # Check that the user widget was created correctly
        self.assertEqual(user_widget.user, self.customer)
        self.assertEqual(user_widget.widget, self.customer_widget)
        self.assertEqual(user_widget.position, 0)
        self.assertTrue(user_widget.is_visible)
        
        # Check string representation
        self.assertEqual(str(user_widget), f"{self.customer.email} - Test Customer Widget")
