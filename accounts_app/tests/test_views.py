from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from accounts_app.models import (
    CustomUser, CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt, DeletedAccount
)

User = get_user_model()


class CustomLoginViewTest(TestCase):
    """Test the CustomLoginView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.login_url = reverse('accounts_app:login')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_successful_login(self):
        """Test successful login."""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123',
        })
        # The login view redirects to booking_cart_app:booking_list for customers,
        # dashboard_app:provider_dashboard for service providers, or accounts_app:home if neither
        # Since our test user doesn't have a specific type, it should redirect to accounts_app:home
        # which in turn redirects to venues_app:home
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)

        # Check that a login attempt was recorded
        self.assertTrue(LoginAttempt.objects.filter(
            email='test@example.com',
            was_successful=True
        ).exists())

        # Check that user activity was recorded
        self.assertTrue(UserActivity.objects.filter(
            user=self.user,
            activity_type='login'
        ).exists())

    def test_failed_login(self):
        """Test failed login."""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page

        # Check that the user is not logged in
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

        # Check that a failed login attempt was recorded
        self.assertTrue(LoginAttempt.objects.filter(
            email='test@example.com',
            was_successful=False
        ).exists())


class LogoutViewTest(TestCase):
    """Test the logout_view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.logout_url = reverse('accounts_app:logout')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')

    def test_logout(self):
        """Test logout."""
        response = self.client.get(self.logout_url)
        # The logout view redirects to accounts_app:home, which then redirects to venues_app:home
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user is logged out
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

        # Check that user activity was recorded
        self.assertTrue(UserActivity.objects.filter(
            user=self.user,
            activity_type='logout'
        ).exists())


class CustomerSignUpViewTest(TestCase):
    """Test the CustomerSignUpView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.signup_url = reverse('accounts_app:customer_signup')

    def test_signup_page_loads(self):
        """Test that the signup page loads correctly."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/customer_signup.html')

    def test_successful_signup(self):
        """Test successful signup."""
        response = self.client.post(self.signup_url, {
            'email': 'newcustomer@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
        })
        # The signup view redirects to booking_cart_app:booking_list
        self.assertRedirects(response, reverse('booking_cart_app:booking_list'), fetch_redirect_response=False)

        # Check that the user was created
        self.assertTrue(User.objects.filter(email='newcustomer@example.com').exists())
        user = User.objects.get(email='newcustomer@example.com')

        # Check that the user is a customer
        self.assertTrue(user.is_customer)

        # Check that a customer profile was created
        self.assertTrue(hasattr(user, 'customer_profile'))

        # Check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == 'Your account has been created successfully. Welcome to CozyWish!' for message in messages))

    def test_signup_with_existing_email(self):
        """Test signup with an email that already exists."""
        # Create a user with the email
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123'
        )

        # Try to sign up with the same email
        response = self.client.post(self.signup_url, {
            'email': 'existing@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page

        # Check for error message
        self.assertContains(response, 'A user with this email already exists')


class ServiceProviderSignUpViewTest(TestCase):
    """Test the ServiceProviderSignUpView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.signup_url = reverse('accounts_app:service_provider_signup')

    def test_signup_page_loads(self):
        """Test that the signup page loads correctly."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/service_provider_signup.html')

    def test_successful_signup(self):
        """Test successful signup."""
        response = self.client.post(self.signup_url, {
            'email': 'newprovider@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'business_name': 'Test Business LLC',
            'phone_number': '+1234567890',
            'contact_person_name': 'Jane Smith',
        })
        # The service provider signup view redirects to dashboard_app:provider_dashboard
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))

        # Check that the user was created
        self.assertTrue(User.objects.filter(email='newprovider@example.com').exists())
        user = User.objects.get(email='newprovider@example.com')

        # Check that the user is a service provider
        self.assertTrue(user.is_service_provider)

        # Check that a service provider profile was created
        self.assertTrue(hasattr(user, 'provider_profile'))

        # Check that the profile has the correct data
        profile = user.provider_profile
        self.assertEqual(profile.business_name, 'Test Business LLC')
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.contact_person_name, 'Jane Smith')

        # Check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == 'Your account has been created successfully. Welcome to CozyWish!' for message in messages))


class ForBusinessViewTest(TestCase):
    """Test the for_business_view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.for_business_url = reverse('accounts_app:for_business')

    def test_for_business_page_loads(self):
        """Test that the for business page loads correctly."""
        response = self.client.get(self.for_business_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/for_business.html')


class DeleteAccountViewTest(TestCase):
    """Test the delete_account_view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.delete_account_url = reverse('accounts_app:account_delete')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')

    def test_delete_account_confirmation_page_loads(self):
        """Test that the delete account confirmation page loads correctly."""
        response = self.client.get(self.delete_account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/account_confirm_delete.html')

    def test_delete_account(self):
        """Test deleting an account."""
        response = self.client.post(self.delete_account_url, {
            'confirm_email': 'test@example.com',
        })
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user was deleted
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

        # Check that a deleted account record was created
        self.assertTrue(DeletedAccount.objects.filter(email='test@example.com').exists())

        # Check that the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == 'Your account has been deleted successfully.' for message in messages))

    def test_account_delete_view_get(self):
        """Test that the account delete view loads correctly."""
        response = self.client.get(self.delete_account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/account_confirm_delete.html')

    def test_cannot_login_after_account_deletion(self):
        """Test that a user cannot log in after their account has been deleted."""
        # Create a user
        email = 'delete_test@example.com'
        password = 'securepassword'
        user = User.objects.create_user(
            email=email,
            password=password
        )

        # Login to verify the account works
        login_success = self.client.login(username=email, password=password)
        self.assertTrue(login_success)

        # Logout
        self.client.logout()

        # Delete the account
        self.client.login(username=email, password=password)
        response = self.client.post(self.delete_account_url, {
            'confirm_email': email,
        })

        # Verify the user was deleted and a DeletedAccount record was created
        self.assertFalse(User.objects.filter(email=email).exists())
        self.assertTrue(DeletedAccount.objects.filter(email=email).exists())

        # Try to login again - this should fail
        login_success = self.client.login(username=email, password=password)
        self.assertFalse(login_success)

        # Try to login via the form
        login_url = reverse('accounts_app:login')
        response = self.client.post(login_url, {
            'username': email,
            'password': password,
        })

        # Should stay on login page (not redirect to success URL)
        self.assertEqual(response.status_code, 200)

        # User should not be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
