from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta

from admin_app.forms import (
    AdminUserCreationForm, AdminUserChangeForm, VenueApprovalForm,
    AdminTaskForm, SystemConfigForm, BulkUserActionForm,
    SecurityEventResolveForm, DateRangeForm
)
from admin_app.models import AdminTask, SystemConfig, SecurityEvent
from venues_app.models import Venue

User = get_user_model()

class AdminUserCreationFormTest(TestCase):
    """Test the AdminUserCreationForm"""
    
    def setUp(self):
        """Set up test data"""
        self.group = Group.objects.create(name='Test Group')
        self.form_data = {
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'is_staff': True,
            'is_superuser': False,
            'is_customer': True,
            'is_service_provider': False,
            'groups': [self.group.id]
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = AdminUserCreationForm()
        expected_fields = [
            'email', 'password1', 'password2', 'is_staff', 'is_superuser',
            'is_customer', 'is_service_provider', 'groups'
        ]
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = AdminUserCreationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_email_required(self):
        """Test that email is required"""
        data = self.form_data.copy()
        data.pop('email')
        form = AdminUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_password_match(self):
        """Test that passwords must match"""
        data = self.form_data.copy()
        data['password2'] = 'differentpassword'
        form = AdminUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_save_method(self):
        """Test that the save method creates a user with correct attributes"""
        form = AdminUserCreationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_customer)
        self.assertFalse(user.is_service_provider)
        self.assertIn(self.group, user.groups.all())


class AdminUserChangeFormTest(TestCase):
    """Test the AdminUserChangeForm"""
    
    def setUp(self):
        """Set up test data"""
        self.group = Group.objects.create(name='Test Group')
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.form_data = {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_active': True,
            'is_staff': True,
            'is_superuser': False,
            'is_customer': True,
            'is_service_provider': False,
            'groups': [self.group.id]
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = AdminUserChangeForm(instance=self.user)
        expected_fields = [
            'email', 'first_name', 'last_name', 'is_active', 'is_staff',
            'is_superuser', 'is_customer', 'is_service_provider', 'groups'
        ]
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = AdminUserChangeForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_email_required(self):
        """Test that email is required"""
        data = self.form_data.copy()
        data.pop('email')
        form = AdminUserChangeForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_save_method(self):
        """Test that the save method updates the user with correct attributes"""
        form = AdminUserChangeForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.email, 'user@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_customer)
        self.assertFalse(user.is_service_provider)
        self.assertIn(self.group, user.groups.all())


class VenueApprovalFormTest(TestCase):
    """Test the VenueApprovalForm"""
    
    def setUp(self):
        """Set up test data"""
        self.approve_data = {
            'action': 'approve'
        }
        self.reject_data = {
            'action': 'reject',
            'rejection_reason': 'Venue does not meet our standards'
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = VenueApprovalForm()
        expected_fields = ['action', 'rejection_reason']
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_approve_valid(self):
        """Test that the form validates with approve action"""
        form = VenueApprovalForm(data=self.approve_data)
        self.assertTrue(form.is_valid())
    
    def test_reject_valid(self):
        """Test that the form validates with reject action and reason"""
        form = VenueApprovalForm(data=self.reject_data)
        self.assertTrue(form.is_valid())
    
    def test_reject_requires_reason(self):
        """Test that rejection requires a reason"""
        data = self.reject_data.copy()
        data.pop('rejection_reason')
        form = VenueApprovalForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('rejection_reason', form.errors)


class AdminTaskFormTest(TestCase):
    """Test the AdminTaskForm"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.assigned_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.form_data = {
            'title': 'Test Task',
            'description': 'This is a test task',
            'assigned_to': self.assigned_user.id,
            'due_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'priority': 'high',
            'status': 'pending'
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = AdminTaskForm()
        expected_fields = [
            'title', 'description', 'assigned_to', 'due_date', 'priority', 'status'
        ]
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = AdminTaskForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_title_required(self):
        """Test that title is required"""
        data = self.form_data.copy()
        data.pop('title')
        form = AdminTaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_assigned_to_optional(self):
        """Test that assigned_to is optional"""
        data = self.form_data.copy()
        data.pop('assigned_to')
        form = AdminTaskForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_due_date_optional(self):
        """Test that due_date is optional"""
        data = self.form_data.copy()
        data.pop('due_date')
        form = AdminTaskForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_save_method(self):
        """Test that the save method creates a task with correct attributes"""
        form = AdminTaskForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        
        task = form.save(commit=False)
        task.created_by = self.admin_user
        task.save()
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.assigned_to, self.assigned_user)
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'pending')


class SystemConfigFormTest(TestCase):
    """Test the SystemConfigForm"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.config = SystemConfig.objects.create(
            last_updated_by=self.admin_user
        )
        self.form_data = {
            'maintenance_mode': True,
            'maintenance_message': 'System is under maintenance',
            'registration_enabled': False,
            'max_login_attempts': 3,
            'login_lockout_duration': 60,
            'password_expiry_days': 30,
            'session_timeout_minutes': 15,
            'enable_two_factor_auth': True
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = SystemConfigForm(instance=self.config)
        expected_fields = [
            'maintenance_mode', 'maintenance_message', 'registration_enabled',
            'max_login_attempts', 'login_lockout_duration', 'password_expiry_days',
            'session_timeout_minutes', 'enable_two_factor_auth'
        ]
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = SystemConfigForm(data=self.form_data, instance=self.config)
        self.assertTrue(form.is_valid())
    
    def test_max_login_attempts_required(self):
        """Test that max_login_attempts is required"""
        data = self.form_data.copy()
        data.pop('max_login_attempts')
        form = SystemConfigForm(data=data, instance=self.config)
        self.assertFalse(form.is_valid())
        self.assertIn('max_login_attempts', form.errors)
    
    def test_login_lockout_duration_required(self):
        """Test that login_lockout_duration is required"""
        data = self.form_data.copy()
        data.pop('login_lockout_duration')
        form = SystemConfigForm(data=data, instance=self.config)
        self.assertFalse(form.is_valid())
        self.assertIn('login_lockout_duration', form.errors)
    
    def test_save_method(self):
        """Test that the save method updates the config with correct attributes"""
        form = SystemConfigForm(data=self.form_data, instance=self.config)
        self.assertTrue(form.is_valid())
        
        config = form.save()
        self.assertTrue(config.maintenance_mode)
        self.assertEqual(config.maintenance_message, 'System is under maintenance')
        self.assertFalse(config.registration_enabled)
        self.assertEqual(config.max_login_attempts, 3)
        self.assertEqual(config.login_lockout_duration, 60)
        self.assertEqual(config.password_expiry_days, 30)
        self.assertEqual(config.session_timeout_minutes, 15)
        self.assertTrue(config.enable_two_factor_auth)


class BulkUserActionFormTest(TestCase):
    """Test the BulkUserActionForm"""
    
    def setUp(self):
        """Set up test data"""
        self.group = Group.objects.create(name='Test Group')
        self.activate_data = {
            'action': 'activate'
        }
        self.add_to_group_data = {
            'action': 'add_to_group',
            'group': self.group.id
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = BulkUserActionForm()
        expected_fields = ['action', 'group']
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_activate_valid(self):
        """Test that the form validates with activate action"""
        form = BulkUserActionForm(data=self.activate_data)
        self.assertTrue(form.is_valid())
    
    def test_add_to_group_valid(self):
        """Test that the form validates with add_to_group action and group"""
        form = BulkUserActionForm(data=self.add_to_group_data)
        self.assertTrue(form.is_valid())
    
    def test_add_to_group_requires_group(self):
        """Test that add_to_group requires a group"""
        data = self.add_to_group_data.copy()
        data.pop('group')
        form = BulkUserActionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('group', form.errors)
    
    def test_remove_from_group_requires_group(self):
        """Test that remove_from_group requires a group"""
        data = {
            'action': 'remove_from_group'
        }
        form = BulkUserActionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('group', form.errors)


class SecurityEventResolveFormTest(TestCase):
    """Test the SecurityEventResolveForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.security_event = SecurityEvent.objects.create(
            user=self.user,
            event_type='failed_login',
            severity='warning',
            description='Failed login attempt'
        )
        self.form_data = {
            'resolution_notes': 'Issue resolved'
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = SecurityEventResolveForm(instance=self.security_event)
        expected_fields = ['resolution_notes']
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = SecurityEventResolveForm(data=self.form_data, instance=self.security_event)
        self.assertTrue(form.is_valid())
    
    def test_resolution_notes_required(self):
        """Test that resolution_notes is required"""
        data = self.form_data.copy()
        data.pop('resolution_notes')
        form = SecurityEventResolveForm(data=data, instance=self.security_event)
        self.assertFalse(form.is_valid())
        self.assertIn('resolution_notes', form.errors)
    
    def test_save_method(self):
        """Test that the save method updates the security event with correct attributes"""
        form = SecurityEventResolveForm(data=self.form_data, instance=self.security_event)
        self.assertTrue(form.is_valid())
        
        event = form.save(commit=False)
        event.is_resolved = True
        event.resolved_by = self.user
        event.resolved_at = timezone.now()
        event.save()
        
        self.assertEqual(event.resolution_notes, 'Issue resolved')
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.resolved_by, self.user)
        self.assertIsNotNone(event.resolved_at)


class DateRangeFormTest(TestCase):
    """Test the DateRangeForm"""
    
    def setUp(self):
        """Set up test data"""
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)
        
        self.form_data = {
            'start_date': self.yesterday.strftime('%Y-%m-%d'),
            'end_date': self.today.strftime('%Y-%m-%d')
        }
    
    def test_form_fields(self):
        """Test that the form has the correct fields"""
        form = DateRangeForm()
        expected_fields = ['start_date', 'end_date']
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_valid_form(self):
        """Test that the form validates with correct data"""
        form = DateRangeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_start_date_required(self):
        """Test that start_date is required"""
        data = self.form_data.copy()
        data.pop('start_date')
        form = DateRangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
    
    def test_end_date_required(self):
        """Test that end_date is required"""
        data = self.form_data.copy()
        data.pop('end_date')
        form = DateRangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)
    
    def test_end_date_after_start_date(self):
        """Test that end_date must be after start_date"""
        data = self.form_data.copy()
        data['start_date'] = self.tomorrow.strftime('%Y-%m-%d')
        data['end_date'] = self.yesterday.strftime('%Y-%m-%d')
        form = DateRangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)
