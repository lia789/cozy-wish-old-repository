from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from dashboard_app.models import DashboardWidget, UserWidget

User = get_user_model()


class CreateDefaultWidgetsCommandTest(TestCase):
    """Test the create_default_widgets management command"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
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
    
    def test_create_default_widgets(self):
        """Test creating default widgets"""
        # Call the command
        out = StringIO()
        call_command('create_default_widgets', stdout=out)
        
        # Check output
        self.assertIn('Creating default widgets...', out.getvalue())
        self.assertIn('Default widgets created successfully.', out.getvalue())
        
        # Check that widgets were created
        widgets = DashboardWidget.objects.all()
        self.assertGreater(widgets.count(), 0)
        
        # Check that there are widgets for each user type
        customer_widgets = DashboardWidget.objects.filter(user_type='customer')
        provider_widgets = DashboardWidget.objects.filter(user_type='provider')
        admin_widgets = DashboardWidget.objects.filter(user_type='admin')
        all_widgets = DashboardWidget.objects.filter(user_type='all')
        
        self.assertGreater(customer_widgets.count(), 0)
        self.assertGreater(provider_widgets.count(), 0)
        self.assertGreater(admin_widgets.count(), 0)
        self.assertGreater(all_widgets.count(), 0)


class ResetUserDashboardCommandTest(TestCase):
    """Test the reset_user_dashboard management command"""
    
    def setUp(self):
        """Set up test data"""
        # Create a customer
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
            user_type='customer'
        )
        
        self.widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            description='Second widget',
            widget_type='chart',
            template_name='dashboard_app/widgets/widget2.html',
            icon_class='fas fa-chart-line',
            user_type='customer'
        )
        
        # Add widgets to user
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
            is_visible=False
        )
    
    def test_reset_user_dashboard_specific_user(self):
        """Test resetting dashboard for a specific user"""
        # Call the command
        out = StringIO()
        call_command('reset_user_dashboard', user_email='customer@example.com', stdout=out)
        
        # Check output
        self.assertIn('Resetting dashboard for user: customer@example.com', out.getvalue())
        self.assertIn('User dashboard reset successfully.', out.getvalue())
        
        # Check that user widgets were removed
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 0)
    
    def test_reset_user_dashboard_all_users(self):
        """Test resetting dashboard for all users"""
        # Create another user with widgets
        provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        provider_widget = UserWidget.objects.create(
            user=provider,
            widget=self.widget1,
            position=0,
            is_visible=True
        )
        
        # Call the command
        out = StringIO()
        call_command('reset_user_dashboard', all_users=True, stdout=out)
        
        # Check output
        self.assertIn('Resetting dashboard for all users...', out.getvalue())
        self.assertIn('All user dashboards reset successfully.', out.getvalue())
        
        # Check that all user widgets were removed
        user_widgets = UserWidget.objects.all()
        self.assertEqual(user_widgets.count(), 0)
    
    def test_reset_user_dashboard_no_user(self):
        """Test resetting dashboard with no user specified"""
        # Call the command
        out = StringIO()
        err = StringIO()
        call_command('reset_user_dashboard', stdout=out, stderr=err)
        
        # Check error output
        self.assertIn('Error: Please specify a user email or use --all-users', err.getvalue())
        
        # Check that user widgets were not removed
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 2)
    
    def test_reset_user_dashboard_nonexistent_user(self):
        """Test resetting dashboard for a nonexistent user"""
        # Call the command
        out = StringIO()
        err = StringIO()
        call_command('reset_user_dashboard', user_email='nonexistent@example.com', stdout=out, stderr=err)
        
        # Check error output
        self.assertIn('Error: User with email nonexistent@example.com not found.', err.getvalue())
        
        # Check that user widgets were not removed
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 2)
