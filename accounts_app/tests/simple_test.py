from django.test import TestCase
from django.apps import apps


class SimpleTestCase(TestCase):
    """Simple test case to verify that the test setup works correctly."""

    def test_app_installed(self):
        """Test that the accounts_app is installed."""
        self.assertTrue(apps.is_installed('accounts_app'))

    def test_models_exist(self):
        """Test that the models exist."""
        from accounts_app.models import (
            CustomUser, CustomerProfile, ServiceProviderProfile,
            StaffMember, UserActivity, LoginAttempt, DeletedAccount
        )
        self.assertTrue(CustomUser)
        self.assertTrue(CustomerProfile)
        self.assertTrue(ServiceProviderProfile)
        self.assertTrue(StaffMember)
        self.assertTrue(UserActivity)
        self.assertTrue(LoginAttempt)
        self.assertTrue(DeletedAccount)
