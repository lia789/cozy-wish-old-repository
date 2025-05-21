# Standard library imports
import os

# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify

# Local imports
from utils.image_utils import generate_image_path




# Custom user manager
class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""


    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)




# Custom user model
class CustomUser(AbstractUser):
    """Custom user model using email as the unique identifier instead of username."""

    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default

    objects = CustomUserManager()

    def __str__(self):
        return self.email




# Image path functions 01
def get_profile_image_path(instance, filename):
    """Generate file path for customer profile images"""
    return generate_image_path(
        entity_type='customers',
        entity_id=instance.user.id,
        image_type='profile',
        filename=filename
    )

# Image path functions 02
def get_service_provider_image_path(instance, filename):
    """Generate file path for service provider images"""
    return generate_image_path(
        entity_type='professionals',
        entity_id=instance.user.id,
        image_type='logo',
        filename=filename
    )

# Image path functions 03
def get_staff_image_path(instance, filename):
    """Generate file path for staff profile images"""
    return generate_image_path(
        entity_type='staff',
        entity_id=instance.id,
        image_type='profile',
        filename=filename
    )




# Customer profile model
class CustomerProfile(models.Model):
    """
    Profile model for customers with essential personal and contact information.
    Linked to CustomUser via one-to-one relationship.
    """

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Core relationship
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )

    # Personal information
    profile_picture = models.ImageField(
        upload_to=get_profile_image_path,
        blank=True,
        null=True
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    # Contact information
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of customer profile."""
        return f"{self.user.email}'s Profile"





# Service provider profile model
class ServiceProviderProfile(models.Model):
    """Profile model for service providers with contact information."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='provider_profile'
    )
    profile_picture = models.ImageField(
        upload_to=get_service_provider_image_path,
        blank=True,
        null=True
    )
    business_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    venue_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    contact_person_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of provider profile."""
        return f"{self.user.email}'s Provider Profile"

    def save(self, *args, **kwargs):
        """Generate slug from business name if not provided."""
        if not self.slug:
            self.slug = slugify(self.business_name)
        super().save(*args, **kwargs)





# Staff member model
class StaffMember(models.Model):
    """
    Model for staff members of service providers.
    Stores information about employees working at service provider venues.
    """

    service_provider = models.ForeignKey(
        ServiceProviderProfile,
        on_delete=models.CASCADE,
        related_name='staff_members'
    )
    name = models.CharField(max_length=255)
    profile_image = models.ImageField(
        upload_to=get_staff_image_path,
        blank=True,
        null=True
    )
    designation = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of staff member."""
        return f"{self.name} - {self.designation}"




# User activity model
class UserActivity(models.Model):
    """Model to track user activity"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.timestamp}"




# Login attempt model
class LoginAttempt(models.Model):
    """Model to track login attempts for security monitoring."""

    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = 'Success' if self.was_successful else 'Failed'
        return f"{self.email} - {status} - {self.timestamp}"




# Deleted account model
class DeletedAccount(models.Model):
    """Model to track deleted accounts to prevent re-registration with same email"""

    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-deleted_at']
        verbose_name = 'Deleted Account'
        verbose_name_plural = 'Deleted Accounts'

    def __str__(self):
        return f"{self.email} - deleted on {self.deleted_at}"
