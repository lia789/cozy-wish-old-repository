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

User = get_user_model()

class AdminIntegrationTest(TestCase):
    """Integration tests for admin workflows"""
    
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
        
        # Create category
        self.category = Category.objects.create(
            name='Spa',
            slug='spa'
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            slug='test-venue',
            description='Description for Test Venue',
            owner=self.provider,
            category=self.category,
            approval_status='pending'
        )
        
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
    
    def test_venue_approval_workflow(self):
        """Test the complete venue approval workflow"""
        # 1. Admin views pending venues
        pending_venues_url = reverse('admin_app:pending_venues')
        response = self.client.get(pending_venues_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['venues']), 1)
        
        # 2. Admin views venue details
        venue_detail_url = reverse('admin_app:venue_detail', kwargs={'venue_id': self.venue.id})
        response = self.client.get(venue_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['venue'], self.venue)
        
        # 3. Admin approves venue
        venue_approval_url = reverse('admin_app:venue_approval', kwargs={'venue_id': self.venue.id})
        response = self.client.post(venue_approval_url, {
            'action': 'approve'
        })
        self.assertRedirects(response, venue_detail_url)
        
        # 4. Verify venue is now approved
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.approval_status, 'approved')
        
        # 5. Verify activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='Venue',
            target_id=str(self.venue.id),
            description__contains='approved'
        ).exists())
        
        # 6. Verify venue no longer appears in pending venues
        response = self.client.get(pending_venues_url)
        self.assertEqual(len(response.context['venues']), 0)
    
    def test_user_management_workflow(self):
        """Test the complete user management workflow"""
        # 1. Admin views user list
        user_list_url = reverse('admin_app:user_list')
        response = self.client.get(user_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 3)  # admin, customer, provider
        
        # 2. Admin creates a new user
        user_create_url = reverse('admin_app:user_create')
        response = self.client.post(user_create_url, {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_staff': True,
            'is_customer': True
        })
        self.assertRedirects(response, user_list_url)
        
        # 3. Verify new user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        new_user = User.objects.get(email='newuser@example.com')
        
        # 4. Admin views user details
        user_detail_url = reverse('admin_app:user_detail', kwargs={'user_id': new_user.id})
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_obj'], new_user)
        
        # 5. Admin edits user
        user_edit_url = reverse('admin_app:user_edit', kwargs={'user_id': new_user.id})
        response = self.client.post(user_edit_url, {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True,
            'is_customer': True,
            'is_service_provider': True
        })
        self.assertRedirects(response, user_detail_url)
        
        # 6. Verify user was updated
        new_user.refresh_from_db()
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        self.assertTrue(new_user.is_service_provider)
        
        # 7. Admin deletes user
        user_delete_url = reverse('admin_app:user_delete', kwargs={'user_id': new_user.id})
        response = self.client.post(user_delete_url)
        self.assertRedirects(response, user_list_url)
        
        # 8. Verify user was deleted (or deactivated)
        self.assertFalse(User.objects.filter(id=new_user.id, is_active=True).exists())
    
    def test_security_event_workflow(self):
        """Test the complete security event workflow"""
        # 1. Create a security event
        security_event = SecurityEvent.objects.create(
            user=self.customer,
            event_type='failed_login',
            severity='warning',
            description='Failed login attempt',
            ip_address='127.0.0.1'
        )
        
        # 2. Admin views security events
        security_event_list_url = reverse('admin_app:security_event_list')
        response = self.client.get(security_event_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['security_events']), 1)
        
        # 3. Admin views security event details
        security_event_detail_url = reverse('admin_app:security_event_detail', kwargs={'event_id': security_event.id})
        response = self.client.get(security_event_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['security_event'], security_event)
        
        # 4. Admin resolves security event
        security_event_resolve_url = reverse('admin_app:security_event_resolve', kwargs={'event_id': security_event.id})
        response = self.client.post(security_event_resolve_url, {
            'resolution_notes': 'Issue investigated and resolved'
        })
        self.assertRedirects(response, security_event_detail_url)
        
        # 5. Verify security event was resolved
        security_event.refresh_from_db()
        self.assertTrue(security_event.is_resolved)
        self.assertEqual(security_event.resolved_by, self.admin_user)
        self.assertIsNotNone(security_event.resolved_at)
        self.assertEqual(security_event.resolution_notes, 'Issue investigated and resolved')
        
        # 6. Verify activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='SecurityEvent',
            target_id=str(security_event.id),
            description__contains='resolved'
        ).exists())
    
    def test_task_management_workflow(self):
        """Test the complete task management workflow"""
        # 1. Admin creates a task
        task_create_url = reverse('admin_app:task_create')
        response = self.client.post(task_create_url, {
            'title': 'Test Task',
            'description': 'This is a test task',
            'assigned_to': self.admin_user.id,
            'due_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'priority': 'high',
            'status': 'pending'
        })
        self.assertRedirects(response, reverse('admin_app:task_list'))
        
        # 2. Verify task was created
        self.assertTrue(AdminTask.objects.filter(title='Test Task').exists())
        task = AdminTask.objects.get(title='Test Task')
        
        # 3. Admin views task details
        task_detail_url = reverse('admin_app:task_detail', kwargs={'task_id': task.id})
        response = self.client.get(task_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task'], task)
        
        # 4. Admin updates task status
        task_update_status_url = reverse('admin_app:task_update_status', kwargs={'task_id': task.id})
        response = self.client.post(task_update_status_url, {
            'status': 'in_progress'
        })
        self.assertRedirects(response, task_detail_url)
        
        # 5. Verify task status was updated
        task.refresh_from_db()
        self.assertEqual(task.status, 'in_progress')
        
        # 6. Admin marks task as completed
        task_mark_completed_url = reverse('admin_app:task_mark_completed', kwargs={'task_id': task.id})
        response = self.client.post(task_mark_completed_url)
        self.assertRedirects(response, task_detail_url)
        
        # 7. Verify task was marked as completed
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
        
        # 8. Verify activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='AdminTask',
            target_id=str(task.id),
            description__contains='completed'
        ).exists())
    
    def test_system_config_workflow(self):
        """Test the system configuration workflow"""
        # 1. Admin views system config
        system_config_url = reverse('admin_app:system_config')
        response = self.client.get(system_config_url)
        self.assertEqual(response.status_code, 200)
        
        # 2. Admin updates system config
        response = self.client.post(system_config_url, {
            'maintenance_mode': True,
            'maintenance_message': 'System is under maintenance',
            'registration_enabled': False,
            'max_login_attempts': 3,
            'login_lockout_duration': 60,
            'password_expiry_days': 30,
            'session_timeout_minutes': 15,
            'enable_two_factor_auth': True
        })
        self.assertRedirects(response, system_config_url)
        
        # 3. Verify system config was updated
        config = SystemConfig.get_instance()
        self.assertTrue(config.maintenance_mode)
        self.assertEqual(config.maintenance_message, 'System is under maintenance')
        self.assertFalse(config.registration_enabled)
        self.assertEqual(config.max_login_attempts, 3)
        self.assertEqual(config.login_lockout_duration, 60)
        self.assertEqual(config.password_expiry_days, 30)
        self.assertEqual(config.session_timeout_minutes, 15)
        self.assertTrue(config.enable_two_factor_auth)
        
        # 4. Verify activity was logged
        self.assertTrue(AdminActivity.objects.filter(
            user=self.admin_user,
            action_type='update',
            target_model='SystemConfig'
        ).exists())
