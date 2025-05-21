from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from cms_app.models import (
    Page, BlogPost, BlogCategory, BlogComment,
    MediaItem, Announcement
)

User = get_user_model()


class CommandsTest(TestCase):
    """Test the management commands in the cms_app"""
    
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
        
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create blog posts
        self.published_post = BlogPost.objects.create(
            title='Published Post',
            slug='published-post',
            content='This is a published post.',
            status='published',
            author=self.provider_user,
            published_at=timezone.now() - timedelta(days=30)  # Old post
        )
        
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post.',
            status='draft',
            author=self.provider_user,
            created_at=timezone.now() - timedelta(days=60)  # Old draft
        )
        
        # Create comments
        self.approved_comment = BlogComment.objects.create(
            blog_post=self.published_post,
            author=self.customer_user,
            content='This is an approved comment.',
            status='approved'
        )
        
        self.pending_comment = BlogComment.objects.create(
            blog_post=self.published_post,
            author=self.customer_user,
            content='This is a pending comment.',
            status='pending',
            created_at=timezone.now() - timedelta(days=30)  # Old pending comment
        )
        
        # Create announcements
        self.active_announcement = Announcement.objects.create(
            title='Active Announcement',
            content='This is an active announcement.',
            announcement_type='info',
            is_active=True,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() - timedelta(days=15),  # Expired
            created_by=self.admin_user
        )
    
    def test_cleanup_draft_posts_command(self):
        """Test the cleanup_draft_posts command"""
        # Create a newer draft post that should not be deleted
        newer_draft = BlogPost.objects.create(
            title='Newer Draft Post',
            slug='newer-draft-post',
            content='This is a newer draft post.',
            status='draft',
            author=self.provider_user,
            created_at=timezone.now() - timedelta(days=10)  # Newer draft
        )
        
        # Call the command
        out = StringIO()
        call_command('cleanup_draft_posts', '--days=30', stdout=out)
        
        # Check that old draft posts are deleted
        self.assertFalse(BlogPost.objects.filter(id=self.draft_post.id).exists())
        
        # Check that newer draft posts are not deleted
        self.assertTrue(BlogPost.objects.filter(id=newer_draft.id).exists())
        
        # Check that published posts are not deleted
        self.assertTrue(BlogPost.objects.filter(id=self.published_post.id).exists())
        
        # Check the output
        self.assertIn('Deleted', out.getvalue())
    
    def test_cleanup_pending_comments_command(self):
        """Test the cleanup_pending_comments command"""
        # Create a newer pending comment that should not be deleted
        newer_pending = BlogComment.objects.create(
            blog_post=self.published_post,
            author=self.customer_user,
            content='This is a newer pending comment.',
            status='pending',
            created_at=timezone.now() - timedelta(days=5)  # Newer pending comment
        )
        
        # Call the command
        out = StringIO()
        call_command('cleanup_pending_comments', '--days=15', stdout=out)
        
        # Check that old pending comments are deleted
        self.assertFalse(BlogComment.objects.filter(id=self.pending_comment.id).exists())
        
        # Check that newer pending comments are not deleted
        self.assertTrue(BlogComment.objects.filter(id=newer_pending.id).exists())
        
        # Check that approved comments are not deleted
        self.assertTrue(BlogComment.objects.filter(id=self.approved_comment.id).exists())
        
        # Check the output
        self.assertIn('Deleted', out.getvalue())
    
    def test_cleanup_expired_announcements_command(self):
        """Test the cleanup_expired_announcements command"""
        # Create a newer expired announcement that should not be deleted
        newer_expired = Announcement.objects.create(
            title='Newer Expired Announcement',
            content='This is a newer expired announcement.',
            announcement_type='warning',
            is_active=True,
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5),  # Recently expired
            created_by=self.admin_user
        )
        
        # Create an active announcement that should not be deleted
        active = Announcement.objects.create(
            title='Current Announcement',
            content='This is a current announcement.',
            announcement_type='success',
            is_active=True,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() + timedelta(days=5),  # Not expired
            created_by=self.admin_user
        )
        
        # Call the command
        out = StringIO()
        call_command('cleanup_expired_announcements', '--days=10', stdout=out)
        
        # Check that old expired announcements are deleted
        self.assertFalse(Announcement.objects.filter(id=self.active_announcement.id).exists())
        
        # Check that newer expired announcements are not deleted
        self.assertTrue(Announcement.objects.filter(id=newer_expired.id).exists())
        
        # Check that active announcements are not deleted
        self.assertTrue(Announcement.objects.filter(id=active.id).exists())
        
        # Check the output
        self.assertIn('Deleted', out.getvalue())
