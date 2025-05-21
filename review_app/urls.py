from django.urls import path
from . import views

app_name = 'review_app'

urlpatterns = [
    # Customer URLs
    path('submit/<int:venue_id>/', views.submit_review_view, name='submit_review'),
    path('edit/<int:review_id>/', views.edit_review_view, name='edit_review'),
    path('flag/<int:review_id>/', views.flag_review_view, name='flag_review'),
    path('history/', views.customer_review_history_view, name='customer_review_history'),
    
    # Service Provider URLs
    path('provider/reviews/', views.provider_venue_reviews_view, name='provider_venue_reviews'),
    path('provider/respond/<int:review_id>/', views.provider_respond_to_review_view, name='provider_respond_to_review'),
    path('provider/summary/', views.provider_review_summary_view, name='provider_review_summary'),
    
    # Admin URLs
    path('admin/reviews/', views.admin_review_list_view, name='admin_review_list'),
    path('admin/reviews/<int:review_id>/', views.admin_review_detail_view, name='admin_review_detail'),
    path('admin/reviews/<int:review_id>/edit/', views.admin_review_edit_view, name='admin_review_edit'),
    path('admin/reviews/<int:review_id>/delete/', views.admin_review_delete_view, name='admin_review_delete'),
    path('admin/flagged/', views.admin_flagged_reviews_view, name='admin_flagged_reviews'),
    path('admin/flags/<int:flag_id>/approve/', views.admin_approve_flag_view, name='admin_approve_flag'),
    path('admin/flags/<int:flag_id>/reject/', views.admin_reject_flag_view, name='admin_reject_flag'),
    
    # Public URLs
    path('venue/<int:venue_id>/', views.venue_reviews_view, name='venue_reviews'),
]
