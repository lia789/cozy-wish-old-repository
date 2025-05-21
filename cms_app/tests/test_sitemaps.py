from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.sites.models import Site

from cms_app.models import Page, BlogPost, BlogCategory
from cms_app.sitemaps import PageSitemap, BlogPostSitemap, BlogCategorySitemap

User = get_user_model()


class SitemapsTest(TestCase):
    """Test the sitemaps in the cms_app"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create pages
        self.published_page = Page.objects.create(
            title='Published Page',
            slug='published-page',
            content='This is a published page.',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        
        self.draft_page = Page.objects.create(
            title='Draft Page',
            slug='draft-page',
            content='This is a draft page.',
            status='draft',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        
        # Create categories
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )
        
        # Create blog posts
        self.published_post = BlogPost.objects.create(
            title='Published Post',
            slug='published-post',
            content='This is a published post.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now()
        )
        self.published_post.categories.add(self.category)
        
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post.',
            status='draft',
            author=self.provider_user
        )
        
        # Set up site
        self.site = Site.objects.get_current()
        self.site.domain = 'example.com'
        self.site.name = 'Example Site'
        self.site.save()
    
    def test_page_sitemap(self):
        """Test the PageSitemap"""
        sitemap = PageSitemap()
        items = sitemap.items()
        
        # Check that only published pages are included
        self.assertIn(self.published_page, items)
        self.assertNotIn(self.draft_page, items)
        
        # Check location
        self.assertEqual(sitemap.location(self.published_page), self.published_page.get_absolute_url())
        
        # Check lastmod
        self.assertEqual(sitemap.lastmod(self.published_page), self.published_page.updated_at)
        
        # Check changefreq
        self.assertEqual(sitemap.changefreq(self.published_page), 'weekly')
        
        # Check priority
        self.assertEqual(sitemap.priority(self.published_page), 0.8)
    
    def test_blog_post_sitemap(self):
        """Test the BlogPostSitemap"""
        sitemap = BlogPostSitemap()
        items = sitemap.items()
        
        # Check that only published posts are included
        self.assertIn(self.published_post, items)
        self.assertNotIn(self.draft_post, items)
        
        # Check location
        self.assertEqual(sitemap.location(self.published_post), self.published_post.get_absolute_url())
        
        # Check lastmod
        self.assertEqual(sitemap.lastmod(self.published_post), self.published_post.updated_at)
        
        # Check changefreq
        self.assertEqual(sitemap.changefreq(self.published_post), 'weekly')
        
        # Check priority
        self.assertEqual(sitemap.priority(self.published_post), 0.7)
    
    def test_blog_category_sitemap(self):
        """Test the BlogCategorySitemap"""
        sitemap = BlogCategorySitemap()
        items = sitemap.items()
        
        # Check that categories are included
        self.assertIn(self.category, items)
        
        # Check location
        self.assertEqual(sitemap.location(self.category), self.category.get_absolute_url())
        
        # Check lastmod (should be None for categories)
        self.assertIsNone(sitemap.lastmod(self.category))
        
        # Check changefreq
        self.assertEqual(sitemap.changefreq(self.category), 'weekly')
        
        # Check priority
        self.assertEqual(sitemap.priority(self.category), 0.6)
