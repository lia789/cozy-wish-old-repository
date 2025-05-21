from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from cms_app.models import Announcement, SiteConfiguration
from cms_app.context_processors import announcements, site_configuration

User = get_user_model()


class ContextProcessorsTest(TestCase):
    """Test the context processors in the cms_app"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create active announcement
        self.active_announcement = Announcement.objects.create(
            title='Active Announcement',
            content='This is an active announcement.',
            announcement_type='info',
            is_active=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin_user
        )
        
        # Create inactive announcement
        self.inactive_announcement = Announcement.objects.create(
            title='Inactive Announcement',
            content='This is an inactive announcement.',
            announcement_type='warning',
            is_active=False,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            created_by=self.admin_user
        )
        
        # Create future announcement
        self.future_announcement = Announcement.objects.create(
            title='Future Announcement',
            content='This is a future announcement.',
            announcement_type='success',
            is_active=True,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.admin_user
        )
        
        # Create expired announcement
        self.expired_announcement = Announcement.objects.create(
            title='Expired Announcement',
            content='This is an expired announcement.',
            announcement_type='danger',
            is_active=True,
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1),
            created_by=self.admin_user
        )
        
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
            linkedin_url='https://linkedin.com/company/testsite',
            google_analytics_id='UA-12345678-1',
            default_meta_description='Test site description for SEO',
            default_meta_keywords='test, site, keywords',
            maintenance_mode=False,
            maintenance_message='Site is under maintenance.'
        )
    
    def test_announcements_context_processor(self):
        """Test the announcements context processor"""
        request = self.factory.get('/')
        context = announcements(request)
        
        self.assertIn('announcements', context)
        self.assertEqual(len(context['announcements']), 1)
        self.assertEqual(context['announcements'][0], self.active_announcement)
        
        # Check that inactive, future, and expired announcements are not included
        self.assertNotIn(self.inactive_announcement, context['announcements'])
        self.assertNotIn(self.future_announcement, context['announcements'])
        self.assertNotIn(self.expired_announcement, context['announcements'])
    
    def test_site_configuration_context_processor(self):
        """Test the site_configuration context processor"""
        request = self.factory.get('/')
        context = site_configuration(request)
        
        self.assertIn('site_config', context)
        self.assertEqual(context['site_config'], self.site_config)
        
        # Check that the site configuration properties are correct
        self.assertEqual(context['site_config'].site_name, 'Test Site')
        self.assertEqual(context['site_config'].site_description, 'This is a test site.')
        self.assertEqual(context['site_config'].contact_email, 'info@testsite.com')
        self.assertEqual(context['site_config'].contact_phone, '123-456-7890')
        self.assertEqual(context['site_config'].contact_address, '123 Test St, Test City, TS 12345')
        self.assertEqual(context['site_config'].facebook_url, 'https://facebook.com/testsite')
        self.assertEqual(context['site_config'].twitter_url, 'https://twitter.com/testsite')
        self.assertEqual(context['site_config'].instagram_url, 'https://instagram.com/testsite')
        self.assertEqual(context['site_config'].linkedin_url, 'https://linkedin.com/company/testsite')
        self.assertEqual(context['site_config'].google_analytics_id, 'UA-12345678-1')
        self.assertEqual(context['site_config'].default_meta_description, 'Test site description for SEO')
        self.assertEqual(context['site_config'].default_meta_keywords, 'test, site, keywords')
        self.assertFalse(context['site_config'].maintenance_mode)
        self.assertEqual(context['site_config'].maintenance_message, 'Site is under maintenance.')
