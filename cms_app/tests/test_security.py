from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from cms_app.models import Page, BlogPost, MediaItem

User = get_user_model()


class SecurityTest(TestCase):
    """Test security measures in the cms_app"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
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
        
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create a page
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='This is a test page.',
            status='published',
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
        
        # Create a blog post
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now()
        )
        
        # Create a media item
        self.media_item = MediaItem.objects.create(
            title='Test Image',
            file_type='image',
            uploaded_by=self.provider_user
        )
        
        # URLs
        self.admin_page_list_url = reverse('cms_app:admin_page_list')
        self.admin_page_create_url = reverse('cms_app:admin_page_create')
        self.admin_page_update_url = reverse('cms_app:admin_page_update', kwargs={'slug': 'test-page'})
        self.admin_page_delete_url = reverse('cms_app:admin_page_delete', kwargs={'slug': 'test-page'})
        
        self.provider_blog_list_url = reverse('cms_app:provider_blog_list')
        self.provider_blog_create_url = reverse('cms_app:provider_blog_create')
        self.provider_blog_update_url = reverse('cms_app:provider_blog_update', kwargs={'slug': 'test-post'})
        self.provider_blog_delete_url = reverse('cms_app:provider_blog_delete', kwargs={'slug': 'test-post'})
        
        self.provider_media_list_url = reverse('cms_app:provider_media_list')
        self.provider_media_upload_url = reverse('cms_app:provider_media_upload')
        self.provider_media_delete_url = reverse('cms_app:provider_media_delete', kwargs={'pk': self.media_item.pk})
    
    def test_admin_views_require_admin_permissions(self):
        """Test that admin views require admin permissions"""
        # Test with unauthenticated user
        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with customer user
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with provider user
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with admin user
        self.client.login(username='admin@example.com', password='testpass123')
        response = self.client.get(self.admin_page_list_url)
        self.assertEqual(response.status_code, 200)  # OK
    
    def test_provider_views_require_provider_permissions(self):
        """Test that provider views require provider permissions"""
        # Test with unauthenticated user
        response = self.client.get(self.provider_blog_list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with customer user
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.provider_blog_list_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with provider user
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.provider_blog_list_url)
        self.assertEqual(response.status_code, 200)  # OK
        
        # Test with admin user (admin should also have access)
        self.client.login(username='admin@example.com', password='testpass123')
        response = self.client.get(self.provider_blog_list_url)
        self.assertEqual(response.status_code, 200)  # OK
    
    def test_provider_cannot_access_other_providers_content(self):
        """Test that a provider cannot access another provider's content"""
        # Create another provider
        other_provider = User.objects.create_user(
            email='other_provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create a blog post by the other provider
        other_post = BlogPost.objects.create(
            title='Other Post',
            slug='other-post',
            content='This is another provider\'s post.',
            status='published',
            author=other_provider,
            published_at=timezone.now()
        )
        
        # Create a media item by the other provider
        other_media = MediaItem.objects.create(
            title='Other Image',
            file_type='image',
            uploaded_by=other_provider
        )
        
        # URLs for other provider's content
        other_blog_update_url = reverse('cms_app:provider_blog_update', kwargs={'slug': 'other-post'})
        other_blog_delete_url = reverse('cms_app:provider_blog_delete', kwargs={'slug': 'other-post'})
        other_media_delete_url = reverse('cms_app:provider_media_delete', kwargs={'pk': other_media.pk})
        
        # Login as the first provider
        self.client.login(username='provider@example.com', password='testpass123')
        
        # Try to access other provider's blog post
        response = self.client.get(other_blog_update_url)
        self.assertEqual(response.status_code, 404)  # Not found
        
        response = self.client.post(other_blog_update_url, {
            'title': 'Hacked Post',
            'content': 'This post has been hacked.',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Try to delete other provider's blog post
        response = self.client.post(other_blog_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Check that the post was not deleted
        self.assertTrue(BlogPost.objects.filter(slug='other-post').exists())
        
        # Try to delete other provider's media item
        response = self.client.post(other_media_delete_url)
        self.assertEqual(response.status_code, 404)  # Not found
        
        # Check that the media item was not deleted
        self.assertTrue(MediaItem.objects.filter(id=other_media.pk).exists())
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Get the CSRF token
        response = self.client.get(self.admin_page_create_url)
        self.assertEqual(response.status_code, 200)
        
        # Create a client with CSRF checking disabled
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username='admin@example.com', password='testpass123')
        
        # Try to submit a form without CSRF token
        response = csrf_client.post(self.admin_page_create_url, {
            'title': 'CSRF Test Page',
            'content': 'This is a CSRF test page.',
            'status': 'published'
        })
        
        # Should be rejected due to missing CSRF token
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Check that the page was not created
        self.assertFalse(Page.objects.filter(title='CSRF Test Page').exists())
    
    def test_xss_protection(self):
        """Test XSS protection"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')
        
        # Try to create a page with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        response = self.client.post(self.admin_page_create_url, {
            'title': 'XSS Test Page',
            'content': f'This is a test page with {xss_payload}',
            'status': 'published'
        })
        
        # Should be created successfully
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        
        # Get the created page
        xss_page = Page.objects.get(title='XSS Test Page')
        
        # View the page
        response = self.client.get(reverse('cms_app:page_detail', kwargs={'slug': xss_page.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Check that the XSS payload is escaped in the response
        self.assertNotIn(xss_payload, response.content.decode())
        self.assertIn('&lt;script&gt;', response.content.decode())
