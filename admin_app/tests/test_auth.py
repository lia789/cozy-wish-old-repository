from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from admin_app.models import AdminActivity

User = get_user_model()

class AdminAuthTests(TestCase):
    def setUp(self):
        # Create a regular user
        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            password='password123',
            is_active=True
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='password123',
            is_active=True,
            is_staff=True
        )
        
        # Create a client
        self.client = Client()
        
    def test_admin_login_view_get(self):
        """Test that the admin login page loads correctly"""
        response = self.client.get(reverse('admin_app:admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/login.html')
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = self.client.post(reverse('admin_app:admin_login'), {
            'username': 'admin@example.com',
            'password': 'password123'
        })
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('admin_app:admin_dashboard'))
        
        # Check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.admin_user)
        
        # Check that an admin activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action='login'
        ).exists())
    
    def test_admin_login_failure_wrong_password(self):
        """Test admin login with wrong password"""
        response = self.client.post(reverse('admin_app:admin_login'), {
            'username': 'admin@example.com',
            'password': 'wrongpassword'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # Check that the user is not logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check for error message
        self.assertContains(response, 'Invalid username or password')
    
    def test_admin_login_failure_non_admin(self):
        """Test admin login with non-admin user"""
        response = self.client.post(reverse('admin_app:admin_login'), {
            'username': 'regular@example.com',
            'password': 'password123'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # Check that the user is not logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check for error message
        self.assertContains(response, 'Your account does not have admin privileges')
    
    def test_admin_logout(self):
        """Test admin logout"""
        # First login
        self.client.login(username='admin@example.com', password='password123')
        
        # Then logout
        response = self.client.get(reverse('admin_app:admin_logout'))
        
        # Should redirect to login page
        self.assertRedirects(response, reverse('admin_app:admin_login'))
        
        # Check that the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check that an admin activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action='logout'
        ).exists())
    
    def test_admin_dashboard_requires_login(self):
        """Test that the admin dashboard requires login"""
        response = self.client.get(reverse('admin_app:admin_dashboard'))
        
        # Should redirect to login page
        login_url = reverse('admin_app:admin_login')
        dashboard_url = reverse('admin_app:admin_dashboard')
        self.assertRedirects(response, f'{login_url}?next={dashboard_url}')
    
    def test_admin_dashboard_requires_staff(self):
        """Test that the admin dashboard requires staff status"""
        # Login as regular user
        self.client.login(username='regular@example.com', password='password123')
        
        # Try to access dashboard
        response = self.client.get(reverse('admin_app:admin_dashboard'))
        
        # Should redirect to login page (due to user_passes_test decorator)
        login_url = reverse('admin_app:admin_login')
        dashboard_url = reverse('admin_app:admin_dashboard')
        self.assertRedirects(response, f'{login_url}?next={dashboard_url}')
