from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json


class AdminPreference(models.Model):
    """Model for storing admin-specific preferences"""
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='admin_preferences',
        limit_choices_to={'is_staff': True}
    )
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    sidebar_collapsed = models.BooleanField(default=False)
    show_quick_actions = models.BooleanField(default=True)
    items_per_page = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Admin Preferences"


class AdminActivity(models.Model):
    """Model for tracking admin actions"""
    
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='admin_activities',
        limit_choices_to={'is_staff': True}
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Admin Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.action_type} - {self.timestamp}"


class AdminTask(models.Model):
    """Model for managing admin tasks"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_tasks',
        limit_choices_to={'is_staff': True}
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tasks',
        limit_choices_to={'is_staff': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)


class SystemConfig(models.Model):
    """Model for system-wide configuration"""
    
    # There should only be one instance of this model
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    registration_enabled = models.BooleanField(default=True)
    max_login_attempts = models.PositiveIntegerField(default=5)
    login_lockout_duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    password_expiry_days = models.PositiveIntegerField(default=90)
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    enable_two_factor_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='system_config_updates',
        limit_choices_to={'is_staff': True}
    )
    
    class Meta:
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configuration'
    
    def __str__(self):
        return "System Configuration"
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class AuditLog(models.Model):
    """Model for detailed audit logging"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    changes = models.JSONField(default=dict, blank=True)
    
    # For generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_pk = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_pk')
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email if self.user else 'System'} - {self.action} - {self.model_name} - {self.timestamp}"
    
    def set_changes(self, old_data, new_data):
        """Set the changes field by comparing old and new data"""
        changes = {}
        for key in set(old_data.keys()) | set(new_data.keys()):
            if key in old_data and key in new_data:
                if old_data[key] != new_data[key]:
                    changes[key] = {
                        'old': old_data[key],
                        'new': new_data[key]
                    }
            elif key in old_data:
                changes[key] = {
                    'old': old_data[key],
                    'new': None
                }
            else:
                changes[key] = {
                    'old': None,
                    'new': new_data[key]
                }
        self.changes = changes
        return changes


class SecurityEvent(models.Model):
    """Model for tracking security-related events"""
    
    EVENT_TYPES = [
        ('failed_login', 'Failed Login'),
        ('successful_login', 'Successful Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('account_lockout', 'Account Lockout'),
        ('permission_change', 'Permission Change'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='security_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='info')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_security_events',
        limit_choices_to={'is_staff': True}
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.user.email if self.user else 'Unknown'} - {self.timestamp}"
    
    def resolve(self, admin_user, notes=''):
        """Mark the security event as resolved"""
        self.is_resolved = True
        self.resolved_by = admin_user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
        return True
