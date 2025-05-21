from django.test import TestCase
from .models import NotificationCategory


class SimpleTest(TestCase):
    def test_category_creation(self):
        """Test creating a notification category"""
        category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description',
            icon='fa-bell',
            color='primary'
        )
        
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.description, 'Test description')
        self.assertEqual(category.icon, 'fa-bell')
        self.assertEqual(category.color, 'primary')
