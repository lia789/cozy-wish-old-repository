from django.utils import timezone
from django.core.cache import cache
from .models import Announcement, SiteConfiguration


def get_current_announcements():
    """Get active announcements for the current time"""
    announcements = cache.get('active_announcements')
    if announcements is None:
        now = timezone.now()
        announcements = Announcement.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            end_date__isnull=True
        ) | Announcement.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')
        cache.set('active_announcements', announcements, 3600)  # Cache for 1 hour
    return announcements


def cms_context(request):
    """Add CMS-related context to all templates"""
    # Get site configuration
    config = cache.get('site_configuration')
    if config is None:
        config = SiteConfiguration.get_instance()
        cache.set('site_configuration', config, 86400)  # Cache for 24 hours
    
    # Get active announcements
    announcements = get_current_announcements()
    
    return {
        'site_config': config,
        'announcements': announcements,
    }
