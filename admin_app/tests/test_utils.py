from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from admin_app.utils import log_admin_activity, get_client_ip, get_admin_preference
from admin_app.models import AdminActivity, AdminPreference

User = get_user_model()

class AdminUtilsTest(TestCase):
    """Test the utility functions in the admin_app"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.preference = AdminPreference.objects.create(
            user=self.admin_user,
            theme='dark',
            sidebar_collapsed=True,
            show_quick_actions=False,
            items_per_page=50
        )
    
    def test_log_admin_activity(self):
        """Test the log_admin_activity function"""
        # Create a request
        request = self.factory.get('/super-admin/')
        request.user = self.admin_user
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Add session and messages to request
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Call the function
        log_admin_activity(
            request=request,
            action_type='create',
            target_model='User',
            target_id='1',
            description='Created a new user'
        )
        
        # Check that an activity was created
        activity = AdminActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.user, self.admin_user)
        self.assertEqual(activity.action_type, 'create')
        self.assertEqual(activity.target_model, 'User')
        self.assertEqual(activity.target_id, '1')
        self.assertEqual(activity.description, 'Created a new user')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertEqual(activity.user_agent, 'Test User Agent')
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test the get_client_ip function with X-Forwarded-For header"""
        # Create a request with X-Forwarded-For header
        request = self.factory.get('/super-admin/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        # Call the function
        ip = get_client_ip(request)
        
        # Check that the correct IP was returned
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_with_remote_addr(self):
        """Test the get_client_ip function with REMOTE_ADDR"""
        # Create a request with REMOTE_ADDR
        request = self.factory.get('/super-admin/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Call the function
        ip = get_client_ip(request)
        
        # Check that the correct IP was returned
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_admin_preference_existing(self):
        """Test the get_admin_preference function with existing preference"""
        # Call the function
        preference = get_admin_preference(self.admin_user)
        
        # Check that the correct preference was returned
        self.assertEqual(preference, self.preference)
    
    def test_get_admin_preference_new(self):
        """Test the get_admin_preference function with new preference"""
        # Create a new user
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Call the function
        preference = get_admin_preference(user)
        
        # Check that a new preference was created
        self.assertIsNotNone(preference)
        self.assertEqual(preference.user, user)
        self.assertEqual(preference.theme, 'light')  # Default value
        self.assertFalse(preference.sidebar_collapsed)  # Default value
        self.assertTrue(preference.show_quick_actions)  # Default value
        self.assertEqual(preference.items_per_page, 20)  # Default value
