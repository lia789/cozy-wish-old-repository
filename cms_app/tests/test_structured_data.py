from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import re

from cms_app.models import BlogPost, BlogCategory, SiteConfiguration

User = get_user_model()


class StructuredDataTest(TestCase):
    """Test structured data in the cms_app"""
    
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
            is_service_provider=True,
            first_name='John',
            last_name='Doe'
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
            author=self.provider_user,
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)
        
        # Create site configuration
        self.site_config = SiteConfiguration.objects.create(
            site_name='Test Site',
            site_description='This is a test site.',
            contact_email='info@testsite.com',
            contact_phone='123-456-7890',
            contact_address='123 Test St, Test City, TS 12345',
            facebook_url='https://facebook.com/testsite',
            twitter_url='https://twitter.com/testsite',
            instagram_url='https://instagram.com/testsite',
            linkedin_url='https://linkedin.com/company/testsite'
        )
        
        # URLs
        self.blog_detail_url = reverse('cms_app:blog_detail', kwargs={'slug': 'test-blog-post'})
        self.blog_list_url = reverse('cms_app:blog_list')
        self.category_url = reverse('cms_app:blog_category', kwargs={'slug': 'test-category'})
    
    def extract_json_ld(self, response):
        """Extract JSON-LD data from response content"""
        content = response.content.decode()
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        json_ld_matches = re.findall(json_ld_pattern, content, re.DOTALL)
        
        if not json_ld_matches:
            return None
        
        return json.loads(json_ld_matches[0])
    
    def test_blog_post_structured_data(self):
        """Test structured data for blog post detail page"""
        response = self.client.get(self.blog_detail_url)
        self.assertEqual(response.status_code, 200)
        
        json_ld = self.extract_json_ld(response)
        self.assertIsNotNone(json_ld)
        
        # Check BlogPosting schema
        self.assertEqual(json_ld['@context'], 'https://schema.org')
        self.assertEqual(json_ld['@type'], 'BlogPosting')
        self.assertEqual(json_ld['headline'], 'Test Blog Post')
        self.assertEqual(json_ld['description'], 'This is a test excerpt.')
        self.assertIn('datePublished', json_ld)
        self.assertIn('dateModified', json_ld)
        
        # Check author
        self.assertEqual(json_ld['author']['@type'], 'Person')
        self.assertEqual(json_ld['author']['name'], 'John Doe')
        
        # Check publisher
        self.assertEqual(json_ld['publisher']['@type'], 'Organization')
        self.assertEqual(json_ld['publisher']['name'], 'Test Site')
        
        # Check mainEntityOfPage
        self.assertEqual(json_ld['mainEntityOfPage']['@type'], 'WebPage')
        self.assertIn(self.blog_detail_url, json_ld['mainEntityOfPage']['@id'])
    
    def test_blog_list_structured_data(self):
        """Test structured data for blog list page"""
        response = self.client.get(self.blog_list_url)
        self.assertEqual(response.status_code, 200)
        
        json_ld = self.extract_json_ld(response)
        self.assertIsNotNone(json_ld)
        
        # Check Blog schema
        self.assertEqual(json_ld['@context'], 'https://schema.org')
        self.assertEqual(json_ld['@type'], 'Blog')
        self.assertEqual(json_ld['name'], 'Test Site Blog')
        self.assertIn('description', json_ld)
        
        # Check blogPosts
        self.assertIn('blogPosts', json_ld)
        self.assertEqual(len(json_ld['blogPosts']), 1)
        self.assertEqual(json_ld['blogPosts'][0]['@type'], 'BlogPosting')
        self.assertEqual(json_ld['blogPosts'][0]['headline'], 'Test Blog Post')
        
        # Check publisher
        self.assertEqual(json_ld['publisher']['@type'], 'Organization')
        self.assertEqual(json_ld['publisher']['name'], 'Test Site')
    
    def test_blog_category_structured_data(self):
        """Test structured data for blog category page"""
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        
        json_ld = self.extract_json_ld(response)
        self.assertIsNotNone(json_ld)
        
        # Check CollectionPage schema
        self.assertEqual(json_ld['@context'], 'https://schema.org')
        self.assertEqual(json_ld['@type'], 'CollectionPage')
        self.assertEqual(json_ld['name'], 'Test Category')
        self.assertEqual(json_ld['description'], 'This is a test category.')
        
        # Check mainEntity
        self.assertIn('mainEntity', json_ld)
        self.assertEqual(json_ld['mainEntity']['@type'], 'ItemList')
        self.assertIn('itemListElement', json_ld['mainEntity'])
        self.assertEqual(len(json_ld['mainEntity']['itemListElement']), 1)
        
        # Check items in the list
        item = json_ld['mainEntity']['itemListElement'][0]
        self.assertEqual(item['@type'], 'ListItem')
        self.assertEqual(item['position'], 1)
        self.assertEqual(item['item']['@type'], 'BlogPosting')
        self.assertEqual(item['item']['headline'], 'Test Blog Post')
