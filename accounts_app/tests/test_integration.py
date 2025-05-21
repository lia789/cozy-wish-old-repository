from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from accounts_app.models import (
    CustomUser, CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt, DeletedAccount
)

User = get_user_model()


class UserRegistrationAndAuthenticationTest(TestCase):
    """Integration test for user registration and authentication."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.customer_signup_url = reverse('accounts_app:customer_signup')
        self.provider_signup_url = reverse('accounts_app:service_provider_signup')
        self.login_url = reverse('accounts_app:login')
        self.logout_url = reverse('accounts_app:logout')
        self.delete_account_url = reverse('accounts_app:account_delete')

    def test_customer_registration_login_logout_flow(self):
        """Test the complete flow for customer registration, login, and logout."""
        # Step 1: Register a new customer
        response = self.client.post(self.customer_signup_url, {
            'email': 'customer@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
        })
        self.assertRedirects(response, reverse('booking_cart_app:booking_list'), fetch_redirect_response=False)

        # Check that the user was created
        self.assertTrue(User.objects.filter(email='customer@example.com').exists())
        user = User.objects.get(email='customer@example.com')

        # Check that the user is a customer
        self.assertTrue(user.is_customer)

        # Check that a customer profile was created
        self.assertTrue(hasattr(user, 'customer_profile'))

        # Step 2: Logout
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Step 3: Login
        response = self.client.post(self.login_url, {
            'username': 'customer@example.com',
            'password': 'securepassword',
        })
        self.assertRedirects(response, reverse('booking_cart_app:booking_list'), fetch_redirect_response=False)

        # Check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Step 4: Delete account
        response = self.client.post(self.delete_account_url, {
            'confirm_email': 'customer@example.com',
        })
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user was deleted
        self.assertFalse(User.objects.filter(email='customer@example.com').exists())

        # Check that a deleted account record was created
        self.assertTrue(DeletedAccount.objects.filter(email='customer@example.com').exists())

        # Step 5: Try to login with deleted account
        response = self.client.post(self.login_url, {
            'username': 'customer@example.com',
            'password': 'securepassword',
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page

        # Check that the user is not logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_service_provider_registration_login_logout_flow(self):
        """Test the complete flow for service provider registration, login, and logout."""
        # Step 1: Register a new service provider
        response = self.client.post(self.provider_signup_url, {
            'email': 'provider@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'business_name': 'Test Business LLC',
            'phone_number': '+1234567890',
            'contact_person_name': 'Jane Smith',
        })
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'), fetch_redirect_response=False)

        # Check that the user was created
        self.assertTrue(User.objects.filter(email='provider@example.com').exists())
        user = User.objects.get(email='provider@example.com')

        # Check that the user is a service provider
        self.assertTrue(user.is_service_provider)

        # Check that a service provider profile was created
        self.assertTrue(hasattr(user, 'provider_profile'))

        # Step 2: Logout
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('accounts_app:home'), fetch_redirect_response=False)

        # Check that the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Step 3: Login
        response = self.client.post(self.login_url, {
            'username': 'provider@example.com',
            'password': 'securepassword',
        })
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'), fetch_redirect_response=False)

        # Check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class UserProfileManagementTest(TestCase):
    """Integration test for user profile management."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.profile_url = reverse('accounts_app:profile')
        self.change_password_url = reverse('accounts_app:password_change')

        # Create a customer user
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.client.login(username='customer@example.com', password='testpass123')

    def test_view_profile(self):
        """Test viewing the profile page."""
        response = self.client.get(self.profile_url)
        # The profile_url redirects to customer_profile for customer users
        customer_profile_url = reverse('accounts_app:customer_profile')
        self.assertRedirects(response, customer_profile_url)

        # Follow the redirect
        response = self.client.get(customer_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/customer_profile.html')

    def test_update_profile(self):
        """Test updating the profile."""
        # Get the customer profile edit URL
        customer_profile_edit_url = reverse('accounts_app:customer_profile_edit')

        response = self.client.post(customer_profile_edit_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'M',
            'birth_month': 5,
            'birth_year': 1990,
            'phone_number': '+1234567890',
            'address': '123 Main St',
            'city': 'New York',
        })
        # Should redirect to customer_profile
        customer_profile_url = reverse('accounts_app:customer_profile')
        self.assertRedirects(response, customer_profile_url)

        # Check that the profile was updated
        self.user.customer_profile.refresh_from_db()
        self.assertEqual(self.user.customer_profile.first_name, 'John')
        self.assertEqual(self.user.customer_profile.last_name, 'Doe')
        self.assertEqual(self.user.customer_profile.gender, 'M')
        self.assertEqual(self.user.customer_profile.birth_month, 5)
        self.assertEqual(self.user.customer_profile.birth_year, 1990)
        self.assertEqual(self.user.customer_profile.phone_number, '+1234567890')
        self.assertEqual(self.user.customer_profile.address, '123 Main St')
        self.assertEqual(self.user.customer_profile.city, 'New York')

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('profile has been updated' in message.message.lower() for message in messages))

    def test_change_password(self):
        """Test changing the password."""
        response = self.client.post(self.change_password_url, {
            'old_password': 'testpass123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        })
        # First redirect to password_change_done
        password_change_done_url = reverse('accounts_app:password_change_done')
        self.assertRedirects(response, password_change_done_url, fetch_redirect_response=False)

        # Follow the redirect to password_change_done
        response = self.client.get(password_change_done_url)
        # This should redirect to profile
        self.assertRedirects(response, self.profile_url, fetch_redirect_response=False)

        # Check that the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('password has been changed' in message.message.lower() for message in messages))

    def test_change_password_with_incorrect_old_password(self):
        """Test changing the password with incorrect old password."""
        response = self.client.post(self.change_password_url, {
            'old_password': 'wrongpassword',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page

        # Check that the password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpass123'))

        # Check for error message
        self.assertContains(response, 'Your old password was entered incorrectly')
