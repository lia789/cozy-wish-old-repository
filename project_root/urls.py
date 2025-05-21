"""
URL configuration for project_root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
# Import error handlers
from admin_app.views import admin_404_handler, admin_500_handler, admin_403_handler
# Import sitemaps
from cms_app.sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    # App URLs
    path('', include('venues_app.urls')),  # Venues app is now the main app
    path('accounts/', include('accounts_app.urls')),  # Accounts app moved to /accounts/ prefix
    path('booking/', include('booking_cart_app.urls')),  # Booking cart app
    path('payments/', include('payments_app.urls')),  # Payments app
    path('dashboard/', include('dashboard_app.urls')),  # Dashboard app
    path('cms/', include('cms_app.urls')),  # CMS app
    path('reviews/', include('review_app.urls')),  # Review app
    path('super-admin/', include('admin_app.urls')),  # Admin app
    path('discounts/', include('discount_app.urls')),  # Discount app
    path('notifications/', include('notifications_app.urls')),  # Notifications app
    path('utils/', include('utils.urls')),  # Utils app for image handling

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Add debug toolbar URLs in debug mode
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = admin_404_handler
handler500 = admin_500_handler
handler403 = admin_403_handler
