from django.test import TestCase
from django.template import Context, Template
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from cms_app.models import BlogPost, BlogCategory, MediaItem

User = get_user_model()


class TemplateTagsTest(TestCase):
    """Test the template tags in the cms_app"""
    
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
        
        # Create categories
        self.category1 = BlogCategory.objects.create(
            name='Category 1',
            slug='category-1',
            description='This is category 1.'
        )
        
        self.category2 = BlogCategory.objects.create(
            name='Category 2',
            slug='category-2',
            description='This is category 2.'
        )
        
        # Create blog posts
        self.post1 = BlogPost.objects.create(
            title='Post 1',
            slug='post-1',
            content='This is post 1 content.',
            excerpt='This is post 1 excerpt.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now() - timedelta(days=1)
        )
        self.post1.categories.add(self.category1)
        
        self.post2 = BlogPost.objects.create(
            title='Post 2',
            slug='post-2',
            content='This is post 2 content.',
            excerpt='This is post 2 excerpt.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now() - timedelta(days=2)
        )
        self.post2.categories.add(self.category1, self.category2)
        
        self.post3 = BlogPost.objects.create(
            title='Post 3',
            slug='post-3',
            content='This is post 3 content.',
            excerpt='This is post 3 excerpt.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now() - timedelta(days=3)
        )
        self.post3.categories.add(self.category2)
        
        # Create draft post
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post content.',
            status='draft',
            author=self.provider_user
        )
        
        # Create media items
        self.media_item = MediaItem.objects.create(
            title='Test Image',
            file_type='image',
            description='This is a test image.',
            uploaded_by=self.admin_user
        )
    
    def test_recent_posts_tag(self):
        """Test the recent_posts template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{% recent_posts 2 as posts %}'
            '{% for post in posts %}'
            '{{ post.title }}|'
            '{% endfor %}'
        )
        context = Context({})
        rendered = template.render(context)
        
        # Check that the most recent posts are included in the correct order
        self.assertEqual(rendered, 'Post 1|Post 2|')
        
        # Check that draft posts are not included
        self.assertNotIn('Draft Post', rendered)
    
    def test_popular_categories_tag(self):
        """Test the popular_categories template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{% popular_categories as categories %}'
            '{% for category in categories %}'
            '{{ category.name }}({{ category.post_count }})|'
            '{% endfor %}'
        )
        context = Context({})
        rendered = template.render(context)
        
        # Check that categories are ordered by post count
        self.assertEqual(rendered, 'Category 1(2)|Category 2(2)|')
    
    def test_related_posts_tag(self):
        """Test the related_posts template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{% related_posts post 2 as related %}'
            '{% for related_post in related %}'
            '{{ related_post.title }}|'
            '{% endfor %}'
        )
        context = Context({'post': self.post1})
        rendered = template.render(context)
        
        # Check that related posts are included
        self.assertIn('Post 2', rendered)
        
        # Check that the current post is not included
        self.assertNotIn('Post 1', rendered)
        
        # Check that draft posts are not included
        self.assertNotIn('Draft Post', rendered)
    
    def test_format_date_tag(self):
        """Test the format_date template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{{ date|format_date }}'
        )
        context = Context({'date': timezone.now()})
        rendered = template.render(context)
        
        # Check that the date is formatted correctly
        self.assertRegex(rendered, r'\w+ \d+, \d{4}')  # e.g., "January 1, 2023"
    
    def test_truncate_chars_tag(self):
        """Test the truncate_chars template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{{ text|truncate_chars:10 }}'
        )
        context = Context({'text': 'This is a long text that should be truncated.'})
        rendered = template.render(context)
        
        # Check that the text is truncated correctly
        self.assertEqual(rendered, 'This is a...')
    
    def test_get_media_url_tag(self):
        """Test the get_media_url template tag"""
        template = Template(
            '{% load cms_tags %}'
            '{% get_media_url media_id as media_url %}'
            '{{ media_url }}'
        )
        context = Context({'media_id': self.media_item.id})
        rendered = template.render(context)
        
        # Check that the media URL is returned correctly
        self.assertEqual(rendered, self.media_item.file.url)
    
    def test_get_media_url_tag_invalid_id(self):
        """Test the get_media_url template tag with an invalid ID"""
        template = Template(
            '{% load cms_tags %}'
            '{% get_media_url 999 as media_url %}'
            '{{ media_url|default:"Not found" }}'
        )
        context = Context({})
        rendered = template.render(context)
        
        # Check that an empty string is returned for an invalid ID
        self.assertEqual(rendered, 'Not found')
