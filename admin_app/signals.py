from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import models
import json

from .models import AdminPreference, AdminActivity, AuditLog, SystemConfig, SecurityEvent

User = get_user_model()


@receiver(post_save, sender=User)
def create_admin_preferences(sender, instance, created, **kwargs):
    """Create admin preferences for staff users"""
    if created and instance.is_staff:
        AdminPreference.objects.create(user=instance)


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log changes to user accounts"""
    if not hasattr(instance, '_skip_audit_log') or not instance._skip_audit_log:
        content_type = ContentType.objects.get_for_model(sender)
        if created:
            AuditLog.objects.create(
                user=None,  # System action or will be set by the view
                action='create',
                model_name='User',
                object_id=str(instance.id),
                content_type=content_type,
                object_pk=str(instance.id),
                changes={'email': instance.email}
            )
        else:
            # This is simplified - in a real app, you'd compare old and new values
            AuditLog.objects.create(
                user=None,  # System action or will be set by the view
                action='update',
                model_name='User',
                object_id=str(instance.id),
                content_type=content_type,
                object_pk=str(instance.id),
                changes={'updated': True}
            )


def log_model_changes(sender, instance, created, **kwargs):
    """Generic function to log model changes"""
    if hasattr(instance, '_skip_audit_log') and instance._skip_audit_log:
        return
    
    content_type = ContentType.objects.get_for_model(sender)
    model_name = sender.__name__
    
    if created:
        AuditLog.objects.create(
            user=None,  # Will be set by the view
            action='create',
            model_name=model_name,
            object_id=str(instance.id),
            content_type=content_type,
            object_pk=str(instance.id),
            changes={'created': True}
        )
    else:
        AuditLog.objects.create(
            user=None,  # Will be set by the view
            action='update',
            model_name=model_name,
            object_id=str(instance.id),
            content_type=content_type,
            object_pk=str(instance.id),
            changes={'updated': True}
        )


def log_model_deletion(sender, instance, **kwargs):
    """Generic function to log model deletion"""
    if hasattr(instance, '_skip_audit_log') and instance._skip_audit_log:
        return
    
    content_type = ContentType.objects.get_for_model(sender)
    model_name = sender.__name__
    
    AuditLog.objects.create(
        user=None,  # Will be set by the view
        action='delete',
        model_name=model_name,
        object_id=str(instance.id),
        content_type=content_type,
        object_pk=str(instance.id),
        changes={'deleted': True}
    )


# You can connect these signals to specific models you want to audit
# For example:
# post_save.connect(log_model_changes, sender=YourModel)
# post_delete.connect(log_model_deletion, sender=YourModel)


@receiver(post_save, sender=SystemConfig)
def update_system_config_timestamp(sender, instance, **kwargs):
    """Update the last_updated timestamp for SystemConfig"""
    if not kwargs.get('created', False):
        instance.updated_at = timezone.now()
        instance._skip_audit_log = True  # Prevent infinite loop
        instance.save(update_fields=['updated_at'])
        instance._skip_audit_log = False
