from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts_app.models import CustomerProfile, ServiceProviderProfile
from accounts_app.signals import create_user_profile

User = get_user_model()


class SignalsTest(TestCase):
    """Test the signals in the accounts_app."""

    def test_customer_profile_created_on_user_creation(self):
        """Test that a customer profile is created when a customer user is created."""
        user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Check that a customer profile was created
        self.assertTrue(hasattr(user, 'customer_profile'))
        self.assertIsInstance(user.customer_profile, CustomerProfile)

    def test_service_provider_profile_created_on_user_creation(self):
        """Test that a service provider profile is created when a service provider user is created."""
        user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Check that a service provider profile was created
        self.assertTrue(hasattr(user, 'provider_profile'))
        self.assertIsInstance(user.provider_profile, ServiceProviderProfile)

    def test_no_profile_created_for_regular_user(self):
        """Test that no profile is created for a regular user."""
        user = User.objects.create_user(
            email='regular@example.com',
            password='testpass123'
        )
        
        # Check that no customer profile was created
        self.assertFalse(hasattr(user, 'customer_profile'))
        
        # Check that no service provider profile was created
        self.assertFalse(hasattr(user, 'provider_profile'))

    def test_signal_disconnection_and_reconnection(self):
        """Test that the signal can be disconnected and reconnected."""
        # Disconnect the signal
        post_save.disconnect(create_user_profile, sender=User)
        
        # Create a user
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Check that no profile was created
        self.assertFalse(hasattr(user, 'customer_profile'))
        
        # Reconnect the signal
        post_save.connect(create_user_profile, sender=User)
        
        # Create another user
        user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Check that a profile was created
        self.assertTrue(hasattr(user2, 'customer_profile'))
        self.assertIsInstance(user2.customer_profile, CustomerProfile)
