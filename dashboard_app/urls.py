from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    # Customer dashboard URLs
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/bookings/', views.customer_booking_history, name='customer_booking_history'),
    path('customer/active-bookings/', views.customer_active_bookings, name='customer_active_bookings'),
    path('customer/favorite-venues/', views.customer_favorite_venues, name='customer_favorite_venues'),
    path('customer/profile/', views.customer_profile_management, name='customer_profile_management'),
    path('customer/reviews/', views.customer_review_history, name='customer_review_history'),

    # Service provider dashboard URLs
    path('provider/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/todays-bookings/', views.provider_todays_bookings, name='provider_todays_bookings'),
    path('provider/revenue/', views.provider_revenue_reports, name='provider_revenue_reports'),
    path('provider/service-performance/', views.provider_service_performance, name='provider_service_performance'),
    path('provider/discount-performance/', views.provider_discount_performance, name='provider_discount_performance'),
    path('provider/team/', views.provider_team_management, name='provider_team_management'),

    # Admin dashboard URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/platform-overview/', views.admin_platform_overview, name='admin_platform_overview'),
    path('admin/user-statistics/', views.admin_user_statistics, name='admin_user_statistics'),
    path('admin/booking-analytics/', views.admin_booking_analytics, name='admin_booking_analytics'),
    path('admin/revenue-tracking/', views.admin_revenue_tracking, name='admin_revenue_tracking'),
    path('admin/system-health/', views.admin_system_health, name='admin_system_health'),


]
