from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Page, BlogPost, BlogCategory


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Page.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogCategory.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['cms_app:blog_list', 'cms_app:search']

    def location(self, item):
        return reverse(item)


# Combine all sitemaps
sitemaps = {
    'pages': PageSitemap,
    'blog_posts': BlogPostSitemap,
    'blog_categories': BlogCategorySitemap,
    'static_views': StaticViewSitemap,
}
