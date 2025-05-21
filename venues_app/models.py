# Standard library imports
import os
from decimal import Decimal

# Django imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify

# Local imports
from utils.image_utils import generate_image_path


# Image upload path for venues
def venue_image_path(instance, filename):
    """Generate file path for venue images"""
    return generate_image_path(
        entity_type='venues',
        entity_id=instance.venue.id,
        image_type='venue',
        filename=filename
    )



# Category model
class Category(models.Model):
    """Category model for venues"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)





class Tag(models.Model):
    """Tag model for venues"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)




class Venue(models.Model):
    """Venue model for service providers"""
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    VENUE_TYPE_CHOICES = [
        ('all', 'All Genders'),
        ('male', 'Male Only'),
        ('female', 'Female Only'),
    ]

    # Basic information
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='venues')
    tags = models.ManyToManyField(Tag, blank=True, related_name='venues')
    venue_type = models.CharField(max_length=10, choices=VENUE_TYPE_CHOICES, default='all')

    # Location information
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    us_city = models.ForeignKey('USCity', on_delete=models.SET_NULL, null=True, blank=True, related_name='venues')

    # Description
    about = models.TextField(help_text="Short venue description")

    # Status and timestamps
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Try to find and link to a US city if not already set
        if not self.us_city and self.city and self.state:
            from django.db.models import Q
            # Try to find a matching city
            city_match = USCity.objects.filter(
                Q(city__iexact=self.city) &
                (Q(state_name__iexact=self.state) | Q(state_id__iexact=self.state))
            ).first()

            if city_match:
                self.us_city = city_match
                # Always update coordinates from the city to ensure they match
                self.latitude = city_match.latitude
                self.longitude = city_match.longitude

        super().save(*args, **kwargs)


    def get_full_address(self):
        """Return the full address as a string"""
        return f"{self.street_number} {self.street_name}, {self.city}, {self.state}"

    def get_average_rating(self):
        """Calculate the average rating for this venue using review_app reviews"""
        avg = self.review_app_reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def get_review_count(self):
        """Return the number of reviews for this venue using review_app reviews"""
        return self.review_app_reviews.filter(is_approved=True).count()

    def get_primary_image(self):
        """Return the primary image for this venue"""
        primary_image = self.images.filter(image_order=1).first()
        if primary_image:
            return primary_image.image.url
        return None





class VenueImage(models.Model):
    """Images for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=venue_image_path)
    image_order = models.PositiveSmallIntegerField(default=1, help_text="Order of the image (1 is primary)")
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['image_order']

    def __str__(self):
        return f"{self.venue.name} - Image {self.image_order}"




class OpeningHours(models.Model):
    """Opening hours for venues"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='opening_hours')
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Opening Hours"
        ordering = ['day', 'open_time']
        unique_together = ['venue', 'day']

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()}: Closed"

        # Handle both string and time objects
        try:
            if isinstance(self.open_time, str):
                open_time_parts = self.open_time.split(':')
                open_time_str = f"{open_time_parts[0]}:{open_time_parts[1]}"
            else:
                open_time_str = self.open_time.strftime('%H:%M')

            if isinstance(self.close_time, str):
                close_time_parts = self.close_time.split(':')
                close_time_str = f"{close_time_parts[0]}:{close_time_parts[1]}"
            else:
                close_time_str = self.close_time.strftime('%H:%M')

            return f"{self.get_day_display()}: {open_time_str} - {close_time_str}"
        except Exception:
            # Fallback for any other issues
            return f"{self.get_day_display()}: {self.open_time} - {self.close_time}"



class FAQ(models.Model):
    """Frequently Asked Questions for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order']

    def __str__(self):
        return self.question




class Service(models.Model):
    """Service model for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    short_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        unique_together = ['venue', 'slug']

    def __str__(self):
        return f"{self.title} - {self.venue.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_final_price(self):
        """Return the final price (discounted if available)"""
        if self.discounted_price is not None:
            return self.discounted_price
        return self.price

    def get_discount_percentage(self):
        """Calculate the discount percentage if discounted price is set"""
        if self.discounted_price is not None and self.price > 0:
            discount = ((self.price - self.discounted_price) / self.price) * 100
            return round(discount)
        return 0

    def get_discount_info(self):
        """Return discount information if available"""
        if hasattr(self, 'discount_info') and self.discount_info:
            return self.discount_info
        return None



class Review(models.Model):
    """Review model for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    def clean(self):
        """Validate the review"""
        super().clean()
        # Validate rating range
        if self.rating is not None and (self.rating < 1 or self.rating > 5):
            raise ValidationError({'rating': 'Rating must be between 1 and 5.'})

    class Meta:
        ordering = ['-created_at']
        unique_together = ['venue', 'user']

    def __str__(self):
        return f"{self.user.email} - {self.venue.name} - {self.rating} stars"


class TeamMember(models.Model):
    """Team member model for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to=venue_image_path, blank=True, null=True)
    title = models.CharField(max_length=255, help_text="Job title or designation")
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.title} at {self.venue.name}"


class USCity(models.Model):
    """Model for storing US city data from us_cities.csv"""
    city = models.CharField(max_length=100)
    state_id = models.CharField(max_length=2)  # e.g., NY, CA
    state_name = models.CharField(max_length=100)  # e.g., New York, California
    county_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    zip_codes = models.TextField()  # Stored as space-separated values
    city_id = models.CharField(max_length=20, unique=True)  # Unique identifier from the CSV

    class Meta:
        verbose_name = "US City"
        verbose_name_plural = "US Cities"
        ordering = ['state_name', 'city']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state_name']),
            models.Index(fields=['county_name']),
            models.Index(fields=['state_id']),
        ]

    def __str__(self):
        return f"{self.city}, {self.state_id}"
