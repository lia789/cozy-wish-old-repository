from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from admin_app.models import (
    AdminPreference, AdminActivity, AdminTask,
    SystemConfig, AuditLog, SecurityEvent
)

User = get_user_model()

class AdminPreferenceModelTest(TestCase):
    """Test the AdminPreference model"""
    
    def setUp(self):
        """Set up test data"""
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
    
    def test_preference_creation(self):
        """Test creating an admin preference"""
        self.assertEqual(self.preference.user, self.admin_user)
        self.assertEqual(self.preference.theme, 'dark')
        self.assertTrue(self.preference.sidebar_collapsed)
        self.assertFalse(self.preference.show_quick_actions)
        self.assertEqual(self.preference.items_per_page, 50)
    
    def test_preference_str(self):
        """Test the string representation of admin preference"""
        self.assertEqual(str(self.preference), "admin@example.com's Admin Preferences")
    
    def test_preference_defaults(self):
        """Test the default values for admin preference"""
        user = User.objects.create_superuser(
            email='admin2@example.com',
            password='testpass123'
        )
        preference = AdminPreference.objects.create(user=user)
        
        self.assertEqual(preference.theme, 'light')
        self.assertFalse(preference.sidebar_collapsed)
        self.assertTrue(preference.show_quick_actions)
        self.assertEqual(preference.items_per_page, 20)


class AdminActivityModelTest(TestCase):
    """Test the AdminActivity model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.activity = AdminActivity.objects.create(
            user=self.admin_user,
            action_type='create',
            target_model='User',
            target_id='1',
            description='Created a new user',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
    
    def test_activity_creation(self):
        """Test creating an admin activity"""
        self.assertEqual(self.activity.user, self.admin_user)
        self.assertEqual(self.activity.action_type, 'create')
        self.assertEqual(self.activity.target_model, 'User')
        self.assertEqual(self.activity.target_id, '1')
        self.assertEqual(self.activity.description, 'Created a new user')
        self.assertEqual(self.activity.ip_address, '127.0.0.1')
        self.assertEqual(self.activity.user_agent, 'Test User Agent')
    
    def test_activity_str(self):
        """Test the string representation of admin activity"""
        expected = f"{self.admin_user.email} - create - {self.activity.timestamp}"
        self.assertEqual(str(self.activity), expected)
    
    def test_activity_ordering(self):
        """Test that activities are ordered by timestamp in descending order"""
        # Create a second activity
        activity2 = AdminActivity.objects.create(
            user=self.admin_user,
            action_type='update',
            target_model='User',
            target_id='1',
            description='Updated a user'
        )
        
        # Get all activities
        activities = AdminActivity.objects.all()
        
        # Check that the most recent activity is first
        self.assertEqual(activities[0], activity2)
        self.assertEqual(activities[1], self.activity)


class AdminTaskModelTest(TestCase):
    """Test the AdminTask model"""
    
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
        self.task = AdminTask.objects.create(
            title='Test Task',
            description='This is a test task',
            created_by=self.admin_user,
            assigned_to=self.assigned_user,
            due_date=timezone.now() + timedelta(days=7),
            priority='high',
            status='pending'
        )
    
    def test_task_creation(self):
        """Test creating an admin task"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task')
        self.assertEqual(self.task.created_by, self.admin_user)
        self.assertEqual(self.task.assigned_to, self.assigned_user)
        self.assertEqual(self.task.priority, 'high')
        self.assertEqual(self.task.status, 'pending')
    
    def test_task_str(self):
        """Test the string representation of admin task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_is_overdue(self):
        """Test the is_overdue property"""
        # Task is not overdue
        self.assertFalse(self.task.is_overdue)
        
        # Set due date to yesterday
        self.task.due_date = timezone.now() - timedelta(days=1)
        self.task.save()
        
        # Task should be overdue
        self.assertTrue(self.task.is_overdue)
        
        # Task with no due date is not overdue
        self.task.due_date = None
        self.task.save()
        self.assertFalse(self.task.is_overdue)
    
    def test_task_ordering(self):
        """Test that tasks are ordered by priority and due date"""
        # Create tasks with different priorities and due dates
        task_low = AdminTask.objects.create(
            title='Low Priority Task',
            created_by=self.admin_user,
            priority='low',
            status='pending',
            due_date=timezone.now() + timedelta(days=10)
        )
        
        task_medium = AdminTask.objects.create(
            title='Medium Priority Task',
            created_by=self.admin_user,
            priority='medium',
            status='pending',
            due_date=timezone.now() + timedelta(days=5)
        )
        
        task_urgent = AdminTask.objects.create(
            title='Urgent Task',
            created_by=self.admin_user,
            priority='urgent',
            status='pending',
            due_date=timezone.now() + timedelta(days=3)
        )
        
        # Get all tasks
        tasks = AdminTask.objects.all()
        
        # Check ordering: urgent, high, medium, low
        self.assertEqual(tasks[0], task_urgent)
        self.assertEqual(tasks[1], self.task)  # high priority
        self.assertEqual(tasks[2], task_medium)
        self.assertEqual(tasks[3], task_low)


class SystemConfigModelTest(TestCase):
    """Test the SystemConfig model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.config = SystemConfig.objects.create(
            maintenance_mode=True,
            maintenance_message='System is under maintenance',
            registration_enabled=False,
            max_login_attempts=3,
            login_lockout_duration=60,
            password_expiry_days=30,
            session_timeout_minutes=15,
            enable_two_factor_auth=True,
            last_updated_by=self.admin_user
        )
    
    def test_config_creation(self):
        """Test creating a system configuration"""
        self.assertTrue(self.config.maintenance_mode)
        self.assertEqual(self.config.maintenance_message, 'System is under maintenance')
        self.assertFalse(self.config.registration_enabled)
        self.assertEqual(self.config.max_login_attempts, 3)
        self.assertEqual(self.config.login_lockout_duration, 60)
        self.assertEqual(self.config.password_expiry_days, 30)
        self.assertEqual(self.config.session_timeout_minutes, 15)
        self.assertTrue(self.config.enable_two_factor_auth)
        self.assertEqual(self.config.last_updated_by, self.admin_user)
    
    def test_config_str(self):
        """Test the string representation of system configuration"""
        self.assertEqual(str(self.config), 'System Configuration')
    
    def test_get_instance(self):
        """Test the get_instance method"""
        # Delete all configs
        SystemConfig.objects.all().delete()
        
        # Get instance should create a new config with default values
        config = SystemConfig.get_instance()
        
        self.assertFalse(config.maintenance_mode)
        self.assertEqual(config.maintenance_message, '')
        self.assertTrue(config.registration_enabled)
        self.assertEqual(config.max_login_attempts, 5)
        self.assertEqual(config.login_lockout_duration, 30)
        self.assertEqual(config.password_expiry_days, 90)
        self.assertEqual(config.session_timeout_minutes, 30)
        self.assertFalse(config.enable_two_factor_auth)
        
        # Get instance should return the existing config
        config2 = SystemConfig.get_instance()
        self.assertEqual(config, config2)


class AuditLogModelTest(TestCase):
    """Test the AuditLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.audit_log = AuditLog.objects.create(
            user=self.admin_user,
            action='create',
            resource_type='User',
            resource_id='1',
            details='Created a new user',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
    
    def test_audit_log_creation(self):
        """Test creating an audit log"""
        self.assertEqual(self.audit_log.user, self.admin_user)
        self.assertEqual(self.audit_log.action, 'create')
        self.assertEqual(self.audit_log.resource_type, 'User')
        self.assertEqual(self.audit_log.resource_id, '1')
        self.assertEqual(self.audit_log.details, 'Created a new user')
        self.assertEqual(self.audit_log.ip_address, '127.0.0.1')
        self.assertEqual(self.audit_log.user_agent, 'Test User Agent')
    
    def test_audit_log_str(self):
        """Test the string representation of audit log"""
        expected = f"{self.admin_user.email} - create User #1 - {self.audit_log.timestamp}"
        self.assertEqual(str(self.audit_log), expected)
    
    def test_audit_log_ordering(self):
        """Test that audit logs are ordered by timestamp in descending order"""
        # Create a second audit log
        audit_log2 = AuditLog.objects.create(
            user=self.admin_user,
            action='update',
            resource_type='User',
            resource_id='1',
            details='Updated a user'
        )
        
        # Get all audit logs
        audit_logs = AuditLog.objects.all()
        
        # Check that the most recent audit log is first
        self.assertEqual(audit_logs[0], audit_log2)
        self.assertEqual(audit_logs[1], self.audit_log)


class SecurityEventModelTest(TestCase):
    """Test the SecurityEvent model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.security_event = SecurityEvent.objects.create(
            user=self.user,
            event_type='failed_login',
            severity='warning',
            description='Failed login attempt',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
    
    def test_security_event_creation(self):
        """Test creating a security event"""
        self.assertEqual(self.security_event.user, self.user)
        self.assertEqual(self.security_event.event_type, 'failed_login')
        self.assertEqual(self.security_event.severity, 'warning')
        self.assertEqual(self.security_event.description, 'Failed login attempt')
        self.assertEqual(self.security_event.ip_address, '127.0.0.1')
        self.assertEqual(self.security_event.user_agent, 'Test User Agent')
        self.assertFalse(self.security_event.is_resolved)
        self.assertIsNone(self.security_event.resolved_by)
        self.assertIsNone(self.security_event.resolved_at)
        self.assertEqual(self.security_event.resolution_notes, '')
    
    def test_security_event_str(self):
        """Test the string representation of security event"""
        expected = f"failed_login - {self.security_event.timestamp} - {self.user.email}"
        self.assertEqual(str(self.security_event), expected)
    
    def test_security_event_resolve(self):
        """Test resolving a security event"""
        self.security_event.resolve(
            resolved_by=self.admin_user,
            resolution_notes='Issue resolved'
        )
        
        self.assertTrue(self.security_event.is_resolved)
        self.assertEqual(self.security_event.resolved_by, self.admin_user)
        self.assertIsNotNone(self.security_event.resolved_at)
        self.assertEqual(self.security_event.resolution_notes, 'Issue resolved')
    
    def test_security_event_ordering(self):
        """Test that security events are ordered by timestamp in descending order"""
        # Create a second security event
        security_event2 = SecurityEvent.objects.create(
            user=self.user,
            event_type='suspicious_activity',
            severity='critical',
            description='Suspicious activity detected'
        )
        
        # Get all security events
        security_events = SecurityEvent.objects.all()
        
        # Check that the most recent security event is first
        self.assertEqual(security_events[0], security_event2)
        self.assertEqual(security_events[1], self.security_event)
