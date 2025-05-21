from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from datetime import timedelta

from cms_app.models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)

User = get_user_model()


class PublicViewsTest(TestCase):
    """Test the public views in the cms_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create service provider user
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create customer user
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a page
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

        # Create a draft page
        self.draft_page = Page.objects.create(
            title='Draft Page',
            slug='draft-page',
            content='This is a draft page content.',
            status='draft',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )

        # Create a category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )

        # Create a blog post
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            content='This is a test blog post content.',
            excerpt='This is a test excerpt.',
            meta_description='Test blog post description',
            meta_keywords='test, blog, post, keywords',
            status='published',
            allow_comments=True,
            author=self.provider_user,
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)

        # Create a draft blog post
        self.draft_post = BlogPost.objects.create(
            title='Draft Blog Post',
            slug='draft-blog-post',
            content='This is a draft blog post content.',
            status='draft',
            author=self.provider_user
        )

        # Create a pending blog post
        self.pending_post = BlogPost.objects.create(
            title='Pending Blog Post',
            slug='pending-blog-post',
            content='This is a pending blog post content.',
            status='pending',
            author=self.provider_user
        )

        # Create a comment
        self.comment = BlogComment.objects.create(
            blog_post=self.post,
            author=self.customer_user,
            content='This is a test comment.',
            status='approved'
        )

        # Create a pending comment
        self.pending_comment = BlogComment.objects.create(
            blog_post=self.post,
            author=self.customer_user,
            content='This is a pending comment.',
            status='pending'
        )

        # Create an announcement
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement.',
            announcement_type='info',
            is_active=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin_user
        )

        # Create site configuration
        self.site_config = SiteConfiguration.objects.create(
            site_name='Test Site',
            site_description='This is a test site.',
            contact_email='info@testsite.com'
        )

        # URLs
        self.page_url = reverse('cms_app:page_detail', kwargs={'slug': 'test-page'})
        self.draft_page_url = reverse('cms_app:page_detail', kwargs={'slug': 'draft-page'})
        self.blog_list_url = reverse('cms_app:blog_list')
        self.blog_detail_url = reverse('cms_app:blog_detail', kwargs={'slug': 'test-blog-post'})
        self.draft_blog_url = reverse('cms_app:blog_detail', kwargs={'slug': 'draft-blog-post'})
        self.pending_blog_url = reverse('cms_app:blog_detail', kwargs={'slug': 'pending-blog-post'})
        self.category_url = reverse('cms_app:blog_category', kwargs={'slug': 'test-category'})
        self.search_url = reverse('cms_app:search')

    def test_page_view(self):
        """Test the page view"""
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/page_detail.html')
        self.assertEqual(response.context['page'], self.page)
        self.assertIn('announcements', response.context)
        self.assertIn('site_config', response.context)

    def test_page_view_draft(self):
        """Test the page view with a draft page"""
        response = self.client.get(self.draft_page_url)
        self.assertEqual(response.status_code, 404)

    def test_blog_list_view(self):
        """Test the blog list view"""
        response = self.client.get(self.blog_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/blog_list.html')
        self.assertIn('posts', response.context)
        self.assertIn('featured_posts', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('announcements', response.context)
        self.assertIn('site_config', response.context)

        # Check that only published posts are shown
        self.assertIn(self.post, response.context['posts'])
        self.assertNotIn(self.draft_post, response.context['posts'])
        self.assertNotIn(self.pending_post, response.context['posts'])

    def test_blog_list_view_with_category(self):
        """Test the blog list view with category filter"""
        response = self.client.get(f"{self.blog_list_url}?category={self.category.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/blog_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])

    def test_blog_detail_view(self):
        """Test the blog detail view"""
        response = self.client.get(self.blog_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/blog_detail.html')
        self.assertEqual(response.context['post'], self.post)
        self.assertIn('related_posts', response.context)
        self.assertIn('comments', response.context)
        self.assertIn('comment_form', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('announcements', response.context)
        self.assertIn('site_config', response.context)

        # Check that only approved comments are shown
        self.assertIn(self.comment, response.context['comments'])
        self.assertNotIn(self.pending_comment, response.context['comments'])

    def test_blog_detail_view_draft(self):
        """Test the blog detail view with a draft post"""
        response = self.client.get(self.draft_blog_url)
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_view_pending(self):
        """Test the blog detail view with a pending post"""
        response = self.client.get(self.pending_blog_url)
        self.assertEqual(response.status_code, 404)

    def test_blog_category_view(self):
        """Test the blog category view"""
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/blog_category.html')
        self.assertEqual(response.context['category'], self.category)
        self.assertIn('posts', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('announcements', response.context)
        self.assertIn('site_config', response.context)

        # Check that only published posts are shown
        self.assertIn(self.post, response.context['posts'])
        self.assertNotIn(self.draft_post, response.context['posts'])
        self.assertNotIn(self.pending_post, response.context['posts'])

    def test_search_view(self):
        """Test the search view"""
        response = self.client.get(f"{self.search_url}?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/search_results.html')
        self.assertEqual(response.context['query'], 'test')
        self.assertIn('search_form', response.context)
        self.assertIn('results', response.context)
        self.assertIn('announcements', response.context)
        self.assertIn('site_config', response.context)

    def test_post_comment(self):
        """Test posting a comment"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.post(self.blog_detail_url, {
            'content': 'This is a new comment.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.blog_detail_url)

        # Check that the comment was created
        self.assertTrue(BlogComment.objects.filter(
            blog_post=self.post,
            author=self.customer_user,
            content='This is a new comment.',
            status='pending'
        ).exists())

    def test_post_comment_not_authenticated(self):
        """Test posting a comment when not authenticated"""
        response = self.client.post(self.blog_detail_url, {
            'content': 'This is a new comment.'
        })
        self.assertEqual(response.status_code, 200)  # Returns to the same page

        # Check that no comment was created
        self.assertFalse(BlogComment.objects.filter(
            content='This is a new comment.'
        ).exists())


class ServiceProviderViewsTest(TestCase):
    """Test the service provider views in the cms_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create service provider user
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create another service provider user
        self.other_provider = User.objects.create_user(
            email='other_provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create a category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )

        # Create a blog post by the provider
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            content='This is a test blog post content.',
            excerpt='This is a test excerpt.',
            status='draft',
            author=self.provider_user
        )
        self.post.categories.add(self.category)

        # Create a blog post by another provider
        self.other_post = BlogPost.objects.create(
            title='Other Blog Post',
            slug='other-blog-post',
            content='This is another blog post content.',
            status='draft',
            author=self.other_provider
        )

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_file.write(b'file content')
        self.temp_file.seek(0)

        # Create a media item by the provider
        self.media_item = MediaItem.objects.create(
            title='Test Image',
            file=SimpleUploadedFile(
                name='test_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            file_type='image',
            description='This is a test image.',
            uploaded_by=self.provider_user
        )

        # Reset file pointer
        self.temp_file.seek(0)

        # Create a media item by another provider
        self.other_media = MediaItem.objects.create(
            title='Other Image',
            file=SimpleUploadedFile(
                name='other_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            file_type='image',
            uploaded_by=self.other_provider
        )

        # URLs
        self.blog_list_url = reverse('cms_app:provider_blog_list')
        self.blog_create_url = reverse('cms_app:provider_blog_create')
        self.blog_update_url = reverse('cms_app:provider_blog_update', kwargs={'slug': 'test-blog-post'})
        self.other_blog_update_url = reverse('cms_app:provider_blog_update', kwargs={'slug': 'other-blog-post'})
        self.blog_delete_url = reverse('cms_app:provider_blog_delete', kwargs={'slug': 'test-blog-post'})
        self.other_blog_delete_url = reverse('cms_app:provider_blog_delete', kwargs={'slug': 'other-blog-post'})
        self.media_list_url = reverse('cms_app:provider_media_list')
        self.media_upload_url = reverse('cms_app:provider_media_upload')
        self.media_delete_url = reverse('cms_app:provider_media_delete', kwargs={'pk': self.media_item.pk})
        self.other_media_delete_url = reverse('cms_app:provider_media_delete', kwargs={'pk': self.other_media.pk})

    def tearDown(self):
        """Clean up after tests"""
        self.temp_file.close()

    def test_provider_blog_list_view(self):
        """Test the provider blog list view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        response = self.client.get(self.blog_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/blog_list.html')
        self.assertIn('posts', response.context)

        # Check that only the provider's posts are shown
        self.assertIn(self.post, response.context['posts'])
        self.assertNotIn(self.other_post, response.context['posts'])

    def test_provider_blog_list_view_not_authenticated(self):
        """Test the provider blog list view when not authenticated"""
        response = self.client.get(self.blog_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(
            response,
            f'/accounts/login/?next={self.blog_list_url}'
        )

    def test_provider_blog_create_view(self):
        """Test the provider blog create view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.blog_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/blog_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['is_create'])

        # POST request
        response = self.client.post(self.blog_create_url, {
            'title': 'New Blog Post',
            'content': 'This is a new blog post content.',
            'excerpt': 'This is a new excerpt.',
            'categories': [self.category.id],
            'status': 'draft',
            'allow_comments': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.blog_list_url)

        # Check that the post was created
        self.assertTrue(BlogPost.objects.filter(
            title='New Blog Post',
            content='This is a new blog post content.',
            excerpt='This is a new excerpt.',
            status='draft',
            author=self.provider_user
        ).exists())

    def test_provider_blog_update_view(self):
        """Test the provider blog update view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.blog_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/blog_form.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['is_create'])
        self.assertEqual(response.context['post'], self.post)

        # POST request
        response = self.client.post(self.blog_update_url, {
            'title': 'Updated Blog Post',
            'content': 'This is an updated blog post content.',
            'excerpt': 'This is an updated excerpt.',
            'categories': [self.category.id],
            'status': 'pending',
            'allow_comments': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.blog_list_url)

        # Check that the post was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Blog Post')
        self.assertEqual(self.post.content, 'This is an updated blog post content.')
        self.assertEqual(self.post.excerpt, 'This is an updated excerpt.')
        self.assertEqual(self.post.status, 'pending')

    def test_provider_blog_update_view_other_provider(self):
        """Test the provider blog update view with another provider's post"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.other_blog_update_url)
        self.assertEqual(response.status_code, 404)  # Not found

        # POST request
        response = self.client.post(self.other_blog_update_url, {
            'title': 'Updated Blog Post',
            'content': 'This is an updated blog post content.',
            'status': 'draft'
        })
        self.assertEqual(response.status_code, 404)  # Not found

        # Check that the post was not updated
        self.other_post.refresh_from_db()
        self.assertEqual(self.other_post.title, 'Other Blog Post')

    def test_provider_blog_delete_view(self):
        """Test the provider blog delete view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.blog_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/blog_confirm_delete.html')
        self.assertEqual(response.context['post'], self.post)

        # POST request
        response = self.client.post(self.blog_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.blog_list_url)

        # Check that the post was deleted
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

    def test_provider_blog_delete_view_other_provider(self):
        """Test the provider blog delete view with another provider's post"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.other_blog_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found

        # POST request
        response = self.client.post(self.other_blog_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found

        # Check that the post was not deleted
        self.assertTrue(BlogPost.objects.filter(id=self.other_post.id).exists())

    def test_provider_media_list_view(self):
        """Test the provider media list view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        response = self.client.get(self.media_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/media_list.html')
        self.assertIn('media_items', response.context)

        # Check that only the provider's media items are shown
        self.assertIn(self.media_item, response.context['media_items'])
        self.assertNotIn(self.other_media, response.context['media_items'])

    def test_provider_media_upload_view(self):
        """Test the provider media upload view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.media_upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/media_upload.html')
        self.assertIn('form', response.context)

        # POST request
        self.temp_file.seek(0)
        response = self.client.post(self.media_upload_url, {
            'title': 'New Image',
            'file': SimpleUploadedFile(
                name='new_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            'file_type': 'image',
            'description': 'This is a new image.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.media_list_url)

        # Check that the media item was created
        self.assertTrue(MediaItem.objects.filter(
            title='New Image',
            file_type='image',
            description='This is a new image.',
            uploaded_by=self.provider_user
        ).exists())

    def test_provider_media_delete_view(self):
        """Test the provider media delete view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.media_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/provider/media_confirm_delete.html')
        self.assertEqual(response.context['media_item'], self.media_item)

        # POST request
        response = self.client.post(self.media_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.media_list_url)

        # Check that the media item was deleted
        self.assertFalse(MediaItem.objects.filter(id=self.media_item.id).exists())

    def test_provider_media_delete_view_other_provider(self):
        """Test the provider media delete view with another provider's media item"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.other_media_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found

        # POST request
        response = self.client.post(self.other_media_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found

        # Check that the media item was not deleted
        self.assertTrue(MediaItem.objects.filter(id=self.other_media.id).exists())


class AdminViewsTest(TestCase):
    """Test the admin views in the cms_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # Create service provider user
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create customer user
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a page
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

        # Create a category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='This is a test category.'
        )

        # Create a blog post
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            content='This is a test blog post content.',
            excerpt='This is a test excerpt.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)

        # Create a pending blog post
        self.pending_post = BlogPost.objects.create(
            title='Pending Blog Post',
            slug='pending-blog-post',
            content='This is a pending blog post content.',
            status='pending',
            author=self.provider_user
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
            uploaded_by=self.admin_user
        )

        # Reset file pointer
        self.temp_file.seek(0)

        # Create an announcement
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement.',
            announcement_type='info',
            is_active=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin_user
        )

        # Create site configuration
        self.site_config = SiteConfiguration.objects.create(
            site_name='Test Site',
            site_description='This is a test site.',
            contact_email='info@testsite.com'
        )

        # URLs
        self.admin_page_list_url = reverse('cms_app:admin_page_list')
        self.admin_page_create_url = reverse('cms_app:admin_page_create')
        self.admin_page_update_url = reverse('cms_app:admin_page_update', kwargs={'slug': 'test-page'})
        self.admin_page_delete_url = reverse('cms_app:admin_page_delete', kwargs={'slug': 'test-page'})

        self.admin_blog_list_url = reverse('cms_app:admin_blog_list')
        self.admin_blog_update_url = reverse('cms_app:admin_blog_update', kwargs={'slug': 'test-blog-post'})
        self.admin_blog_approve_url = reverse('cms_app:admin_blog_approve', kwargs={'slug': 'pending-blog-post'})
        self.admin_blog_delete_url = reverse('cms_app:admin_blog_delete', kwargs={'slug': 'test-blog-post'})

        self.admin_blog_category_list_url = reverse('cms_app:admin_blog_category_list')
        self.admin_blog_category_create_url = reverse('cms_app:admin_blog_category_create')
        self.admin_blog_category_update_url = reverse('cms_app:admin_blog_category_update', kwargs={'pk': self.category.id})
        self.admin_blog_category_delete_url = reverse('cms_app:admin_blog_category_delete', kwargs={'pk': self.category.id})

        self.admin_media_list_url = reverse('cms_app:admin_media_list')
        self.admin_media_upload_url = reverse('cms_app:admin_media_upload')
        self.admin_media_delete_url = reverse('cms_app:admin_media_delete', kwargs={'pk': self.media_item.pk})

        self.admin_site_configuration_url = reverse('cms_app:admin_site_configuration')

        self.admin_announcement_list_url = reverse('cms_app:admin_announcement_list')
        self.admin_announcement_create_url = reverse('cms_app:admin_announcement_create')
        self.admin_announcement_update_url = reverse('cms_app:admin_announcement_update', kwargs={'pk': self.announcement.pk})
        self.admin_announcement_delete_url = reverse('cms_app:admin_announcement_delete', kwargs={'pk': self.announcement.pk})

    def tearDown(self):
        """Clean up after tests"""
        self.temp_file.close()

    def test_admin_page_list_view(self):
        """Test the admin page list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/page_list.html')
        self.assertIn('pages', response.context)
        self.assertIn(self.page, response.context['pages'])

    def test_admin_page_list_view_not_admin(self):
        """Test the admin page list view when not admin"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_admin_page_create_view(self):
        """Test the admin page create view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_page_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/page_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['is_create'])

        # POST request
        response = self.client.post(self.admin_page_create_url, {
            'title': 'New Page',
            'content': 'This is a new page content.',
            'meta_description': 'New page description',
            'meta_keywords': 'new, page, keywords',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_page_list_url)

        # Check that the page was created
        self.assertTrue(Page.objects.filter(
            title='New Page',
            content='This is a new page content.',
            meta_description='New page description',
            meta_keywords='new, page, keywords',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        ).exists())

    def test_admin_page_update_view(self):
        """Test the admin page update view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_page_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/page_form.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['is_create'])
        self.assertEqual(response.context['page'], self.page)

        # POST request
        response = self.client.post(self.admin_page_update_url, {
            'title': 'Updated Page',
            'content': 'This is an updated page content.',
            'meta_description': 'Updated page description',
            'meta_keywords': 'updated, page, keywords',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_page_list_url)

        # Check that the page was updated
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, 'Updated Page')
        self.assertEqual(self.page.content, 'This is an updated page content.')
        self.assertEqual(self.page.meta_description, 'Updated page description')
        self.assertEqual(self.page.meta_keywords, 'updated, page, keywords')
        self.assertEqual(self.page.updated_by, self.admin_user)

    def test_admin_page_delete_view(self):
        """Test the admin page delete view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_page_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/page_confirm_delete.html')
        self.assertEqual(response.context['page'], self.page)

        # POST request
        response = self.client.post(self.admin_page_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_page_list_url)

        # Check that the page was deleted
        self.assertFalse(Page.objects.filter(id=self.page.id).exists())

    def test_admin_blog_list_view(self):
        """Test the admin blog list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        response = self.client.get(self.admin_blog_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/blog_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])
        self.assertIn(self.pending_post, response.context['posts'])

    def test_admin_blog_update_view(self):
        """Test the admin blog update view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_blog_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/blog_form.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['is_create'])
        self.assertEqual(response.context['post'], self.post)

        # POST request
        response = self.client.post(self.admin_blog_update_url, {
            'title': 'Updated Blog Post',
            'content': 'This is an updated blog post content.',
            'excerpt': 'This is an updated excerpt.',
            'categories': [self.category.id],
            'status': 'published',
            'allow_comments': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_list_url)

        # Check that the post was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Blog Post')
        self.assertEqual(self.post.content, 'This is an updated blog post content.')
        self.assertEqual(self.post.excerpt, 'This is an updated excerpt.')

    def test_admin_blog_approve_view(self):
        """Test the admin blog approve view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_blog_approve_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/blog_approve.html')
        self.assertEqual(response.context['post'], self.pending_post)

        # POST request - approve
        response = self.client.post(self.admin_blog_approve_url, {
            'action': 'approve',
            'feedback': 'Looks good!',
            'notify_author': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_list_url)

        # Check that the post was approved
        self.pending_post.refresh_from_db()
        self.assertEqual(self.pending_post.status, 'published')
        self.assertIsNotNone(self.pending_post.published_at)

        # Create another pending post for reject test
        reject_post = BlogPost.objects.create(
            title='Reject Blog Post',
            slug='reject-blog-post',
            content='This is a post to be rejected.',
            status='pending',
            author=self.provider_user
        )

        # POST request - reject
        reject_url = reverse('cms_app:admin_blog_approve', kwargs={'slug': 'reject-blog-post'})
        response = self.client.post(reject_url, {
            'action': 'reject',
            'feedback': 'Needs improvement.',
            'notify_author': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_list_url)

        # Check that the post was rejected
        reject_post.refresh_from_db()
        self.assertEqual(reject_post.status, 'draft')

    def test_admin_blog_delete_view(self):
        """Test the admin blog delete view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_blog_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/blog_confirm_delete.html')
        self.assertEqual(response.context['post'], self.post)

        # POST request
        response = self.client.post(self.admin_blog_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_list_url)

        # Check that the post was deleted
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

    def test_admin_blog_category_list_view(self):
        """Test the admin blog category list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        response = self.client.get(self.admin_blog_category_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/blog_category_list.html')
        self.assertIn('categories', response.context)
        self.assertIn(self.category, response.context['categories'])

    def test_admin_blog_category_create_view(self):
        """Test the admin blog category create view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # POST request
        response = self.client.post(self.admin_blog_category_create_url, {
            'name': 'New Category',
            'description': 'This is a new category.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_category_list_url)

        # Check that the category was created
        self.assertTrue(BlogCategory.objects.filter(
            name='New Category',
            description='This is a new category.'
        ).exists())

    def test_admin_blog_category_update_view(self):
        """Test the admin blog category update view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # POST request
        response = self.client.post(self.admin_blog_category_update_url, {
            'name': 'Updated Category',
            'description': 'This is an updated category.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_category_list_url)

        # Check that the category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')
        self.assertEqual(self.category.description, 'This is an updated category.')

    def test_admin_blog_category_delete_view(self):
        """Test the admin blog category delete view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # POST request
        response = self.client.post(self.admin_blog_category_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_blog_category_list_url)

        # Check that the category was deleted
        self.assertFalse(BlogCategory.objects.filter(id=self.category.id).exists())

    def test_admin_media_list_view(self):
        """Test the admin media list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        response = self.client.get(self.admin_media_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/media_list.html')
        self.assertIn('media_items', response.context)
        self.assertIn(self.media_item, response.context['media_items'])

    def test_admin_media_upload_view(self):
        """Test the admin media upload view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_media_upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/media_upload.html')
        self.assertIn('form', response.context)

        # POST request
        self.temp_file.seek(0)
        response = self.client.post(self.admin_media_upload_url, {
            'title': 'New Admin Image',
            'file': SimpleUploadedFile(
                name='new_admin_image.jpg',
                content=self.temp_file.read(),
                content_type='image/jpeg'
            ),
            'file_type': 'image',
            'description': 'This is a new admin image.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_media_list_url)

        # Check that the media item was created
        self.assertTrue(MediaItem.objects.filter(
            title='New Admin Image',
            file_type='image',
            description='This is a new admin image.',
            uploaded_by=self.admin_user
        ).exists())

    def test_admin_media_delete_view(self):
        """Test the admin media delete view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_media_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/media_confirm_delete.html')
        self.assertEqual(response.context['media_item'], self.media_item)

        # POST request
        response = self.client.post(self.admin_media_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_media_list_url)

        # Check that the media item was deleted
        self.assertFalse(MediaItem.objects.filter(id=self.media_item.id).exists())

    def test_admin_site_configuration_view(self):
        """Test the admin site configuration view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_site_configuration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/site_configuration.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['config'], self.site_config)

        # POST request
        response = self.client.post(self.admin_site_configuration_url, {
            'site_name': 'Updated Site',
            'site_description': 'This is an updated site.',
            'contact_email': 'updated@testsite.com',
            'contact_phone': '987-654-3210',
            'contact_address': '456 Updated St, Updated City, US 54321',
            'facebook_url': 'https://facebook.com/updatedsite',
            'twitter_url': 'https://twitter.com/updatedsite',
            'instagram_url': 'https://instagram.com/updatedsite',
            'linkedin_url': 'https://linkedin.com/company/updatedsite',
            'google_analytics_id': 'UA-87654321-1',
            'default_meta_description': 'Updated site description for SEO',
            'default_meta_keywords': 'updated, site, keywords',
            'maintenance_mode': True,
            'maintenance_message': 'Site is under maintenance. Please check back later.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_site_configuration_url)

        # Check that the site configuration was updated
        self.site_config.refresh_from_db()
        self.assertEqual(self.site_config.site_name, 'Updated Site')
        self.assertEqual(self.site_config.site_description, 'This is an updated site.')
        self.assertEqual(self.site_config.contact_email, 'updated@testsite.com')
        self.assertEqual(self.site_config.contact_phone, '987-654-3210')
        self.assertEqual(self.site_config.contact_address, '456 Updated St, Updated City, US 54321')
        self.assertEqual(self.site_config.facebook_url, 'https://facebook.com/updatedsite')
        self.assertEqual(self.site_config.twitter_url, 'https://twitter.com/updatedsite')
        self.assertEqual(self.site_config.instagram_url, 'https://instagram.com/updatedsite')
        self.assertEqual(self.site_config.linkedin_url, 'https://linkedin.com/company/updatedsite')
        self.assertEqual(self.site_config.google_analytics_id, 'UA-87654321-1')
        self.assertEqual(self.site_config.default_meta_description, 'Updated site description for SEO')
        self.assertEqual(self.site_config.default_meta_keywords, 'updated, site, keywords')
        self.assertTrue(self.site_config.maintenance_mode)
        self.assertEqual(self.site_config.maintenance_message, 'Site is under maintenance. Please check back later.')

    def test_admin_announcement_list_view(self):
        """Test the admin announcement list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        response = self.client.get(self.admin_announcement_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/announcement_list.html')
        self.assertIn('announcements', response.context)
        self.assertIn(self.announcement, response.context['announcements'])

    def test_admin_announcement_create_view(self):
        """Test the admin announcement create view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_announcement_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/announcement_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['is_create'])

        # POST request
        response = self.client.post(self.admin_announcement_create_url, {
            'title': 'New Announcement',
            'content': 'This is a new announcement.',
            'announcement_type': 'success',
            'is_active': True,
            'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_announcement_list_url)

        # Check that the announcement was created
        self.assertTrue(Announcement.objects.filter(
            title='New Announcement',
            content='This is a new announcement.',
            announcement_type='success',
            is_active=True,
            created_by=self.admin_user
        ).exists())

    def test_admin_announcement_update_view(self):
        """Test the admin announcement update view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_announcement_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/announcement_form.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['is_create'])
        self.assertEqual(response.context['announcement'], self.announcement)

        # POST request
        response = self.client.post(self.admin_announcement_update_url, {
            'title': 'Updated Announcement',
            'content': 'This is an updated announcement.',
            'announcement_type': 'warning',
            'is_active': True,
            'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_date': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M')
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_announcement_list_url)

        # Check that the announcement was updated
        self.announcement.refresh_from_db()
        self.assertEqual(self.announcement.title, 'Updated Announcement')
        self.assertEqual(self.announcement.content, 'This is an updated announcement.')
        self.assertEqual(self.announcement.announcement_type, 'warning')

    def test_admin_announcement_delete_view(self):
        """Test the admin announcement delete view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # GET request
        response = self.client.get(self.admin_announcement_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms_app/admin/announcement_confirm_delete.html')
        self.assertEqual(response.context['announcement'], self.announcement)

        # POST request
        response = self.client.post(self.admin_announcement_delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertRedirects(response, self.admin_announcement_list_url)

        # Check that the announcement was deleted
        self.assertFalse(Announcement.objects.filter(id=self.announcement.id).exists())
