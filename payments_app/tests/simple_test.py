from django.test import SimpleTestCase

class SimpleTest(SimpleTestCase):
    def test_basic_addition(self):
        """Tests that 1 + 1 = 2"""
        self.assertEqual(1 + 1, 2)
        print("Simple test passed!")
