from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from admin_app.models import (
    AdminPreference, AdminActivity, AdminTask,
    SystemConfig, AuditLog, SecurityEvent
)
from venues_app.models import Venue, Category
from admin_app.forms import (AdminUserCreationForm, AdminUserChangeForm, BulkUserActionForm,
                          SystemConfigForm, SecurityEventResolveForm, DateRangeForm)

User = get_user_model()

class AdminAuthViewsTest(TestCase):
    """Test the admin authentication views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_login_url = reverse('admin_app:admin_login')
        self.admin_logout_url = reverse('admin_app:admin_logout')
        self.admin_dashboard_url = reverse('admin_app:admin_dashboard')

        # Create users
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

    def test_admin_login_view_get(self):
        """Test that the admin login view returns a 200 response"""
        response = self.client.get(self.admin_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/login.html')

    def test_admin_login_view_post_admin_valid(self):
        """Test valid admin login"""
        response = self.client.post(self.admin_login_url, {
            'username': 'admin@example.com',
            'password': 'testpass123',
        })
        self.assertRedirects(response, self.admin_dashboard_url)

        # Check that the user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_superuser)

    def test_admin_login_view_post_staff_valid(self):
        """Test valid staff login"""
        response = self.client.post(self.admin_login_url, {
            'username': 'staff@example.com',
            'password': 'testpass123',
        })
        self.assertRedirects(response, self.admin_dashboard_url)

        # Check that the user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_staff)

    def test_admin_login_view_post_regular_user_invalid(self):
        """Test that regular users cannot log in to admin"""
        response = self.client.post(self.admin_login_url, {
            'username': 'user@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertTemplateUsed(response, 'admin_app/login.html')

        # Check that the user is not logged in
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_admin_login_view_post_invalid_credentials(self):
        """Test invalid login credentials"""
        response = self.client.post(self.admin_login_url, {
            'username': 'admin@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertTemplateUsed(response, 'admin_app/login.html')

        # Check that the user is not logged in
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_admin_logout_view(self):
        """Test admin logout"""
        # Login first
        self.client.login(username='admin@example.com', password='testpass123')

        # Then logout
        response = self.client.get(self.admin_logout_url)
        self.assertRedirects(response, self.admin_login_url)

        # Check that the user is logged out
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_admin_dashboard_view_admin_access(self):
        """Test that admin users can access the dashboard"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Access dashboard
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/dashboard.html')

    def test_admin_dashboard_view_staff_access(self):
        """Test that staff users can access the dashboard"""
        # Login as staff
        self.client.login(username='staff@example.com', password='testpass123')

        # Access dashboard
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/dashboard.html')

    def test_admin_dashboard_view_regular_user_no_access(self):
        """Test that regular users cannot access the dashboard"""
        # Login as regular user
        self.client.login(username='user@example.com', password='testpass123')

        # Try to access dashboard
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_admin_dashboard_view_unauthenticated_no_access(self):
        """Test that unauthenticated users cannot access the dashboard"""
        # Try to access dashboard without login
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login


class AdminDashboardViewTest(TestCase):
    """Test the admin dashboard view content"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_dashboard_url = reverse('admin_app:admin_dashboard')

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create admin preference
        self.preference = AdminPreference.objects.create(
            user=self.admin_user,
            theme='dark',
            sidebar_collapsed=True
        )

        # Create system config
        self.config = SystemConfig.objects.create(
            maintenance_mode=True,
            last_updated_by=self.admin_user
        )

        # Create some users
        for i in range(5):
            User.objects.create_user(
                email=f'customer{i}@example.com',
                password='testpass123',
                is_customer=True
            )

        for i in range(3):
            User.objects.create_user(
                email=f'provider{i}@example.com',
                password='testpass123',
                is_service_provider=True
            )

        # Create some venues
        category = Category.objects.create(name='Spa', slug='spa')

        for i in range(3):
            Venue.objects.create(
                name=f'Test Venue {i}',
                slug=f'test-venue-{i}',
                description=f'Description for Test Venue {i}',
                owner=User.objects.get(email=f'provider{i}@example.com'),
                category=category,
                approval_status='approved'
            )

        # Create a pending venue
        Venue.objects.create(
            name='Pending Venue',
            slug='pending-venue',
            description='Description for Pending Venue',
            owner=User.objects.get(email='provider0@example.com'),
            category=category,
            approval_status='pending'
        )

        # Create some tasks
        for i in range(3):
            AdminTask.objects.create(
                title=f'Test Task {i}',
                description=f'Description for Test Task {i}',
                created_by=self.admin_user,
                assigned_to=self.admin_user,
                priority='high',
                status='pending'
            )

        # Create some security events
        for i in range(2):
            SecurityEvent.objects.create(
                user=self.admin_user,
                event_type='failed_login',
                severity='warning',
                description=f'Failed login attempt {i}'
            )

        # Create some admin activities
        for i in range(5):
            AdminActivity.objects.create(
                user=self.admin_user,
                action_type='view',
                target_model='User',
                target_id=str(i),
                description=f'Viewed user {i}'
            )

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_dashboard_context_data(self):
        """Test that the dashboard view provides the correct context data"""
        response = self.client.get(self.admin_dashboard_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/dashboard.html')

        # Check context data
        self.assertEqual(response.context['preference'], self.preference)
        self.assertEqual(response.context['system_config'], self.config)
        self.assertEqual(response.context['total_users'], 9)  # 5 customers + 3 providers + 1 admin
        self.assertEqual(response.context['customer_count'], 5)
        self.assertEqual(response.context['provider_count'], 3)
        self.assertEqual(response.context['total_venues'], 4)  # 3 approved + 1 pending
        self.assertEqual(response.context['pending_venues'], 1)
        self.assertEqual(response.context['approved_venues'], 3)
        self.assertEqual(len(response.context['pending_tasks']), 3)
        self.assertEqual(len(response.context['unresolved_security_events']), 2)
        self.assertEqual(len(response.context['recent_activities']), 5)
        self.assertEqual(len(response.context['pending_venue_approvals']), 1)


class AdminUserManagementViewsTest(TestCase):
    """Test the admin user management views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create regular users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            is_service_provider=True
        )

        # URLs
        self.user_list_url = reverse('admin_app:user_list')
        self.user_create_url = reverse('admin_app:user_create')
        self.user_detail_url = lambda user_id: reverse('admin_app:user_detail', kwargs={'user_id': user_id})
        self.user_edit_url = lambda user_id: reverse('admin_app:user_edit', kwargs={'user_id': user_id})
        self.user_delete_url = lambda user_id: reverse('admin_app:user_delete', kwargs={'user_id': user_id})
        self.user_bulk_actions_url = reverse('admin_app:user_bulk_actions')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_user_list_view(self):
        """Test the user list view"""
        response = self.client.get(self.user_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_list.html')

        # Check context data
        self.assertEqual(len(response.context['users']), 3)  # admin, customer, provider

        # Test filtering
        response = self.client.get(self.user_list_url + '?role=customer')
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], self.customer)

        response = self.client.get(self.user_list_url + '?role=service_provider')
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], self.provider)

        # Test search
        response = self.client.get(self.user_list_url + '?search=john')
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], self.customer)

        response = self.client.get(self.user_list_url + '?search=jane')
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], self.provider)

    def test_user_create_view_get(self):
        """Test the user create view GET request"""
        response = self.client.get(self.user_create_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_form.html')

        # Check form in context
        self.assertIsInstance(response.context['form'], AdminUserCreationForm)

    def test_user_create_view_post_valid(self):
        """Test the user create view with valid POST data"""
        response = self.client.post(self.user_create_url, {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_staff': True,
            'is_customer': True
        })

        # Check redirect
        self.assertRedirects(response, self.user_list_url)

        # Check that user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        new_user = User.objects.get(email='newuser@example.com')
        self.assertTrue(new_user.is_staff)
        self.assertTrue(new_user.is_customer)
        self.assertFalse(new_user.is_superuser)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='create',
            target_model='User',
            target_id=str(new_user.id)
        ).exists())

    def test_user_create_view_post_invalid(self):
        """Test the user create view with invalid POST data"""
        response = self.client.post(self.user_create_url, {
            'email': 'invalid-email',  # Invalid email
            'password1': 'testpass123',
            'password2': 'different-password',  # Passwords don't match
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_form.html')

        # Check form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('password2', response.context['form'].errors)

        # Check that user was not created
        self.assertFalse(User.objects.filter(email='invalid-email').exists())

    def test_user_detail_view(self):
        """Test the user detail view"""
        response = self.client.get(self.user_detail_url(self.customer.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_detail.html')

        # Check context data
        self.assertEqual(response.context['user_obj'], self.customer)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='view',
            target_model='User',
            target_id=str(self.customer.id)
        ).exists())

    def test_user_edit_view_get(self):
        """Test the user edit view GET request"""
        response = self.client.get(self.user_edit_url(self.customer.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_form.html')

        # Check form in context
        self.assertIsInstance(response.context['form'], AdminUserChangeForm)
        self.assertEqual(response.context['form'].instance, self.customer)

    def test_user_edit_view_post_valid(self):
        """Test the user edit view with valid POST data"""
        response = self.client.post(self.user_edit_url(self.customer.id), {
            'email': 'customer@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
            'is_active': True,
            'is_staff': True,
            'is_customer': True,
            'is_service_provider': False
        })

        # Check redirect
        self.assertRedirects(response, self.user_detail_url(self.customer.id))

        # Check that user was updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Updated')
        self.assertEqual(self.customer.last_name, 'Name')
        self.assertTrue(self.customer.is_staff)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='User',
            target_id=str(self.customer.id)
        ).exists())

    def test_user_edit_view_post_invalid(self):
        """Test the user edit view with invalid POST data"""
        response = self.client.post(self.user_edit_url(self.customer.id), {
            'email': 'invalid-email',  # Invalid email
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_form.html')

        # Check form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)

        # Check that user was not updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.email, 'customer@example.com')  # Unchanged

    def test_user_delete_view_get(self):
        """Test the user delete view GET request"""
        response = self.client.get(self.user_delete_url(self.customer.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_confirm_delete.html')

        # Check context data
        self.assertEqual(response.context['user_obj'], self.customer)

    def test_user_delete_view_post(self):
        """Test the user delete view POST request"""
        response = self.client.post(self.user_delete_url(self.customer.id))

        # Check redirect
        self.assertRedirects(response, self.user_list_url)

        # Check that user was deleted (or deactivated)
        self.assertFalse(User.objects.filter(id=self.customer.id, is_active=True).exists())

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='delete',
            target_model='User',
            target_id=str(self.customer.id)
        ).exists())

    def test_user_bulk_actions_view_activate(self):
        """Test the user bulk actions view with activate action"""
        # Deactivate users first
        self.customer.is_active = False
        self.customer.save()
        self.provider.is_active = False
        self.provider.save()

        response = self.client.post(self.user_bulk_actions_url, {
            'user_ids': f'{self.customer.id},{self.provider.id}',
            'action': 'activate'
        })

        # Check redirect
        self.assertRedirects(response, self.user_list_url)

        # Check that users were activated
        self.customer.refresh_from_db()
        self.provider.refresh_from_db()
        self.assertTrue(self.customer.is_active)
        self.assertTrue(self.provider.is_active)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='bulk_update',
            target_model='User',
            description__contains='activate'
        ).exists())

    def test_user_bulk_actions_view_deactivate(self):
        """Test the user bulk actions view with deactivate action"""
        response = self.client.post(self.user_bulk_actions_url, {
            'user_ids': f'{self.customer.id},{self.provider.id}',
            'action': 'deactivate'
        })

        # Check redirect
        self.assertRedirects(response, self.user_list_url)

        # Check that users were deactivated
        self.customer.refresh_from_db()
        self.provider.refresh_from_db()
        self.assertFalse(self.customer.is_active)
        self.assertFalse(self.provider.is_active)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='bulk_update',
            target_model='User',
            description__contains='deactivate'
        ).exists())


class AdminVenueManagementViewsTest(TestCase):
    """Test the admin venue management views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create provider user
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create category
        self.category = Category.objects.create(
            name='Spa',
            slug='spa'
        )

        # Create venues
        self.approved_venue = Venue.objects.create(
            name='Approved Venue',
            slug='approved-venue',
            description='Description for Approved Venue',
            owner=self.provider,
            category=self.category,
            approval_status='approved'
        )

        self.pending_venue = Venue.objects.create(
            name='Pending Venue',
            slug='pending-venue',
            description='Description for Pending Venue',
            owner=self.provider,
            category=self.category,
            approval_status='pending'
        )

        self.rejected_venue = Venue.objects.create(
            name='Rejected Venue',
            slug='rejected-venue',
            description='Description for Rejected Venue',
            owner=self.provider,
            category=self.category,
            approval_status='rejected',
            rejection_reason='Does not meet our standards'
        )

        # URLs
        self.venue_list_url = reverse('admin_app:venue_list')
        self.venue_detail_url = lambda venue_id: reverse('admin_app:venue_detail', kwargs={'venue_id': venue_id})
        self.venue_approval_url = lambda venue_id: reverse('admin_app:venue_approval', kwargs={'venue_id': venue_id})
        self.pending_venues_url = reverse('admin_app:pending_venues')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_venue_list_view(self):
        """Test the venue list view"""
        response = self.client.get(self.venue_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/venue_list.html')

        # Check context data
        self.assertEqual(len(response.context['venues']), 3)  # approved, pending, rejected

        # Test filtering by status
        response = self.client.get(self.venue_list_url + '?status=approved')
        self.assertEqual(len(response.context['venues']), 1)
        self.assertEqual(response.context['venues'][0], self.approved_venue)

        response = self.client.get(self.venue_list_url + '?status=pending')
        self.assertEqual(len(response.context['venues']), 1)
        self.assertEqual(response.context['venues'][0], self.pending_venue)

        response = self.client.get(self.venue_list_url + '?status=rejected')
        self.assertEqual(len(response.context['venues']), 1)
        self.assertEqual(response.context['venues'][0], self.rejected_venue)

        # Test search
        response = self.client.get(self.venue_list_url + '?search=approved')
        self.assertEqual(len(response.context['venues']), 1)
        self.assertEqual(response.context['venues'][0], self.approved_venue)

    def test_venue_detail_view(self):
        """Test the venue detail view"""
        response = self.client.get(self.venue_detail_url(self.approved_venue.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/venue_detail.html')

        # Check context data
        self.assertEqual(response.context['venue'], self.approved_venue)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='view',
            target_model='Venue',
            target_id=str(self.approved_venue.id)
        ).exists())

    def test_venue_approval_view_get(self):
        """Test the venue approval view GET request"""
        response = self.client.get(self.venue_approval_url(self.pending_venue.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/venue_approval.html')

        # Check context data
        self.assertEqual(response.context['venue'], self.pending_venue)

    def test_venue_approval_view_post_approve(self):
        """Test the venue approval view with approve action"""
        response = self.client.post(self.venue_approval_url(self.pending_venue.id), {
            'action': 'approve'
        })

        # Check redirect
        self.assertRedirects(response, self.venue_detail_url(self.pending_venue.id))

        # Check that venue was approved
        self.pending_venue.refresh_from_db()
        self.assertEqual(self.pending_venue.approval_status, 'approved')

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='Venue',
            target_id=str(self.pending_venue.id),
            description__contains='approved'
        ).exists())

    def test_venue_approval_view_post_reject(self):
        """Test the venue approval view with reject action"""
        response = self.client.post(self.venue_approval_url(self.pending_venue.id), {
            'action': 'reject',
            'rejection_reason': 'Does not meet our standards'
        })

        # Check redirect
        self.assertRedirects(response, self.venue_detail_url(self.pending_venue.id))

        # Check that venue was rejected
        self.pending_venue.refresh_from_db()
        self.assertEqual(self.pending_venue.approval_status, 'rejected')
        self.assertEqual(self.pending_venue.rejection_reason, 'Does not meet our standards')

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='Venue',
            target_id=str(self.pending_venue.id),
            description__contains='rejected'
        ).exists())

    def test_venue_approval_view_post_reject_without_reason(self):
        """Test the venue approval view with reject action but no reason"""
        response = self.client.post(self.venue_approval_url(self.pending_venue.id), {
            'action': 'reject'
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/venue_approval.html')

        # Check form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('rejection_reason', response.context['form'].errors)

        # Check that venue was not rejected
        self.pending_venue.refresh_from_db()
        self.assertEqual(self.pending_venue.approval_status, 'pending')  # Unchanged

    def test_pending_venues_view(self):
        """Test the pending venues view"""
        response = self.client.get(self.pending_venues_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/pending_venues.html')

        # Check context data
        self.assertEqual(len(response.context['venues']), 1)
        self.assertEqual(response.context['venues'][0], self.pending_venue)


class AdminSystemConfigViewTest(TestCase):
    """Test the admin system configuration view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create system config
        self.config = SystemConfig.objects.create(
            maintenance_mode=False,
            registration_enabled=True,
            max_login_attempts=5,
            login_lockout_duration=30,
            password_expiry_days=90,
            session_timeout_minutes=30,
            enable_two_factor_auth=False,
            last_updated_by=self.admin_user
        )

        # URL
        self.system_config_url = reverse('admin_app:system_config')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_system_config_view_get(self):
        """Test the system config view GET request"""
        response = self.client.get(self.system_config_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/system_config.html')

        # Check form in context
        self.assertIsInstance(response.context['form'], SystemConfigForm)
        self.assertEqual(response.context['form'].instance, self.config)

    def test_system_config_view_post_valid(self):
        """Test the system config view with valid POST data"""
        response = self.client.post(self.system_config_url, {
            'maintenance_mode': True,
            'maintenance_message': 'System is under maintenance',
            'registration_enabled': False,
            'max_login_attempts': 3,
            'login_lockout_duration': 60,
            'password_expiry_days': 30,
            'session_timeout_minutes': 15,
            'enable_two_factor_auth': True
        })

        # Check redirect
        self.assertRedirects(response, self.system_config_url)

        # Check that config was updated
        self.config.refresh_from_db()
        self.assertTrue(self.config.maintenance_mode)
        self.assertEqual(self.config.maintenance_message, 'System is under maintenance')
        self.assertFalse(self.config.registration_enabled)
        self.assertEqual(self.config.max_login_attempts, 3)
        self.assertEqual(self.config.login_lockout_duration, 60)
        self.assertEqual(self.config.password_expiry_days, 30)
        self.assertEqual(self.config.session_timeout_minutes, 15)
        self.assertTrue(self.config.enable_two_factor_auth)
        self.assertEqual(self.config.last_updated_by, self.admin_user)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='SystemConfig'
        ).exists())

    def test_system_config_view_post_invalid(self):
        """Test the system config view with invalid POST data"""
        response = self.client.post(self.system_config_url, {
            'max_login_attempts': 'invalid',  # Should be an integer
            'login_lockout_duration': -1,  # Should be positive
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/system_config.html')

        # Check form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('max_login_attempts', response.context['form'].errors)
        self.assertIn('login_lockout_duration', response.context['form'].errors)

        # Check that config was not updated
        self.config.refresh_from_db()
        self.assertEqual(self.config.max_login_attempts, 5)  # Unchanged
        self.assertEqual(self.config.login_lockout_duration, 30)  # Unchanged


class AdminAuditLogViewsTest(TestCase):
    """Test the admin audit log views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create audit logs
        for i in range(5):
            AuditLog.objects.create(
                user=self.admin_user,
                action='create',
                resource_type='User',
                resource_id=str(i),
                details=f'Created user {i}',
                ip_address='127.0.0.1'
            )

        # URLs
        self.audit_log_list_url = reverse('admin_app:audit_log_list')
        self.audit_log_detail_url = lambda log_id: reverse('admin_app:audit_log_detail', kwargs={'log_id': log_id})
        self.export_audit_logs_url = reverse('admin_app:export_audit_logs')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_audit_log_list_view(self):
        """Test the audit log list view"""
        response = self.client.get(self.audit_log_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/audit_log_list.html')

        # Check context data
        self.assertEqual(len(response.context['audit_logs']), 5)

        # Test filtering by action
        response = self.client.get(self.audit_log_list_url + '?action=create')
        self.assertEqual(len(response.context['audit_logs']), 5)

        response = self.client.get(self.audit_log_list_url + '?action=update')
        self.assertEqual(len(response.context['audit_logs']), 0)

        # Test filtering by resource type
        response = self.client.get(self.audit_log_list_url + '?resource_type=User')
        self.assertEqual(len(response.context['audit_logs']), 5)

        response = self.client.get(self.audit_log_list_url + '?resource_type=Venue')
        self.assertEqual(len(response.context['audit_logs']), 0)

        # Test search
        response = self.client.get(self.audit_log_list_url + '?search=Created')
        self.assertEqual(len(response.context['audit_logs']), 5)

        response = self.client.get(self.audit_log_list_url + '?search=Updated')
        self.assertEqual(len(response.context['audit_logs']), 0)

    def test_audit_log_detail_view(self):
        """Test the audit log detail view"""
        audit_log = AuditLog.objects.first()
        response = self.client.get(self.audit_log_detail_url(audit_log.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/audit_log_detail.html')

        # Check context data
        self.assertEqual(response.context['audit_log'], audit_log)

    def test_export_audit_logs_view(self):
        """Test the export audit logs view"""
        response = self.client.get(self.export_audit_logs_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="audit_logs.csv"'
        )

        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('User ID,Action,Resource Type,Resource ID,Details,IP Address,Timestamp', content)
        for i in range(5):
            self.assertIn(f'admin@example.com,create,User,{i},Created user {i},127.0.0.1', content)


class AdminSecurityMonitoringViewsTest(TestCase):
    """Test the admin security monitoring views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create regular user
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        # Create security events
        self.unresolved_event = SecurityEvent.objects.create(
            user=self.user,
            event_type='failed_login',
            severity='warning',
            description='Failed login attempt',
            ip_address='127.0.0.1'
        )

        self.resolved_event = SecurityEvent.objects.create(
            user=self.user,
            event_type='suspicious_activity',
            severity='critical',
            description='Suspicious activity detected',
            ip_address='127.0.0.1',
            is_resolved=True,
            resolved_by=self.admin_user,
            resolved_at=timezone.now(),
            resolution_notes='Issue investigated and resolved'
        )

        # URLs
        self.security_event_list_url = reverse('admin_app:security_event_list')
        self.security_event_detail_url = lambda event_id: reverse('admin_app:security_event_detail', kwargs={'event_id': event_id})
        self.security_event_resolve_url = lambda event_id: reverse('admin_app:security_event_resolve', kwargs={'event_id': event_id})

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_security_event_list_view(self):
        """Test the security event list view"""
        response = self.client.get(self.security_event_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/security_event_list.html')

        # Check context data
        self.assertEqual(len(response.context['security_events']), 2)  # unresolved and resolved

        # Test filtering by status
        response = self.client.get(self.security_event_list_url + '?status=unresolved')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.unresolved_event)

        response = self.client.get(self.security_event_list_url + '?status=resolved')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.resolved_event)

        # Test filtering by severity
        response = self.client.get(self.security_event_list_url + '?severity=warning')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.unresolved_event)

        response = self.client.get(self.security_event_list_url + '?severity=critical')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.resolved_event)

        # Test filtering by event type
        response = self.client.get(self.security_event_list_url + '?event_type=failed_login')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.unresolved_event)

        response = self.client.get(self.security_event_list_url + '?event_type=suspicious_activity')
        self.assertEqual(len(response.context['security_events']), 1)
        self.assertEqual(response.context['security_events'][0], self.resolved_event)

    def test_security_event_detail_view(self):
        """Test the security event detail view"""
        response = self.client.get(self.security_event_detail_url(self.unresolved_event.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/security_event_detail.html')

        # Check context data
        self.assertEqual(response.context['security_event'], self.unresolved_event)

    def test_security_event_resolve_view_get(self):
        """Test the security event resolve view GET request"""
        response = self.client.get(self.security_event_resolve_url(self.unresolved_event.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/security_event_resolve.html')

        # Check context data
        self.assertEqual(response.context['security_event'], self.unresolved_event)
        self.assertIsInstance(response.context['form'], SecurityEventResolveForm)

    def test_security_event_resolve_view_post_valid(self):
        """Test the security event resolve view with valid POST data"""
        response = self.client.post(self.security_event_resolve_url(self.unresolved_event.id), {
            'resolution_notes': 'Issue investigated and resolved'
        })

        # Check redirect
        self.assertRedirects(response, self.security_event_detail_url(self.unresolved_event.id))

        # Check that security event was resolved
        self.unresolved_event.refresh_from_db()
        self.assertTrue(self.unresolved_event.is_resolved)
        self.assertEqual(self.unresolved_event.resolved_by, self.admin_user)
        self.assertIsNotNone(self.unresolved_event.resolved_at)
        self.assertEqual(self.unresolved_event.resolution_notes, 'Issue investigated and resolved')

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='SecurityEvent',
            target_id=str(self.unresolved_event.id),
            description__contains='resolved'
        ).exists())

    def test_security_event_resolve_view_post_invalid(self):
        """Test the security event resolve view with invalid POST data"""
        response = self.client.post(self.security_event_resolve_url(self.unresolved_event.id), {
            'resolution_notes': ''  # Empty notes
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/security_event_resolve.html')

        # Check form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('resolution_notes', response.context['form'].errors)

        # Check that security event was not resolved
        self.unresolved_event.refresh_from_db()
        self.assertFalse(self.unresolved_event.is_resolved)
        self.assertIsNone(self.unresolved_event.resolved_by)
        self.assertIsNone(self.unresolved_event.resolved_at)
        self.assertEqual(self.unresolved_event.resolution_notes, '')

    def test_security_event_resolve_view_already_resolved(self):
        """Test the security event resolve view with already resolved event"""
        response = self.client.get(self.security_event_resolve_url(self.resolved_event.id))

        # Check redirect
        self.assertRedirects(response, self.security_event_detail_url(self.resolved_event.id))


class AdminTaskManagementViewsTest(TestCase):
    """Test the admin task management views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )

        # Create tasks
        self.pending_task = AdminTask.objects.create(
            title='Pending Task',
            description='This is a pending task',
            created_by=self.admin_user,
            assigned_to=self.staff_user,
            priority='high',
            status='pending',
            due_date=timezone.now() + timedelta(days=7)
        )

        self.in_progress_task = AdminTask.objects.create(
            title='In Progress Task',
            description='This is a task in progress',
            created_by=self.admin_user,
            assigned_to=self.admin_user,
            priority='medium',
            status='in_progress',
            due_date=timezone.now() + timedelta(days=3)
        )

        self.completed_task = AdminTask.objects.create(
            title='Completed Task',
            description='This is a completed task',
            created_by=self.admin_user,
            assigned_to=self.staff_user,
            priority='low',
            status='completed',
            due_date=timezone.now() - timedelta(days=1),
            completed_at=timezone.now()
        )

        # URLs
        self.task_list_url = reverse('admin_app:task_list')
        self.task_create_url = reverse('admin_app:task_create')
        self.task_detail_url = lambda task_id: reverse('admin_app:task_detail', kwargs={'task_id': task_id})
        self.task_edit_url = lambda task_id: reverse('admin_app:task_edit', kwargs={'task_id': task_id})
        self.task_delete_url = lambda task_id: reverse('admin_app:task_delete', kwargs={'task_id': task_id})
        self.task_update_status_url = lambda task_id: reverse('admin_app:task_update_status', kwargs={'task_id': task_id})
        self.task_mark_completed_url = lambda task_id: reverse('admin_app:task_mark_completed', kwargs={'task_id': task_id})
        self.task_mark_cancelled_url = lambda task_id: reverse('admin_app:task_mark_cancelled', kwargs={'task_id': task_id})

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_task_list_view(self):
        """Test the task list view"""
        response = self.client.get(self.task_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/task_list.html')

        # Check context data
        self.assertEqual(len(response.context['tasks']), 3)  # pending, in_progress, completed

        # Test filtering by status
        response = self.client.get(self.task_list_url + '?status=pending')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.pending_task)

        response = self.client.get(self.task_list_url + '?status=in_progress')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.in_progress_task)

        response = self.client.get(self.task_list_url + '?status=completed')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.completed_task)

        # Test filtering by priority
        response = self.client.get(self.task_list_url + '?priority=high')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.pending_task)

        response = self.client.get(self.task_list_url + '?priority=medium')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.in_progress_task)

        # Test filtering by assigned_to
        response = self.client.get(self.task_list_url + f'?assigned_to={self.staff_user.id}')
        self.assertEqual(len(response.context['tasks']), 2)  # pending and completed

        response = self.client.get(self.task_list_url + f'?assigned_to={self.admin_user.id}')
        self.assertEqual(len(response.context['tasks']), 1)  # in_progress
        self.assertEqual(response.context['tasks'][0], self.in_progress_task)

    def test_task_create_view_get(self):
        """Test the task create view GET request"""
        response = self.client.get(self.task_create_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/task_form.html')

    def test_task_create_view_post_valid(self):
        """Test the task create view with valid POST data"""
        response = self.client.post(self.task_create_url, {
            'title': 'New Task',
            'description': 'This is a new task',
            'assigned_to': self.staff_user.id,
            'due_date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
            'priority': 'high',
            'status': 'pending'
        })

        # Check redirect
        self.assertRedirects(response, self.task_list_url)

        # Check that task was created
        self.assertTrue(AdminTask.objects.filter(title='New Task').exists())
        new_task = AdminTask.objects.get(title='New Task')
        self.assertEqual(new_task.description, 'This is a new task')
        self.assertEqual(new_task.assigned_to, self.staff_user)
        self.assertEqual(new_task.priority, 'high')
        self.assertEqual(new_task.status, 'pending')
        self.assertEqual(new_task.created_by, self.admin_user)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='create',
            target_model='AdminTask',
            target_id=str(new_task.id)
        ).exists())

    def test_task_detail_view(self):
        """Test the task detail view"""
        response = self.client.get(self.task_detail_url(self.pending_task.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/task_detail.html')

        # Check context data
        self.assertEqual(response.context['task'], self.pending_task)

    def test_task_edit_view_get(self):
        """Test the task edit view GET request"""
        response = self.client.get(self.task_edit_url(self.pending_task.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/task_form.html')

    def test_task_edit_view_post_valid(self):
        """Test the task edit view with valid POST data"""
        response = self.client.post(self.task_edit_url(self.pending_task.id), {
            'title': 'Updated Task',
            'description': 'This is an updated task',
            'assigned_to': self.admin_user.id,
            'due_date': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M'),
            'priority': 'medium',
            'status': 'in_progress'
        })

        # Check redirect
        self.assertRedirects(response, self.task_detail_url(self.pending_task.id))

        # Check that task was updated
        self.pending_task.refresh_from_db()
        self.assertEqual(self.pending_task.title, 'Updated Task')
        self.assertEqual(self.pending_task.description, 'This is an updated task')
        self.assertEqual(self.pending_task.assigned_to, self.admin_user)
        self.assertEqual(self.pending_task.priority, 'medium')
        self.assertEqual(self.pending_task.status, 'in_progress')

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='AdminTask',
            target_id=str(self.pending_task.id)
        ).exists())

    def test_task_delete_view_get(self):
        """Test the task delete view GET request"""
        response = self.client.get(self.task_delete_url(self.pending_task.id))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/task_confirm_delete.html')

        # Check context data
        self.assertEqual(response.context['task'], self.pending_task)

    def test_task_delete_view_post(self):
        """Test the task delete view POST request"""
        response = self.client.post(self.task_delete_url(self.pending_task.id))

        # Check redirect
        self.assertRedirects(response, self.task_list_url)

        # Check that task was deleted
        self.assertFalse(AdminTask.objects.filter(id=self.pending_task.id).exists())

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='delete',
            target_model='AdminTask',
            target_id=str(self.pending_task.id)
        ).exists())

    def test_task_mark_completed_view(self):
        """Test the task mark completed view"""
        response = self.client.post(self.task_mark_completed_url(self.pending_task.id))

        # Check redirect
        self.assertRedirects(response, self.task_detail_url(self.pending_task.id))

        # Check that task was marked as completed
        self.pending_task.refresh_from_db()
        self.assertEqual(self.pending_task.status, 'completed')
        self.assertIsNotNone(self.pending_task.completed_at)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='AdminTask',
            target_id=str(self.pending_task.id),
            description__contains='completed'
        ).exists())

    def test_task_mark_cancelled_view(self):
        """Test the task mark cancelled view"""
        response = self.client.post(self.task_mark_cancelled_url(self.pending_task.id))

        # Check redirect
        self.assertRedirects(response, self.task_detail_url(self.pending_task.id))

        # Check that task was marked as cancelled
        self.pending_task.refresh_from_db()
        self.assertEqual(self.pending_task.status, 'cancelled')

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='AdminTask',
            target_id=str(self.pending_task.id),
            description__contains='cancelled'
        ).exists())


class AdminAnalyticsViewsTest(TestCase):
    """Test the admin analytics views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # URLs
        self.analytics_dashboard_url = reverse('admin_app:analytics_dashboard')
        self.user_report_url = reverse('admin_app:user_report')
        self.booking_report_url = reverse('admin_app:booking_report')
        self.revenue_report_url = reverse('admin_app:revenue_report')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_analytics_dashboard_view(self):
        """Test the analytics dashboard view"""
        response = self.client.get(self.analytics_dashboard_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/analytics_dashboard.html')

    def test_user_report_view(self):
        """Test the user report view"""
        response = self.client.get(self.user_report_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/user_report.html')

        # Test with date range
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        response = self.client.get(self.user_report_url + f'?start_date={yesterday.strftime("%Y-%m-%d")}&end_date={today.strftime("%Y-%m-%d")}')
        self.assertEqual(response.status_code, 200)

    def test_booking_report_view(self):
        """Test the booking report view"""
        response = self.client.get(self.booking_report_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/booking_report.html')

        # Test with date range
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        response = self.client.get(self.booking_report_url + f'?start_date={yesterday.strftime("%Y-%m-%d")}&end_date={today.strftime("%Y-%m-%d")}')
        self.assertEqual(response.status_code, 200)

    def test_revenue_report_view(self):
        """Test the revenue report view"""
        response = self.client.get(self.revenue_report_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/revenue_report.html')

        # Test with date range
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        response = self.client.get(self.revenue_report_url + f'?start_date={yesterday.strftime("%Y-%m-%d")}&end_date={today.strftime("%Y-%m-%d")}')
        self.assertEqual(response.status_code, 200)


class AdminPreferencesViewTest(TestCase):
    """Test the admin preferences view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create admin preference
        self.preference = AdminPreference.objects.create(
            user=self.admin_user,
            theme='light',
            sidebar_collapsed=False,
            show_quick_actions=True,
            items_per_page=20
        )

        # URL
        self.admin_preferences_url = reverse('admin_app:admin_preferences')

        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

    def test_admin_preferences_view_get(self):
        """Test the admin preferences view GET request"""
        response = self.client.get(self.admin_preferences_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/admin_preferences.html')

        # Check context data
        self.assertEqual(response.context['preference'], self.preference)

    def test_admin_preferences_view_post_valid(self):
        """Test the admin preferences view with valid POST data"""
        response = self.client.post(self.admin_preferences_url, {
            'theme': 'dark',
            'sidebar_collapsed': True,
            'show_quick_actions': False,
            'items_per_page': 50
        })

        # Check redirect
        self.assertRedirects(response, self.admin_preferences_url)

        # Check that preference was updated
        self.preference.refresh_from_db()
        self.assertEqual(self.preference.theme, 'dark')
        self.assertTrue(self.preference.sidebar_collapsed)
        self.assertFalse(self.preference.show_quick_actions)
        self.assertEqual(self.preference.items_per_page, 50)

        # Check that activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='AdminPreference'
        ).exists())

    def test_admin_preferences_view_post_invalid(self):
        """Test the admin preferences view with invalid POST data"""
        response = self.client.post(self.admin_preferences_url, {
            'theme': 'invalid_theme',  # Invalid theme
            'items_per_page': 'invalid'  # Should be an integer
        })

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_app/admin_preferences.html')

        # Check that preference was not updated
        self.preference.refresh_from_db()
        self.assertEqual(self.preference.theme, 'light')  # Unchanged
        self.assertEqual(self.preference.items_per_page, 20)  # Unchanged
