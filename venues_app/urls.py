from django.urls import path
from . import views

app_name = 'venues_app'

urlpatterns = [
    # Public views
    path('', views.home_view, name='home'),
    path('venues/', views.venue_list_view, name='venue_list'),
    path('venues/search/', views.venue_list_view, name='venue_search'),
    path('venues/<slug:slug>/', views.venue_detail_view, name='venue_detail'),
    path('venues/<slug:venue_slug>/services/<slug:service_slug>/', views.service_detail_view, name='service_detail'),
    path('venues/<slug:venue_slug>/review/', views.submit_review_view, name='submit_review'),

    # Service Provider views
    path('provider/venues/create/', views.create_venue_view, name='create_venue'),
    path('provider/venues/<slug:slug>/', views.provider_venue_detail_view, name='provider_venue_detail'),
    path('provider/venues/<slug:slug>/edit/', views.edit_venue_view, name='edit_venue'),
    path('provider/venues/<slug:slug>/delete/', views.delete_venue_view, name='delete_venue'),
    path('provider/venues/<slug:venue_slug>/services/create/', views.create_service_view, name='create_service'),
    path('provider/venues/<slug:venue_slug>/services/add/', views.create_service_view, name='add_service'),
    path('provider/venues/<slug:venue_slug>/services/<slug:service_slug>/edit/', views.edit_service_view, name='edit_service'),
    path('provider/venues/<slug:venue_slug>/services/<slug:service_slug>/delete/', views.delete_service_view, name='delete_service'),
    path('provider/services/create/', views.service_create_redirect, name='service_create'),
    path('provider/venues/<slug:venue_slug>/opening-hours/<int:hour_id>/delete/', views.delete_opening_hours_view, name='delete_opening_hours'),

    # Team Member views
    path('provider/venues/<slug:venue_slug>/team/add/', views.create_team_member_view, name='create_team_member'),
    path('provider/venues/<slug:venue_slug>/team/<int:team_member_id>/edit/', views.edit_team_member_view, name='edit_team_member'),
    path('provider/venues/<slug:venue_slug>/team/<int:team_member_id>/delete/', views.delete_team_member_view, name='delete_team_member'),

    # Admin views - changed from 'admin/' to 'venue-admin/' to avoid conflict with Django admin
    path('venue-admin/venues/', views.admin_venue_list_view, name='admin_venue_list'),
    path('venue-admin/venues/<slug:slug>/', views.admin_venue_detail_view, name='admin_venue_detail'),
    path('venue-admin/venues/<slug:slug>/approval/', views.admin_venue_approval_view, name='admin_venue_approval'),

    # API views
    path('api/location-suggestions/', views.location_suggestions_api, name='location_suggestions_api'),
    path('api/location-data/', views.get_location_data_api, name='location_data_api'),
]
