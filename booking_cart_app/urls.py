from django.urls import path
from . import views

app_name = 'booking_cart_app'

urlpatterns = [
    # Customer URLs
    path('cart/add/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('booking/confirmation/<uuid:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Service Provider URLs
    path('provider/bookings/', views.provider_booking_list, name='provider_booking_list'),
    path('provider/bookings/<uuid:booking_id>/', views.provider_booking_detail, name='provider_booking_detail'),
    path('provider/bookings/<uuid:booking_id>/status/', views.provider_update_booking_status, name='provider_update_booking_status'),
    path('provider/services/<int:service_id>/availability/', views.provider_service_availability, name='provider_service_availability'),
    path('provider/services/<int:service_id>/bulk-availability/', views.provider_bulk_availability, name='provider_bulk_availability'),
    path('provider/availability/<int:availability_id>/delete/', views.provider_delete_availability, name='provider_delete_availability'),
    
    # Admin URLs
    path('admin/bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('admin/bookings/<uuid:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('admin/bookings/<uuid:booking_id>/status/', views.admin_update_booking_status, name='admin_update_booking_status'),
    path('admin/bookings/analytics/', views.admin_booking_analytics, name='admin_booking_analytics'),
]
