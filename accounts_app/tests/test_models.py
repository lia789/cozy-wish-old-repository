from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from accounts_app.models import (
    CustomUser, CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt, DeletedAccount
)

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test the CustomUser model."""

    def test_create_user(self):
        """Test creating a user with email and password."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_customer)
        self.assertFalse(user.is_service_provider)
        self.assertFalse(user.email_verified)
        self.assertTrue(user.is_active)

    def test_create_user_without_email(self):
        """Test creating a user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_str_method(self):
        """Test the string representation of a user."""
        email = 'test@example.com'
        user = User.objects.create_user(
            email=email,
            password='testpass123'
        )
        self.assertEqual(str(user), email)


class CustomerProfileModelTest(TestCase):
    """Test the CustomerProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.profile = self.user.customer_profile

    def test_profile_creation(self):
        """Test profile is created for customer user."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str_method(self):
        """Test the string representation of a profile."""
        expected_str = f"{self.user.email}'s Profile"
        self.assertEqual(str(self.profile), expected_str)

    def test_profile_update(self):
        """Test updating profile fields."""
        self.profile.first_name = 'John'
        self.profile.last_name = 'Doe'
        self.profile.gender = 'M'
        self.profile.birth_month = 5
        self.profile.birth_year = 1990
        self.profile.phone_number = '+1234567890'
        self.profile.address = '123 Main St'
        self.profile.city = 'New York'
        self.profile.save()

        # Refresh from database
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.first_name, 'John')
        self.assertEqual(self.profile.last_name, 'Doe')
        self.assertEqual(self.profile.gender, 'M')
        self.assertEqual(self.profile.birth_month, 5)
        self.assertEqual(self.profile.birth_year, 1990)
        self.assertEqual(self.profile.phone_number, '+1234567890')
        self.assertEqual(self.profile.address, '123 Main St')
        self.assertEqual(self.profile.city, 'New York')


class ServiceProviderProfileModelTest(TestCase):
    """Test the ServiceProviderProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        self.profile = self.user.provider_profile

    def test_profile_creation(self):
        """Test profile is created for service provider user."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str_method(self):
        """Test the string representation of a profile."""
        expected_str = f"{self.user.email}'s Provider Profile"
        self.assertEqual(str(self.profile), expected_str)

    def test_profile_update(self):
        """Test updating profile fields."""
        self.profile.phone_number = '+1234567890'
        self.profile.contact_person_name = 'Jane Smith'
        self.profile.contact_person_email = 'jane@example.com'
        self.profile.save()

        # Refresh from database
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.phone_number, '+1234567890')
        self.assertEqual(self.profile.contact_person_name, 'Jane Smith')
        self.assertEqual(self.profile.contact_person_email, 'jane@example.com')


class StaffMemberModelTest(TestCase):
    """Test the StaffMember model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        self.provider_profile = self.user.provider_profile
        self.provider_profile.phone_number = '+1234567890'
        self.provider_profile.contact_person_name = 'Jane Smith'
        self.provider_profile.contact_person_email = 'jane@example.com'
        self.provider_profile.save()

        self.staff = StaffMember.objects.create(
            service_provider=self.provider_profile,
            name='John Doe',
            designation='Hair Stylist',
            is_active=True
        )

    def test_staff_creation(self):
        """Test creating a staff member."""
        self.assertEqual(self.staff.service_provider, self.provider_profile)
        self.assertEqual(self.staff.name, 'John Doe')
        self.assertEqual(self.staff.designation, 'Hair Stylist')
        self.assertTrue(self.staff.is_active)

    def test_staff_str_method(self):
        """Test the string representation of a staff member."""
        expected_str = f"John Doe - Hair Stylist"
        self.assertEqual(str(self.staff), expected_str)

    def test_staff_update(self):
        """Test updating staff fields."""
        self.staff.name = 'Jane Doe'
        self.staff.designation = 'Makeup Artist'
        self.staff.is_active = False
        self.staff.save()

        # Refresh from database
        self.staff.refresh_from_db()

        self.assertEqual(self.staff.name, 'Jane Doe')
        self.assertEqual(self.staff.designation, 'Makeup Artist')
        self.assertFalse(self.staff.is_active)


class UserActivityModelTest(TestCase):
    """Test the UserActivity model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.activity = UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            details='Logged in from Chrome'
        )

    def test_activity_creation(self):
        """Test creating a user activity."""
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.activity_type, 'login')
        self.assertEqual(self.activity.ip_address, '127.0.0.1')
        self.assertEqual(self.activity.user_agent, 'Mozilla/5.0')
        self.assertEqual(self.activity.details, 'Logged in from Chrome')

    def test_activity_str_method(self):
        """Test the string representation of an activity."""
        expected_str = f"{self.user.email} - login - {self.activity.timestamp}"
        self.assertEqual(str(self.activity), expected_str)


class LoginAttemptModelTest(TestCase):
    """Test the LoginAttempt model."""

    def setUp(self):
        """Set up test data."""
        self.login_attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            was_successful=True
        )

    def test_login_attempt_creation(self):
        """Test creating a login attempt."""
        self.assertEqual(self.login_attempt.email, 'test@example.com')
        self.assertEqual(self.login_attempt.ip_address, '127.0.0.1')
        self.assertEqual(self.login_attempt.user_agent, 'Mozilla/5.0')
        self.assertTrue(self.login_attempt.was_successful)

    def test_login_attempt_str_method(self):
        """Test the string representation of a login attempt."""
        expected_str = f"test@example.com - Success - {self.login_attempt.timestamp}"
        self.assertEqual(str(self.login_attempt), expected_str)

    def test_failed_login_attempt_str_method(self):
        """Test the string representation of a failed login attempt."""
        failed_attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            was_successful=False
        )
        expected_str = f"test@example.com - Failed - {failed_attempt.timestamp}"
        self.assertEqual(str(failed_attempt), expected_str)


class DeletedAccountModelTest(TestCase):
    """Test the DeletedAccount model."""

    def setUp(self):
        """Set up test data."""
        self.deleted_account = DeletedAccount.objects.create(
            email='deleted@example.com',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )

    def test_deleted_account_creation(self):
        """Test creating a deleted account record."""
        self.assertEqual(self.deleted_account.email, 'deleted@example.com')
        self.assertEqual(self.deleted_account.ip_address, '127.0.0.1')
        self.assertEqual(self.deleted_account.user_agent, 'Mozilla/5.0')

    def test_deleted_account_str_method(self):
        """Test the string representation of a deleted account."""
        expected_str = f"deleted@example.com - deleted on {self.deleted_account.deleted_at}"
        self.assertEqual(str(self.deleted_account), expected_str)

    def test_unique_email_constraint(self):
        """Test that email must be unique for deleted accounts."""
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            DeletedAccount.objects.create(
                email='deleted@example.com',
                ip_address='192.168.1.1',
                user_agent='Firefox'
            )
