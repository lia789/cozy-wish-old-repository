from django.urls import path
from . import views

app_name = 'cms_app'

urlpatterns = [
    # Public URLs
    path('page/<slug:slug>/', views.page_view, name='page_detail'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('blog/category/<slug:slug>/', views.blog_category_view, name='blog_category'),
    path('search/', views.search_view, name='search'),
    
    # Service Provider URLs
    path('provider/blog/', views.provider_blog_list_view, name='provider_blog_list'),
    path('provider/blog/create/', views.provider_blog_create_view, name='provider_blog_create'),
    path('provider/blog/<slug:slug>/edit/', views.provider_blog_update_view, name='provider_blog_update'),
    path('provider/blog/<slug:slug>/delete/', views.provider_blog_delete_view, name='provider_blog_delete'),
    path('provider/media/', views.provider_media_list_view, name='provider_media_list'),
    path('provider/media/upload/', views.provider_media_upload_view, name='provider_media_upload'),
    path('provider/media/<int:pk>/delete/', views.provider_media_delete_view, name='provider_media_delete'),
    
    # Admin URLs
    path('admin/pages/', views.admin_page_list_view, name='admin_page_list'),
    path('admin/pages/create/', views.admin_page_create_view, name='admin_page_create'),
    path('admin/pages/<slug:slug>/edit/', views.admin_page_update_view, name='admin_page_update'),
    path('admin/pages/<slug:slug>/delete/', views.admin_page_delete_view, name='admin_page_delete'),
    
    path('admin/blog/', views.admin_blog_list_view, name='admin_blog_list'),
    path('admin/blog/<slug:slug>/edit/', views.admin_blog_update_view, name='admin_blog_update'),
    path('admin/blog/<slug:slug>/approve/', views.admin_blog_approve_view, name='admin_blog_approve'),
    path('admin/blog/<slug:slug>/delete/', views.admin_blog_delete_view, name='admin_blog_delete'),
    
    path('admin/blog/categories/', views.admin_blog_category_list_view, name='admin_blog_category_list'),
    path('admin/blog/categories/create/', views.admin_blog_category_create_view, name='admin_blog_category_create'),
    path('admin/blog/categories/<slug:slug>/edit/', views.admin_blog_category_update_view, name='admin_blog_category_update'),
    path('admin/blog/categories/<slug:slug>/delete/', views.admin_blog_category_delete_view, name='admin_blog_category_delete'),
    
    path('admin/media/', views.admin_media_list_view, name='admin_media_list'),
    path('admin/media/upload/', views.admin_media_upload_view, name='admin_media_upload'),
    path('admin/media/<int:pk>/delete/', views.admin_media_delete_view, name='admin_media_delete'),
    
    path('admin/configuration/', views.admin_site_configuration_view, name='admin_site_configuration'),
    
    path('admin/announcements/', views.admin_announcement_list_view, name='admin_announcement_list'),
    path('admin/announcements/create/', views.admin_announcement_create_view, name='admin_announcement_create'),
    path('admin/announcements/<int:pk>/edit/', views.admin_announcement_update_view, name='admin_announcement_update'),
    path('admin/announcements/<int:pk>/delete/', views.admin_announcement_delete_view, name='admin_announcement_delete'),
]
