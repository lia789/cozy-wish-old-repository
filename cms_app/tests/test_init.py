from django.test import TestCase
from cms_app.apps import CmsAppConfig


class InitTest(TestCase):
    """Test the cms_app initialization"""
    
    def test_app_config(self):
        """Test the app configuration"""
        self.assertEqual(CmsAppConfig.name, 'cms_app')
        self.assertEqual(CmsAppConfig.verbose_name, 'CMS App')
