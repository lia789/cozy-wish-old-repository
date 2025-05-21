from django.urls import path
from . import views

app_name = 'notifications_app'

urlpatterns = [
    # Customer and Service Provider URLs
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('<int:notification_id>/unread/', views.mark_notification_unread, name='mark_notification_unread'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    path('unread/', views.get_unread_notifications, name='get_unread_notifications'),

    # Admin URLs
    path('admin/dashboard/', views.admin_notification_dashboard, name='admin_notification_dashboard'),
    path('admin/announcement/create/', views.admin_create_announcement, name='admin_create_announcement'),
    path('admin/categories/', views.admin_manage_categories, name='admin_manage_categories'),
    path('admin/categories/create/', views.admin_create_category, name='admin_create_category'),
    path('admin/categories/<int:category_id>/edit/', views.admin_edit_category, name='admin_edit_category'),
    path('admin/categories/<int:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/notifications/', views.admin_notification_list, name='admin_notification_list'),
    path('admin/notifications/<int:notification_id>/', views.admin_notification_detail, name='admin_notification_detail'),
    path('admin/notifications/<int:notification_id>/deactivate/', views.admin_deactivate_notification, name='admin_deactivate_notification'),

    # Test URL
    path('test/', views.test_view, name='test_view'),
]
