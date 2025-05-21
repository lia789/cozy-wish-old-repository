from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from datetime import timedelta

from cms_app.models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)
from cms_app.forms import (
    PageForm, BlogCategoryForm, BlogPostForm, BlogCommentForm,
    MediaUploadForm, SiteConfigurationForm, AnnouncementForm, SearchForm
)

User = get_user_model()


class PageFormTest(TestCase):
    """Test the PageForm"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create a page for testing uniqueness
        self.existing_page = Page.objects.create(
            title='Existing Page',
            slug='existing-page',
            content='This is an existing page.',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        
        # Valid form data
        self.form_data = {
            'title': 'Test Page',
            'content': 'This is a test page content.',
            'meta_description': 'Test page description',
            'meta_keywords': 'test, page, keywords',
            'status': 'published'
        }
    
    def test_page_form_valid(self):
        """Test form is valid with valid data"""
        form = PageForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_page_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing title
        form_data = self.form_data.copy()
        form_data.pop('title')
        form = PageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing content
        form_data = self.form_data.copy()
        form_data.pop('content')
        form = PageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
        # Missing status
        form_data = self.form_data.copy()
        form_data.pop('status')
        form = PageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
    
    def test_page_form_meta_fields_optional(self):
        """Test meta fields are optional"""
        form_data = self.form_data.copy()
        form_data.pop('meta_description')
        form_data.pop('meta_keywords')
        form = PageForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_page_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = PageForm()
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['rows'], 15)
        self.assertEqual(form.fields['meta_description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['meta_description'].widget.attrs['rows'], 2)
        self.assertEqual(form.fields['meta_keywords'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['status'].widget.attrs['class'], 'form-select')


class BlogCategoryFormTest(TestCase):
    """Test the BlogCategoryForm"""
    
    def setUp(self):
        """Set up test data"""
        # Create a category for testing uniqueness
        self.existing_category = BlogCategory.objects.create(
            name='Existing Category',
            slug='existing-category',
            description='This is an existing category.'
        )
        
        # Valid form data
        self.form_data = {
            'name': 'Test Category',
            'description': 'This is a test category.'
        }
    
    def test_category_form_valid(self):
        """Test form is valid with valid data"""
        form = BlogCategoryForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_category_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing name
        form_data = self.form_data.copy()
        form_data.pop('name')
        form = BlogCategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_category_form_description_optional(self):
        """Test description field is optional"""
        form_data = self.form_data.copy()
        form_data.pop('description')
        form = BlogCategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_category_form_duplicate_name(self):
        """Test form is invalid when name would create a duplicate slug"""
        form_data = {
            'name': 'Existing Category',  # This will create the same slug
            'description': 'This is a test category.'
        }
        form = BlogCategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_category_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = BlogCategoryForm()
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['rows'], 3)


class BlogPostFormTest(TestCase):
    """Test the BlogPostForm"""
    
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
        
        # Create a category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )
        
        # Create a post for testing uniqueness
        self.existing_post = BlogPost.objects.create(
            title='Existing Post',
            slug='existing-post',
            content='This is an existing post.',
            status='published',
            author=self.admin_user
        )
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_file.write(b'file content')
        self.temp_file.seek(0)
        
        # Valid form data
        self.form_data = {
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content.',
            'excerpt': 'This is a test excerpt.',
            'categories': [self.category.id],
            'meta_description': 'Test blog post description',
            'meta_keywords': 'test, blog, post, keywords',
            'status': 'published',
            'allow_comments': True
        }
        
        self.form_files = {
            'featured_image': SimpleUploadedFile(
                name='test_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            )
        }
        
        # Reset file pointer
        self.temp_file.seek(0)
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_file.close()
    
    def test_blog_post_form_valid(self):
        """Test form is valid with valid data"""
        form = BlogPostForm(
            data=self.form_data,
            files=self.form_files,
            user=self.admin_user
        )
        self.assertTrue(form.is_valid())
    
    def test_blog_post_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing title
        form_data = self.form_data.copy()
        form_data.pop('title')
        form = BlogPostForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing content
        form_data = self.form_data.copy()
        form_data.pop('content')
        form = BlogPostForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
        # Missing status
        form_data = self.form_data.copy()
        form_data.pop('status')
        form = BlogPostForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
    
    def test_blog_post_form_optional_fields(self):
        """Test optional fields"""
        form_data = self.form_data.copy()
        form_data.pop('excerpt')
        form_data.pop('meta_description')
        form_data.pop('meta_keywords')
        form_data.pop('allow_comments')
        form = BlogPostForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())
    
    def test_blog_post_form_duplicate_title(self):
        """Test form is invalid when title would create a duplicate slug"""
        form_data = self.form_data.copy()
        form_data['title'] = 'Existing Post'  # This will create the same slug
        form = BlogPostForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_blog_post_form_status_choices_for_provider(self):
        """Test status choices are limited for service providers"""
        form = BlogPostForm(user=self.provider_user)
        status_choices = [choice[0] for choice in form.fields['status'].choices]
        self.assertEqual(len(status_choices), 2)
        self.assertIn('draft', status_choices)
        self.assertIn('pending', status_choices)
        self.assertNotIn('published', status_choices)
        self.assertNotIn('archived', status_choices)
    
    def test_blog_post_form_status_choices_for_admin(self):
        """Test all status choices are available for admin"""
        form = BlogPostForm(user=self.admin_user)
        status_choices = [choice[0] for choice in form.fields['status'].choices]
        self.assertEqual(len(status_choices), 4)
        self.assertIn('draft', status_choices)
        self.assertIn('pending', status_choices)
        self.assertIn('published', status_choices)
        self.assertIn('archived', status_choices)
    
    def test_blog_post_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = BlogPostForm(user=self.admin_user)
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['rows'], 15)
        self.assertEqual(form.fields['excerpt'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['excerpt'].widget.attrs['rows'], 3)
        self.assertEqual(form.fields['featured_image'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['categories'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['meta_description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['meta_description'].widget.attrs['rows'], 2)
        self.assertEqual(form.fields['meta_keywords'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['status'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['allow_comments'].widget.attrs['class'], 'form-check-input')


class BlogCommentFormTest(TestCase):
    """Test the BlogCommentForm"""
    
    def setUp(self):
        """Set up test data"""
        # Valid form data
        self.form_data = {
            'content': 'This is a test comment.'
        }
    
    def test_blog_comment_form_valid(self):
        """Test form is valid with valid data"""
        form = BlogCommentForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_blog_comment_form_invalid_missing_content(self):
        """Test form is invalid when content is missing"""
        form_data = self.form_data.copy()
        form_data.pop('content')
        form = BlogCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_blog_comment_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = BlogCommentForm()
        self.assertEqual(form.fields['content'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['rows'], 3)


class MediaUploadFormTest(TestCase):
    """Test the MediaUploadForm"""
    
    def setUp(self):
        """Set up test data"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_file.write(b'file content')
        self.temp_file.seek(0)
        
        # Valid form data
        self.form_data = {
            'title': 'Test Image',
            'file_type': 'image',
            'description': 'This is a test image.',
            'alt_text': 'Test image alt text'
        }
        
        self.form_files = {
            'file': SimpleUploadedFile(
                name='test_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            )
        }
        
        # Reset file pointer
        self.temp_file.seek(0)
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_file.close()
    
    def test_media_upload_form_valid(self):
        """Test form is valid with valid data"""
        form = MediaUploadForm(
            data=self.form_data,
            files=self.form_files
        )
        self.assertTrue(form.is_valid())
    
    def test_media_upload_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing title
        form_data = self.form_data.copy()
        form_data.pop('title')
        form = MediaUploadForm(data=form_data, files=self.form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing file
        form = MediaUploadForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
    
    def test_media_upload_form_optional_fields(self):
        """Test optional fields"""
        form_data = self.form_data.copy()
        form_data.pop('description')
        form_data.pop('alt_text')
        form = MediaUploadForm(data=form_data, files=self.form_files)
        self.assertTrue(form.is_valid())
    
    def test_media_upload_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = MediaUploadForm()
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['file'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['file_type'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['rows'], 3)
        self.assertEqual(form.fields['alt_text'].widget.attrs['class'], 'form-control')


class SiteConfigurationFormTest(TestCase):
    """Test the SiteConfigurationForm"""
    
    def setUp(self):
        """Set up test data"""
        # Valid form data
        self.form_data = {
            'site_name': 'Test Site',
            'site_description': 'This is a test site.',
            'contact_email': 'info@testsite.com',
            'contact_phone': '123-456-7890',
            'contact_address': '123 Test St, Test City, TS 12345',
            'facebook_url': 'https://facebook.com/testsite',
            'twitter_url': 'https://twitter.com/testsite',
            'instagram_url': 'https://instagram.com/testsite',
            'linkedin_url': 'https://linkedin.com/company/testsite',
            'google_analytics_id': 'UA-12345678-1',
            'default_meta_description': 'Test site description for SEO',
            'default_meta_keywords': 'test, site, keywords',
            'maintenance_mode': False,
            'maintenance_message': 'Site is under maintenance.'
        }
    
    def test_site_configuration_form_valid(self):
        """Test form is valid with valid data"""
        form = SiteConfigurationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_site_configuration_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing site_name
        form_data = self.form_data.copy()
        form_data.pop('site_name')
        form = SiteConfigurationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('site_name', form.errors)
        
        # Missing contact_email
        form_data = self.form_data.copy()
        form_data.pop('contact_email')
        form = SiteConfigurationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_email', form.errors)
    
    def test_site_configuration_form_optional_fields(self):
        """Test optional fields"""
        form_data = self.form_data.copy()
        form_data.pop('site_description')
        form_data.pop('contact_phone')
        form_data.pop('contact_address')
        form_data.pop('facebook_url')
        form_data.pop('twitter_url')
        form_data.pop('instagram_url')
        form_data.pop('linkedin_url')
        form_data.pop('google_analytics_id')
        form_data.pop('default_meta_description')
        form_data.pop('default_meta_keywords')
        form_data.pop('maintenance_message')
        form = SiteConfigurationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_site_configuration_form_invalid_email(self):
        """Test form is invalid with invalid email"""
        form_data = self.form_data.copy()
        form_data['contact_email'] = 'invalid-email'
        form = SiteConfigurationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_email', form.errors)
    
    def test_site_configuration_form_invalid_urls(self):
        """Test form is invalid with invalid URLs"""
        form_data = self.form_data.copy()
        form_data['facebook_url'] = 'invalid-url'
        form = SiteConfigurationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('facebook_url', form.errors)


class AnnouncementFormTest(TestCase):
    """Test the AnnouncementForm"""
    
    def setUp(self):
        """Set up test data"""
        # Valid form data
        self.form_data = {
            'title': 'Test Announcement',
            'content': 'This is a test announcement.',
            'announcement_type': 'info',
            'is_active': True,
            'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
        }
    
    def test_announcement_form_valid(self):
        """Test form is valid with valid data"""
        form = AnnouncementForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_announcement_form_invalid_missing_required_fields(self):
        """Test form is invalid when required fields are missing"""
        # Missing title
        form_data = self.form_data.copy()
        form_data.pop('title')
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing content
        form_data = self.form_data.copy()
        form_data.pop('content')
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
        # Missing announcement_type
        form_data = self.form_data.copy()
        form_data.pop('announcement_type')
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('announcement_type', form.errors)
    
    def test_announcement_form_optional_fields(self):
        """Test optional fields"""
        form_data = self.form_data.copy()
        form_data.pop('is_active')
        form_data.pop('end_date')
        form = AnnouncementForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_announcement_form_end_date_before_start_date(self):
        """Test form is invalid when end_date is before start_date"""
        form_data = self.form_data.copy()
        form_data['start_date'] = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
        form_data['end_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Form-level error
    
    def test_announcement_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = AnnouncementForm()
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['content'].widget.attrs['rows'], 3)
        self.assertEqual(form.fields['announcement_type'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['is_active'].widget.attrs['class'], 'form-check-input')
        self.assertEqual(form.fields['start_date'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['start_date'].widget.attrs['type'], 'datetime-local')
        self.assertEqual(form.fields['end_date'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['end_date'].widget.attrs['type'], 'datetime-local')


class SearchFormTest(TestCase):
    """Test the SearchForm"""
    
    def setUp(self):
        """Set up test data"""
        # Valid form data
        self.form_data = {
            'query': 'test search query'
        }
    
    def test_search_form_valid(self):
        """Test form is valid with valid data"""
        form = SearchForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_search_form_invalid_missing_query(self):
        """Test form is invalid when query is missing"""
        form_data = self.form_data.copy()
        form_data.pop('query')
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('query', form.errors)
    
    def test_search_form_invalid_empty_query(self):
        """Test form is invalid when query is empty"""
        form_data = self.form_data.copy()
        form_data['query'] = ''
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('query', form.errors)
    
    def test_search_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = SearchForm()
        self.assertEqual(form.fields['query'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['query'].widget.attrs['placeholder'], 'Search...')
