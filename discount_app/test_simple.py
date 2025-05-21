from django.test import TestCase
from django.urls import reverse


class SimpleTest(TestCase):
    def test_test_view(self):
        """Test the test view"""
        response = self.client.get(reverse('discount_app:test_view'))
        self.assertEqual(response.status_code, 200)
