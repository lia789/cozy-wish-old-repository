from django.urls import path
from . import views

app_name = 'discount_app'

urlpatterns = [
    # Test URL
    path('test/', views.test_view, name='test_view'),

    # Customer URLs
    path('featured/', views.featured_discounts, name='featured_discounts'),
    path('venue/<int:venue_id>/', views.venue_discounts, name='venue_discounts'),
    path('search/', views.search_discounts, name='search_discounts'),

    # Service Provider URLs
    path('provider/discounts/', views.service_provider_discounts, name='service_provider_discounts'),
    path('provider/venue/create/', views.create_venue_discount, name='create_venue_discount'),
    path('provider/service/create/', views.create_service_discount, name='create_service_discount'),
    path('provider/venue/edit/<int:discount_id>/', views.edit_venue_discount, name='edit_venue_discount'),
    path('provider/service/edit/<int:discount_id>/', views.edit_service_discount, name='edit_service_discount'),
    path('provider/delete/<str:discount_type>/<int:discount_id>/', views.delete_discount, name='delete_discount'),
    path('provider/detail/<str:discount_type>/<int:discount_id>/', views.discount_detail, name='discount_detail'),

    # Admin URLs
    path('admin/dashboard/', views.admin_discount_dashboard, name='admin_discount_dashboard'),
    path('admin/list/<str:discount_type>/', views.admin_discount_list, name='admin_discount_list'),
    path('admin/detail/<str:discount_type>/<int:discount_id>/', views.admin_discount_detail, name='admin_discount_detail'),
    path('admin/approve/<str:discount_type>/<int:discount_id>/', views.admin_approve_discount, name='admin_approve_discount'),
    path('admin/platform/create/', views.admin_create_platform_discount, name='admin_create_platform_discount'),
    path('admin/platform/edit/<int:discount_id>/', views.admin_edit_platform_discount, name='admin_edit_platform_discount'),
]
