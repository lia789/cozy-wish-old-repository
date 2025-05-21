from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/bulk-actions/', views.user_bulk_actions, name='user_bulk_actions'),

    # Venue Management
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('venues/<int:venue_id>/approval/', views.venue_approval, name='venue_approval'),
    path('venues/pending/', views.pending_venues, name='pending_venues'),

    # System Configuration
    path('system/config/', views.system_config, name='system_config'),

    # Audit Logs
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),
    path('audit-logs/<int:log_id>/', views.audit_log_detail, name='audit_log_detail'),
    path('audit-logs/export/', views.export_audit_logs, name='export_audit_logs'),

    # Security Monitoring
    path('security/events/', views.security_event_list, name='security_event_list'),
    path('security/events/<int:event_id>/', views.security_event_detail, name='security_event_detail'),
    path('security/events/<int:event_id>/resolve/', views.security_event_resolve, name='security_event_resolve'),

    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/update-status/', views.task_update_status, name='task_update_status'),
    path('tasks/<int:task_id>/mark-completed/', views.task_mark_completed, name='task_mark_completed'),
    path('tasks/<int:task_id>/mark-cancelled/', views.task_mark_cancelled, name='task_mark_cancelled'),

    # Admin Preferences
    path('preferences/', views.admin_preferences, name='admin_preferences'),

    # Analytics and Reporting
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
    path('analytics/users/', views.user_report, name='user_report'),
    path('analytics/bookings/', views.booking_report, name='booking_report'),
    path('analytics/revenue/', views.revenue_report, name='revenue_report'),
]
