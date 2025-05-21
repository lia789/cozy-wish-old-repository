from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Page, BlogCategory, BlogPost, MediaItem, SiteConfiguration, Announcement

User = get_user_model()


class PageModelTest(TestCase):
    """Test the Page model"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpassword'
        )
        
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='<p>This is a test page.</p>',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
    
    def test_page_creation(self):
        """Test page is created correctly"""
        self.assertEqual(self.page.title, 'Test Page')
        self.assertEqual(self.page.slug, 'test-page')
        self.assertEqual(self.page.status, 'published')
        self.assertEqual(self.page.created_by, self.admin_user)
    
    def test_page_str(self):
        """Test the string representation of page"""
        self.assertEqual(str(self.page), 'Test Page')
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.page.get_absolute_url(), reverse('cms_app:page_detail', kwargs={'slug': 'test-page'}))


class BlogCategoryModelTest(TestCase):
    """Test the BlogCategory model"""
    
    def setUp(self):
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )
    
    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(self.category.description, 'This is a test category.')
    
    def test_category_str(self):
        """Test the string representation of category"""
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.category.get_absolute_url(), reverse('cms_app:blog_category', kwargs={'slug': 'test-category'}))


class BlogPostModelTest(TestCase):
    """Test the BlogPost model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpassword'
        )
        
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='<p>This is a test post.</p>',
            excerpt='Test excerpt',
            status='published',
            author=self.user
        )
        self.post.categories.add(self.category)
    
    def test_post_creation(self):
        """Test post is created correctly"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.status, 'published')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.categories.first(), self.category)
    
    def test_post_str(self):
        """Test the string representation of post"""
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        self.assertEqual(self.post.get_absolute_url(), reverse('cms_app:blog_detail', kwargs={'slug': 'test-post'}))


class SiteConfigurationModelTest(TestCase):
    """Test the SiteConfiguration model"""
    
    def setUp(self):
        self.config = SiteConfiguration.objects.create(
            site_name='Test Site',
            site_description='Test description',
            contact_email='test@example.com'
        )
    
    def test_config_creation(self):
        """Test configuration is created correctly"""
        self.assertEqual(self.config.site_name, 'Test Site')
        self.assertEqual(self.config.site_description, 'Test description')
        self.assertEqual(self.config.contact_email, 'test@example.com')
    
    def test_config_str(self):
        """Test the string representation of configuration"""
        self.assertEqual(str(self.config), 'Test Site')
    
    def test_get_instance(self):
        """Test get_instance method returns the singleton instance"""
        instance = SiteConfiguration.get_instance()
        self.assertEqual(instance, self.config)
        
        # Create another instance (should replace the first one)
        new_config = SiteConfiguration.objects.create(
            site_name='New Site',
            contact_email='new@example.com'
        )
        
        # get_instance should return the new instance
        instance = SiteConfiguration.get_instance()
        self.assertEqual(instance, new_config)
        
        # The old instance should be deleted
        self.assertEqual(SiteConfiguration.objects.count(), 1)


class AnnouncementModelTest(TestCase):
    """Test the Announcement model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpassword'
        )
        
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement.',
            announcement_type='info',
            is_active=True,
            created_by=self.user
        )
    
    def test_announcement_creation(self):
        """Test announcement is created correctly"""
        self.assertEqual(self.announcement.title, 'Test Announcement')
        self.assertEqual(self.announcement.content, 'This is a test announcement.')
        self.assertEqual(self.announcement.announcement_type, 'info')
        self.assertTrue(self.announcement.is_active)
        self.assertEqual(self.announcement.created_by, self.user)
    
    def test_announcement_str(self):
        """Test the string representation of announcement"""
        self.assertEqual(str(self.announcement), 'Test Announcement')
    
    def test_is_current(self):
        """Test is_current property"""
        self.assertTrue(self.announcement.is_current)
        
        # Test inactive announcement
        self.announcement.is_active = False
        self.announcement.save()
        self.assertFalse(self.announcement.is_current)
