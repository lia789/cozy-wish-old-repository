from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
import os
import tempfile
from datetime import timedelta

from cms_app.models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)

User = get_user_model()


class PageModelTest(TestCase):
    """Test the Page model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='This is a test page content.',
            meta_description='Test page description',
            meta_keywords='test, page, keywords',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
    
    def test_page_creation(self):
        """Test creating a page is successful"""
        self.assertEqual(self.page.title, 'Test Page')
        self.assertEqual(self.page.slug, 'test-page')
        self.assertEqual(self.page.content, 'This is a test page content.')
        self.assertEqual(self.page.meta_description, 'Test page description')
        self.assertEqual(self.page.meta_keywords, 'test, page, keywords')
        self.assertEqual(self.page.status, 'published')
        self.assertEqual(self.page.created_by, self.admin_user)
        self.assertEqual(self.page.updated_by, self.admin_user)
        
        # Test string representation
        self.assertEqual(str(self.page), 'Test Page')
    
    def test_page_slug_generation(self):
        """Test slug is generated automatically if not provided"""
        page = Page.objects.create(
            title='Another Test Page',
            content='This is another test page content.',
            status='draft',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        self.assertEqual(page.slug, 'another-test-page')
    
    def test_page_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.page.get_absolute_url(), '/cms/page/test-page/')
    
    def test_page_ordering(self):
        """Test pages are ordered by title"""
        Page.objects.create(
            title='A Test Page',
            content='This is a test page content.',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        
        pages = Page.objects.all()
        self.assertEqual(pages[0].title, 'A Test Page')
        self.assertEqual(pages[1].title, 'Test Page')


class BlogCategoryModelTest(TestCase):
    """Test the BlogCategory model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )
    
    def test_category_creation(self):
        """Test creating a category is successful"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(self.category.description, 'This is a test category.')
        
        # Test string representation
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_category_slug_generation(self):
        """Test slug is generated automatically if not provided"""
        category = BlogCategory.objects.create(
            name='Another Test Category',
            description='This is another test category.'
        )
        self.assertEqual(category.slug, 'another-test-category')
    
    def test_category_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.category.get_absolute_url(), '/cms/blog/category/test-category/')
    
    def test_category_ordering(self):
        """Test categories are ordered by name"""
        BlogCategory.objects.create(
            name='A Test Category',
            description='This is a test category.'
        )
        
        categories = BlogCategory.objects.all()
        self.assertEqual(categories[0].name, 'A Test Category')
        self.assertEqual(categories[1].name, 'Test Category')


class BlogPostModelTest(TestCase):
    """Test the BlogPost model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )
        
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            content='This is a test blog post content.',
            excerpt='This is a test excerpt.',
            meta_description='Test blog post description',
            meta_keywords='test, blog, post, keywords',
            status='published',
            allow_comments=True,
            author=self.user
        )
        
        # Add category to post
        self.post.categories.add(self.category)
        
        # Set published_at for published post
        self.post.published_at = timezone.now()
        self.post.save()
    
    def test_post_creation(self):
        """Test creating a blog post is successful"""
        self.assertEqual(self.post.title, 'Test Blog Post')
        self.assertEqual(self.post.slug, 'test-blog-post')
        self.assertEqual(self.post.content, 'This is a test blog post content.')
        self.assertEqual(self.post.excerpt, 'This is a test excerpt.')
        self.assertEqual(self.post.meta_description, 'Test blog post description')
        self.assertEqual(self.post.meta_keywords, 'test, blog, post, keywords')
        self.assertEqual(self.post.status, 'published')
        self.assertTrue(self.post.allow_comments)
        self.assertEqual(self.post.author, self.user)
        self.assertIsNotNone(self.post.published_at)
        
        # Test categories
        self.assertEqual(self.post.categories.count(), 1)
        self.assertEqual(self.post.categories.first(), self.category)
        
        # Test string representation
        self.assertEqual(str(self.post), 'Test Blog Post')
    
    def test_post_slug_generation(self):
        """Test slug is generated automatically if not provided"""
        post = BlogPost.objects.create(
            title='Another Test Blog Post',
            content='This is another test blog post content.',
            status='draft',
            author=self.user
        )
        self.assertEqual(post.slug, 'another-test-blog-post')
    
    def test_post_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.post.get_absolute_url(), '/cms/blog/test-blog-post/')
    
    def test_post_ordering(self):
        """Test posts are ordered by created_at in descending order"""
        # Create an older post
        older_post = BlogPost.objects.create(
            title='Older Test Blog Post',
            content='This is an older test blog post content.',
            status='published',
            author=self.user
        )
        older_post.created_at = timezone.now() - timedelta(days=1)
        older_post.save()
        
        posts = BlogPost.objects.all()
        self.assertEqual(posts[0].title, 'Test Blog Post')
        self.assertEqual(posts[1].title, 'Older Test Blog Post')
    
    def test_post_published_at_auto_set(self):
        """Test published_at is automatically set when status changes to published"""
        draft_post = BlogPost.objects.create(
            title='Draft Blog Post',
            content='This is a draft blog post content.',
            status='draft',
            author=self.user
        )
        self.assertIsNone(draft_post.published_at)
        
        # Change status to published
        draft_post.status = 'published'
        draft_post.save()
        
        # Refresh from database
        draft_post.refresh_from_db()
        
        self.assertIsNotNone(draft_post.published_at)


class BlogCommentModelTest(TestCase):
    """Test the BlogComment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        self.commenter = User.objects.create_user(
            email='commenter@example.com',
            password='testpass123',
            is_customer=True
        )
        
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            content='This is a test blog post content.',
            status='published',
            author=self.user
        )
        
        self.comment = BlogComment.objects.create(
            blog_post=self.post,
            author=self.commenter,
            content='This is a test comment.',
            status='approved'
        )
    
    def test_comment_creation(self):
        """Test creating a blog comment is successful"""
        self.assertEqual(self.comment.blog_post, self.post)
        self.assertEqual(self.comment.author, self.commenter)
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.status, 'approved')
        
        # Test string representation
        expected_str = f"Comment by {self.commenter.email} on {self.post.title}"
        self.assertEqual(str(self.comment), expected_str)
    
    def test_comment_ordering(self):
        """Test comments are ordered by created_at in descending order"""
        # Create an older comment
        older_comment = BlogComment.objects.create(
            blog_post=self.post,
            author=self.commenter,
            content='This is an older test comment.',
            status='approved'
        )
        older_comment.created_at = timezone.now() - timedelta(days=1)
        older_comment.save()
        
        comments = BlogComment.objects.all()
        self.assertEqual(comments[0].content, 'This is a test comment.')
        self.assertEqual(comments[1].content, 'This is an older test comment.')


class MediaItemModelTest(TestCase):
    """Test the MediaItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_file.write(b'file content')
        self.temp_file.seek(0)
        
        # Create a media item
        self.media_item = MediaItem.objects.create(
            title='Test Image',
            file=SimpleUploadedFile(
                name='test_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            file_type='image',
            description='This is a test image.',
            alt_text='Test image alt text',
            uploaded_by=self.admin_user
        )
        
        # Reset file pointer
        self.temp_file.seek(0)
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_file.close()
        # Delete the file if it exists
        if self.media_item.file and hasattr(self.media_item.file, 'path') and os.path.exists(self.media_item.file.path):
            os.remove(self.media_item.file.path)
    
    def test_media_item_creation(self):
        """Test creating a media item is successful"""
        self.assertEqual(self.media_item.title, 'Test Image')
        self.assertEqual(self.media_item.file_type, 'image')
        self.assertEqual(self.media_item.description, 'This is a test image.')
        self.assertEqual(self.media_item.alt_text, 'Test image alt text')
        self.assertEqual(self.media_item.uploaded_by, self.admin_user)
        
        # Test string representation
        self.assertEqual(str(self.media_item), 'Test Image')
    
    def test_media_item_file_properties(self):
        """Test media item file properties"""
        self.assertIsNotNone(self.media_item.file_url)
        self.assertGreater(self.media_item.file_size, 0)
        self.assertEqual(self.media_item.file_extension, '.jpg')
    
    def test_media_item_upload_path_admin(self):
        """Test media item upload path for admin user"""
        # The path should contain 'admin' for admin uploads
        self.assertIn('admin', self.media_item.file.name)
    
    def test_media_item_upload_path_provider(self):
        """Test media item upload path for service provider"""
        # Create a media item uploaded by a service provider
        provider_media = MediaItem.objects.create(
            title='Provider Image',
            file=SimpleUploadedFile(
                name='provider_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            file_type='image',
            uploaded_by=self.provider_user
        )
        
        # The path should contain the provider's username
        self.assertIn('provider', provider_media.file.name)
        
        # Clean up
        if provider_media.file and hasattr(provider_media.file, 'path') and os.path.exists(provider_media.file.path):
            os.remove(provider_media.file.path)


class SiteConfigurationModelTest(TestCase):
    """Test the SiteConfiguration model"""
    
    def setUp(self):
        """Set up test data"""
        self.config = SiteConfiguration.objects.create(
            site_name='Test Site',
            site_description='This is a test site.',
            contact_email='info@testsite.com',
            contact_phone='123-456-7890',
            contact_address='123 Test St, Test City, TS 12345',
            facebook_url='https://facebook.com/testsite',
            twitter_url='https://twitter.com/testsite',
            instagram_url='https://instagram.com/testsite',
            linkedin_url='https://linkedin.com/company/testsite',
            google_analytics_id='UA-12345678-1',
            default_meta_description='Test site description for SEO',
            default_meta_keywords='test, site, keywords',
            maintenance_mode=False,
            maintenance_message='Site is under maintenance.'
        )
    
    def test_site_configuration_creation(self):
        """Test creating a site configuration is successful"""
        self.assertEqual(self.config.site_name, 'Test Site')
        self.assertEqual(self.config.site_description, 'This is a test site.')
        self.assertEqual(self.config.contact_email, 'info@testsite.com')
        self.assertEqual(self.config.contact_phone, '123-456-7890')
        self.assertEqual(self.config.contact_address, '123 Test St, Test City, TS 12345')
        self.assertEqual(self.config.facebook_url, 'https://facebook.com/testsite')
        self.assertEqual(self.config.twitter_url, 'https://twitter.com/testsite')
        self.assertEqual(self.config.instagram_url, 'https://instagram.com/testsite')
        self.assertEqual(self.config.linkedin_url, 'https://linkedin.com/company/testsite')
        self.assertEqual(self.config.google_analytics_id, 'UA-12345678-1')
        self.assertEqual(self.config.default_meta_description, 'Test site description for SEO')
        self.assertEqual(self.config.default_meta_keywords, 'test, site, keywords')
        self.assertFalse(self.config.maintenance_mode)
        self.assertEqual(self.config.maintenance_message, 'Site is under maintenance.')
        
        # Test string representation
        self.assertEqual(str(self.config), 'Test Site')
    
    def test_site_configuration_singleton(self):
        """Test that only one site configuration can exist"""
        # Create another configuration
        another_config = SiteConfiguration.objects.create(
            site_name='Another Site',
            contact_email='info@anothersite.com'
        )
        
        # There should still be only one configuration in the database
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        
        # The new configuration should be the only one
        config = SiteConfiguration.objects.first()
        self.assertEqual(config.site_name, 'Another Site')
        self.assertEqual(config.contact_email, 'info@anothersite.com')
    
    def test_get_instance_method(self):
        """Test get_instance class method"""
        # Delete all configurations
        SiteConfiguration.objects.all().delete()
        
        # Get or create an instance
        config = SiteConfiguration.get_instance()
        
        # Check that an instance was created
        self.assertIsNotNone(config)
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        
        # Get the instance again
        config2 = SiteConfiguration.get_instance()
        
        # Check that the same instance is returned
        self.assertEqual(config, config2)


class AnnouncementModelTest(TestCase):
    """Test the Announcement model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement.',
            announcement_type='info',
            is_active=True,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            created_by=self.admin_user
        )
    
    def test_announcement_creation(self):
        """Test creating an announcement is successful"""
        self.assertEqual(self.announcement.title, 'Test Announcement')
        self.assertEqual(self.announcement.content, 'This is a test announcement.')
        self.assertEqual(self.announcement.announcement_type, 'info')
        self.assertTrue(self.announcement.is_active)
        self.assertIsNotNone(self.announcement.start_date)
        self.assertIsNotNone(self.announcement.end_date)
        self.assertEqual(self.announcement.created_by, self.admin_user)
        
        # Test string representation
        self.assertEqual(str(self.announcement), 'Test Announcement')
    
    def test_announcement_is_current(self):
        """Test is_current property"""
        # Current announcement
        self.assertTrue(self.announcement.is_current)
        
        # Inactive announcement
        self.announcement.is_active = False
        self.announcement.save()
        self.assertFalse(self.announcement.is_current)
        
        # Active but not started yet
        self.announcement.is_active = True
        self.announcement.start_date = timezone.now() + timedelta(days=1)
        self.announcement.save()
        self.assertFalse(self.announcement.is_current)
        
        # Active but expired
        self.announcement.start_date = timezone.now() - timedelta(days=14)
        self.announcement.end_date = timezone.now() - timedelta(days=7)
        self.announcement.save()
        self.assertFalse(self.announcement.is_current)
        
        # Active and current
        self.announcement.start_date = timezone.now() - timedelta(days=1)
        self.announcement.end_date = timezone.now() + timedelta(days=1)
        self.announcement.save()
        self.assertTrue(self.announcement.is_current)
    
    def test_announcement_ordering(self):
        """Test announcements are ordered by created_at in descending order"""
        # Create an older announcement
        older_announcement = Announcement.objects.create(
            title='Older Announcement',
            content='This is an older announcement.',
            announcement_type='warning',
            is_active=True,
            created_by=self.admin_user
        )
        older_announcement.created_at = timezone.now() - timedelta(days=1)
        older_announcement.save()
        
        announcements = Announcement.objects.all()
        self.assertEqual(announcements[0].title, 'Test Announcement')
        self.assertEqual(announcements[1].title, 'Older Announcement')
