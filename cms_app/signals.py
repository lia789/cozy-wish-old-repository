from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Page, BlogPost, BlogCategory, Announcement, SiteConfiguration


@receiver(post_save, sender=Page)
def clear_page_cache(sender, instance, **kwargs):
    """Clear cache when a page is saved"""
    cache.delete(f'page_{instance.slug}')
    cache.delete('all_pages')


@receiver(post_delete, sender=Page)
def clear_page_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when a page is deleted"""
    cache.delete(f'page_{instance.slug}')
    cache.delete('all_pages')


@receiver(post_save, sender=BlogPost)
def clear_blog_cache(sender, instance, **kwargs):
    """Clear cache when a blog post is saved"""
    cache.delete(f'blog_post_{instance.slug}')
    cache.delete('blog_posts')
    
    # Clear category caches for related categories
    for category in instance.categories.all():
        cache.delete(f'blog_category_{category.slug}')


@receiver(post_delete, sender=BlogPost)
def clear_blog_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when a blog post is deleted"""
    cache.delete(f'blog_post_{instance.slug}')
    cache.delete('blog_posts')


@receiver(post_save, sender=BlogCategory)
def clear_category_cache(sender, instance, **kwargs):
    """Clear cache when a blog category is saved"""
    cache.delete(f'blog_category_{instance.slug}')
    cache.delete('blog_categories')


@receiver(post_delete, sender=BlogCategory)
def clear_category_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when a blog category is deleted"""
    cache.delete(f'blog_category_{instance.slug}')
    cache.delete('blog_categories')


@receiver(post_save, sender=Announcement)
def clear_announcement_cache(sender, instance, **kwargs):
    """Clear cache when an announcement is saved"""
    cache.delete('active_announcements')


@receiver(post_delete, sender=Announcement)
def clear_announcement_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when an announcement is deleted"""
    cache.delete('active_announcements')


@receiver(post_save, sender=SiteConfiguration)
def clear_site_config_cache(sender, instance, **kwargs):
    """Clear cache when site configuration is saved"""
    cache.delete('site_configuration')
