from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate

from accounts_app.models import DeletedAccount
from accounts_app.backends import CustomModelBackend

User = get_user_model()


class CustomModelBackendTest(TestCase):
    """Test the CustomModelBackend."""

    def setUp(self):
        """Set up test data."""
        self.backend = CustomModelBackend()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.deleted_email = 'deleted@example.com'
        DeletedAccount.objects.create(
            email=self.deleted_email,
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )

    def test_authenticate_with_valid_credentials(self):
        """Test authentication with valid credentials."""
        user = authenticate(username='test@example.com', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_password(self):
        """Test authentication with invalid password."""
        user = authenticate(username='test@example.com', password='wrongpassword')
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_user(self):
        """Test authentication with nonexistent user."""
        user = authenticate(username='nonexistent@example.com', password='testpass123')
        self.assertIsNone(user)

    def test_authenticate_with_deleted_account(self):
        """Test authentication with a deleted account."""
        # Create a user with the deleted email
        User.objects.create_user(
            email=self.deleted_email,
            password='testpass123'
        )
        
        # Try to authenticate
        user = authenticate(username=self.deleted_email, password='testpass123')
        self.assertIsNone(user)

    def test_authenticate_with_none_username(self):
        """Test authentication with None username."""
        user = authenticate(username=None, password='testpass123')
        self.assertIsNone(user)

    def test_authenticate_with_none_password(self):
        """Test authentication with None password."""
        user = authenticate(username='test@example.com', password=None)
        self.assertIsNone(user)
