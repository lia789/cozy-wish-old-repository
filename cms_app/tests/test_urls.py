from django.test import SimpleTestCase
from django.urls import reverse, resolve
from cms_app import views

class UrlsTest(SimpleTestCase):
    """Test the URLs for the cms_app"""
    
    # Public URLs
    def test_page_detail_url(self):
        """Test the page detail URL"""
        url = reverse('cms_app:page_detail', kwargs={'slug': 'test-page'})
        self.assertEqual(url, '/cms/page/test-page/')
        self.assertEqual(resolve(url).func, views.page_view)
    
    def test_blog_list_url(self):
        """Test the blog list URL"""
        url = reverse('cms_app:blog_list')
        self.assertEqual(url, '/cms/blog/')
        self.assertEqual(resolve(url).func, views.blog_list_view)
    
    def test_blog_detail_url(self):
        """Test the blog detail URL"""
        url = reverse('cms_app:blog_detail', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/blog/test-post/')
        self.assertEqual(resolve(url).func, views.blog_detail_view)
    
    def test_blog_category_url(self):
        """Test the blog category URL"""
        url = reverse('cms_app:blog_category', kwargs={'slug': 'test-category'})
        self.assertEqual(url, '/cms/blog/category/test-category/')
        self.assertEqual(resolve(url).func, views.blog_category_view)
    
    def test_search_url(self):
        """Test the search URL"""
        url = reverse('cms_app:search')
        self.assertEqual(url, '/cms/search/')
        self.assertEqual(resolve(url).func, views.search_view)
    
    # Service Provider URLs
    def test_provider_blog_list_url(self):
        """Test the provider blog list URL"""
        url = reverse('cms_app:provider_blog_list')
        self.assertEqual(url, '/cms/provider/blog/')
        self.assertEqual(resolve(url).func, views.provider_blog_list_view)
    
    def test_provider_blog_create_url(self):
        """Test the provider blog create URL"""
        url = reverse('cms_app:provider_blog_create')
        self.assertEqual(url, '/cms/provider/blog/create/')
        self.assertEqual(resolve(url).func, views.provider_blog_create_view)
    
    def test_provider_blog_update_url(self):
        """Test the provider blog update URL"""
        url = reverse('cms_app:provider_blog_update', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/provider/blog/test-post/edit/')
        self.assertEqual(resolve(url).func, views.provider_blog_update_view)
    
    def test_provider_blog_delete_url(self):
        """Test the provider blog delete URL"""
        url = reverse('cms_app:provider_blog_delete', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/provider/blog/test-post/delete/')
        self.assertEqual(resolve(url).func, views.provider_blog_delete_view)
    
    def test_provider_media_list_url(self):
        """Test the provider media list URL"""
        url = reverse('cms_app:provider_media_list')
        self.assertEqual(url, '/cms/provider/media/')
        self.assertEqual(resolve(url).func, views.provider_media_list_view)
    
    def test_provider_media_upload_url(self):
        """Test the provider media upload URL"""
        url = reverse('cms_app:provider_media_upload')
        self.assertEqual(url, '/cms/provider/media/upload/')
        self.assertEqual(resolve(url).func, views.provider_media_upload_view)
    
    def test_provider_media_delete_url(self):
        """Test the provider media delete URL"""
        url = reverse('cms_app:provider_media_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/cms/provider/media/1/delete/')
        self.assertEqual(resolve(url).func, views.provider_media_delete_view)
    
    # Admin URLs
    def test_admin_page_list_url(self):
        """Test the admin page list URL"""
        url = reverse('cms_app:admin_page_list')
        self.assertEqual(url, '/cms/admin/pages/')
        self.assertEqual(resolve(url).func, views.admin_page_list_view)
    
    def test_admin_page_create_url(self):
        """Test the admin page create URL"""
        url = reverse('cms_app:admin_page_create')
        self.assertEqual(url, '/cms/admin/pages/create/')
        self.assertEqual(resolve(url).func, views.admin_page_create_view)
    
    def test_admin_page_update_url(self):
        """Test the admin page update URL"""
        url = reverse('cms_app:admin_page_update', kwargs={'slug': 'test-page'})
        self.assertEqual(url, '/cms/admin/pages/test-page/edit/')
        self.assertEqual(resolve(url).func, views.admin_page_update_view)
    
    def test_admin_page_delete_url(self):
        """Test the admin page delete URL"""
        url = reverse('cms_app:admin_page_delete', kwargs={'slug': 'test-page'})
        self.assertEqual(url, '/cms/admin/pages/test-page/delete/')
        self.assertEqual(resolve(url).func, views.admin_page_delete_view)
    
    def test_admin_blog_list_url(self):
        """Test the admin blog list URL"""
        url = reverse('cms_app:admin_blog_list')
        self.assertEqual(url, '/cms/admin/blog/')
        self.assertEqual(resolve(url).func, views.admin_blog_list_view)
    
    def test_admin_blog_update_url(self):
        """Test the admin blog update URL"""
        url = reverse('cms_app:admin_blog_update', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/admin/blog/test-post/edit/')
        self.assertEqual(resolve(url).func, views.admin_blog_update_view)
    
    def test_admin_blog_approve_url(self):
        """Test the admin blog approve URL"""
        url = reverse('cms_app:admin_blog_approve', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/admin/blog/test-post/approve/')
        self.assertEqual(resolve(url).func, views.admin_blog_approve_view)
    
    def test_admin_blog_delete_url(self):
        """Test the admin blog delete URL"""
        url = reverse('cms_app:admin_blog_delete', kwargs={'slug': 'test-post'})
        self.assertEqual(url, '/cms/admin/blog/test-post/delete/')
        self.assertEqual(resolve(url).func, views.admin_blog_delete_view)
    
    def test_admin_blog_category_list_url(self):
        """Test the admin blog category list URL"""
        url = reverse('cms_app:admin_blog_category_list')
        self.assertEqual(url, '/cms/admin/blog/categories/')
        self.assertEqual(resolve(url).func, views.admin_blog_category_list_view)
    
    def test_admin_blog_category_create_url(self):
        """Test the admin blog category create URL"""
        url = reverse('cms_app:admin_blog_category_create')
        self.assertEqual(url, '/cms/admin/blog/categories/create/')
        self.assertEqual(resolve(url).func, views.admin_blog_category_create_view)
    
    def test_admin_blog_category_update_url(self):
        """Test the admin blog category update URL"""
        url = reverse('cms_app:admin_blog_category_update', kwargs={'slug': 'test-category'})
        self.assertEqual(url, '/cms/admin/blog/categories/test-category/edit/')
        self.assertEqual(resolve(url).func, views.admin_blog_category_update_view)
    
    def test_admin_blog_category_delete_url(self):
        """Test the admin blog category delete URL"""
        url = reverse('cms_app:admin_blog_category_delete', kwargs={'slug': 'test-category'})
        self.assertEqual(url, '/cms/admin/blog/categories/test-category/delete/')
        self.assertEqual(resolve(url).func, views.admin_blog_category_delete_view)
    
    def test_admin_media_list_url(self):
        """Test the admin media list URL"""
        url = reverse('cms_app:admin_media_list')
        self.assertEqual(url, '/cms/admin/media/')
        self.assertEqual(resolve(url).func, views.admin_media_list_view)
    
    def test_admin_media_upload_url(self):
        """Test the admin media upload URL"""
        url = reverse('cms_app:admin_media_upload')
        self.assertEqual(url, '/cms/admin/media/upload/')
        self.assertEqual(resolve(url).func, views.admin_media_upload_view)
    
    def test_admin_media_delete_url(self):
        """Test the admin media delete URL"""
        url = reverse('cms_app:admin_media_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/cms/admin/media/1/delete/')
        self.assertEqual(resolve(url).func, views.admin_media_delete_view)
    
    def test_admin_site_configuration_url(self):
        """Test the admin site configuration URL"""
        url = reverse('cms_app:admin_site_configuration')
        self.assertEqual(url, '/cms/admin/configuration/')
        self.assertEqual(resolve(url).func, views.admin_site_configuration_view)
    
    def test_admin_announcement_list_url(self):
        """Test the admin announcement list URL"""
        url = reverse('cms_app:admin_announcement_list')
        self.assertEqual(url, '/cms/admin/announcements/')
        self.assertEqual(resolve(url).func, views.admin_announcement_list_view)
    
    def test_admin_announcement_create_url(self):
        """Test the admin announcement create URL"""
        url = reverse('cms_app:admin_announcement_create')
        self.assertEqual(url, '/cms/admin/announcements/create/')
        self.assertEqual(resolve(url).func, views.admin_announcement_create_view)
    
    def test_admin_announcement_update_url(self):
        """Test the admin announcement update URL"""
        url = reverse('cms_app:admin_announcement_update', kwargs={'pk': 1})
        self.assertEqual(url, '/cms/admin/announcements/1/edit/')
        self.assertEqual(resolve(url).func, views.admin_announcement_update_view)
    
    def test_admin_announcement_delete_url(self):
        """Test the admin announcement delete URL"""
        url = reverse('cms_app:admin_announcement_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/cms/admin/announcements/1/delete/')
        self.assertEqual(resolve(url).func, views.admin_announcement_delete_view)
