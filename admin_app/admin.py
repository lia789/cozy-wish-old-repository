from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    AdminPreference, AdminActivity, AdminTask, 
    SystemConfig, AuditLog, SecurityEvent
)


@admin.register(AdminPreference)
class AdminPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'sidebar_collapsed', 'show_quick_actions', 'items_per_page', 'updated_at')
    list_filter = ('theme', 'sidebar_collapsed', 'show_quick_actions')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Display Preferences', {
            'fields': ('theme', 'sidebar_collapsed', 'show_quick_actions', 'items_per_page')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AdminActivity)
class AdminActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'target_model', 'target_id', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__email', 'target_model', 'target_id', 'description')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Activity Details', {
            'fields': ('action_type', 'target_model', 'target_id', 'description')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(AdminTask)
class AdminTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'assigned_to', 'priority', 'status', 'due_date', 'is_overdue')
    list_filter = ('priority', 'status', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'created_by__email', 'assigned_to__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def is_overdue(self, obj):
        if obj.due_date and obj.status not in ['completed', 'cancelled'] and obj.due_date < timezone.now():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_overdue.short_description = 'Overdue'


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'maintenance_mode', 'registration_enabled', 'max_login_attempts', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('System Status', {
            'fields': ('maintenance_mode', 'maintenance_message', 'registration_enabled')
        }),
        ('Security Settings', {
            'fields': ('max_login_attempts', 'login_lockout_duration', 'password_expiry_days', 'session_timeout_minutes', 'enable_two_factor_auth')
        }),
        ('Audit Information', {
            'fields': ('last_updated_by', 'created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Check if an instance already exists
        return not SystemConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__email', 'model_name', 'object_id', 'ip_address')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address', 'user_agent', 'changes', 'content_type', 'object_pk')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Action Details', {
            'fields': ('action', 'model_name', 'object_id', 'content_type', 'object_pk')
        }),
        ('Changes', {
            'fields': ('changes',)
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of audit logs
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'severity', 'timestamp', 'ip_address', 'is_resolved')
    list_filter = ('event_type', 'severity', 'timestamp', 'is_resolved')
    search_fields = ('user__email', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'resolved_at')
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'severity', 'description')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        for event in queryset.filter(is_resolved=False):
            event.resolve(request.user, notes='Resolved in bulk by admin')
        self.message_user(request, f"{queryset.filter(is_resolved=False).count()} events marked as resolved.")
    mark_as_resolved.short_description = "Mark selected events as resolved"
