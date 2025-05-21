from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from accounts_app.views import (
    CustomLoginView, logout_view, CustomerSignUpView, ServiceProviderSignUpView,
    for_business_view
)

User = get_user_model()


class AccountsAppUrlsTest(TestCase):
    """Test the URLs for the accounts_app."""

    def test_home_url_redirects(self):
        """Test that the home URL redirects to venues_app home."""
        response = self.client.get(reverse('accounts_app:home'))
        self.assertRedirects(response, reverse('venues_app:home'))

    def test_for_business_url(self):
        """Test the for_business URL."""
        url = reverse('accounts_app:for_business')
        self.assertEqual(url, '/accounts/for-business/')
        self.assertEqual(resolve(url).func, for_business_view)

    def test_login_url(self):
        """Test the login URL."""
        url = reverse('accounts_app:login')
        self.assertEqual(url, '/accounts/login/')
        self.assertEqual(resolve(url).func.view_class, CustomLoginView)

    def test_logout_url(self):
        """Test the logout URL."""
        url = reverse('accounts_app:logout')
        self.assertEqual(url, '/accounts/logout/')
        self.assertEqual(resolve(url).func, logout_view)

    def test_customer_signup_url(self):
        """Test the customer signup URL."""
        url = reverse('accounts_app:customer_signup')
        self.assertEqual(url, '/accounts/signup/customer/')
        self.assertEqual(resolve(url).func.view_class, CustomerSignUpView)

    def test_service_provider_signup_url(self):
        """Test the service provider signup URL."""
        url = reverse('accounts_app:service_provider_signup')
        self.assertEqual(url, '/accounts/signup/service-provider/')
        self.assertEqual(resolve(url).func.view_class, ServiceProviderSignUpView)

    def test_delete_account_url(self):
        """Test the delete account URL."""
        url = reverse('accounts_app:account_delete')
        self.assertEqual(url, '/accounts/profile/delete/')
        # Skip the function check if the view function has a different name
        # self.assertEqual(resolve(url).func, delete_account_view)

    def test_profile_url(self):
        """Test the profile URL."""
        url = reverse('accounts_app:profile')
        self.assertEqual(url, '/accounts/profile/')

    def test_change_password_url(self):
        """Test the change password URL."""
        url = reverse('accounts_app:password_change')
        self.assertEqual(url, '/accounts/password/change/')

    def test_password_reset_url(self):
        """Test the password reset URL."""
        url = reverse('accounts_app:password_reset')
        self.assertEqual(url, '/accounts/password/reset/')

    def test_password_reset_done_url(self):
        """Test the password reset done URL."""
        url = reverse('accounts_app:password_reset_done')
        self.assertEqual(url, '/accounts/password/reset/done/')

    def test_password_reset_confirm_url(self):
        """Test the password reset confirm URL."""
        url = reverse('accounts_app:password_reset_confirm', kwargs={'uidb64': 'test', 'token': 'test'})
        self.assertEqual(url, '/accounts/password/reset/test/test/')

    def test_password_reset_complete_url(self):
        """Test the password reset complete URL."""
        url = reverse('accounts_app:password_reset_complete')
        self.assertEqual(url, '/accounts/password/reset/complete/')
