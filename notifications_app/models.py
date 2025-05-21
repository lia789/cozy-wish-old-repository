from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationCategory(models.Model):
    """Categories for organizing notifications"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=20, blank=True, help_text="CSS color class")

    class Meta:
        verbose_name = "Notification Category"
        verbose_name_plural = "Notification Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Notification(models.Model):
    """Base model for all notifications"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # For linking to related objects (e.g., booking, review, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # For system-wide notifications
    is_system_wide = models.BooleanField(default=False)

    # For tracking notification status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_expired(self):
        """Check if the notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserNotification(models.Model):
    """Link between notifications and users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'notification']
        ordering = ['-notification__created_at']

    def __str__(self):
        return f"{self.user.email} - {self.notification.title}"

    def mark_as_read(self):
        """Mark the notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        """Mark the notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])

    def delete_notification(self):
        """Soft delete the notification"""
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    CHANNEL_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('both', 'Both'),
        ('none', 'None'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='preferences')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='both')
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'category']
        ordering = ['category__name']

    def __str__(self):
        return f"{self.user.email} - {self.category.name} - {self.get_channel_display()}"

