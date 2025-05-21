from django.contrib import admin
from .models import NotificationCategory, Notification, UserNotification, NotificationPreference


@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon', 'color')
    search_fields = ('name', 'description')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'created_at', 'expires_at', 'is_system_wide', 'is_active')
    list_filter = ('category', 'priority', 'is_system_wide', 'is_active')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'is_read', 'read_at', 'is_deleted', 'deleted_at')
    list_filter = ('is_read', 'is_deleted')
    search_fields = ('user__email', 'notification__title')
    date_hierarchy = 'notification__created_at'
    readonly_fields = ('read_at', 'deleted_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'channel', 'is_enabled')
    list_filter = ('category', 'channel', 'is_enabled')
    search_fields = ('user__email', 'category__name')

