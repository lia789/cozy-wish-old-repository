# CozyWish Database Models

This document provides a detailed overview of the database models used in the CozyWish application, organized by Django app.

## accounts_app Models

### CustomUser

The core user model that extends Django's AbstractUser:

```python
class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

### CustomerProfile

Profile for customers with personal and contact information:

```python
class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    profile_picture = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### ServiceProviderProfile

Profile for service providers with business information:

```python
class ServiceProviderProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='service_provider_profile')
    business_name = models.CharField(max_length=255)
    contact_person_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    business_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### StaffMember

Staff members for service providers:

```python
class StaffMember(models.Model):
    service_provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staff_members')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to=get_staff_image_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### UserActivity, LoginAttempt, DeletedAccount

Security and tracking models:

```python
class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

class LoginAttempt(models.Model):
    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=False)

class DeletedAccount(models.Model):
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
```

## venues_app Models

### Category and Tag

Categorization models for venues:

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
```

### Venue

The core venue model:

```python
class Venue(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='venues')
    tags = models.ManyToManyField(Tag, blank=True, related_name='venues')
    venue_type = models.CharField(max_length=10, choices=VENUE_TYPE_CHOICES, default='all')
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    us_city = models.ForeignKey('USCity', on_delete=models.SET_NULL, null=True, blank=True, related_name='venues')
    about = models.TextField(help_text="Short venue description")
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### VenueImage

Images for venues:

```python
class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=venue_image_path)
    image_order = models.PositiveSmallIntegerField(default=1)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### Service

Services offered by venues:

```python
class Service(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### OpeningHours, FAQ, TeamMember

Additional venue-related models:

```python
class OpeningHours(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='opening_hours')
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

class FAQ(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

class TeamMember(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to=venue_image_path, blank=True, null=True)
    title = models.CharField(max_length=255, help_text="Job title or designation")
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

## booking_cart_app Models

### CartItem

Items in a user's cart:

```python
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    time_slot = models.TimeField()
    added_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

### Booking and BookingItem

Booking models:

```python
class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    dispute_reason = models.TextField(blank=True)
    last_status_change = models.DateTimeField(auto_now=True)

class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_title = models.CharField(max_length=255)
    service_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    time_slot = models.TimeField()
```

### ServiceAvailability

Availability for services:

```python
class ServiceAvailability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    time_slot = models.TimeField()
    max_bookings = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
```

## payments_app Models

### PaymentMethod

User payment methods:

```python
class PaymentMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    last_four = models.CharField(max_length=4, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Transaction and Invoice

Payment transaction models:

```python
class Transaction(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_method_details = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invoices')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
```

## review_app Models

### Review and ReviewResponse

Review models:

```python
class Review(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='review_app_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_app_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)

class ReviewResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### ReviewFlag

Flag inappropriate reviews:

```python
class ReviewFlag(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flags')
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flagged_reviews')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_flags')
```

## discount_app Models

### Discount Models

Various discount types:

```python
class VenueDiscount(DiscountBase):
    venue = models.ForeignKey('venues_app.Venue', on_delete=models.CASCADE, related_name='discounts')
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)

class ServiceDiscount(DiscountBase):
    service = models.ForeignKey('venues_app.Service', on_delete=models.CASCADE, related_name='discounts')
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)

class PlatformDiscount(DiscountBase):
    category = models.ForeignKey('venues_app.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='platform_discounts')
    min_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
```

## cms_app Models

### Content Models

Content management models:

```python
class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_pages')

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to=get_media_upload_path, blank=True, null=True)
    categories = models.ManyToManyField(BlogCategory, related_name='blog_posts')
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
```

## notifications_app Models

### Notification Models

Notification system models:

```python
class NotificationCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)

class Notification(models.Model):
    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_system_wide = models.BooleanField(default=False)

class UserNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
```

## Model Relationships

### Key Relationships

1. **User to Profiles**: One-to-one relationship between CustomUser and CustomerProfile/ServiceProviderProfile
2. **User to Venues**: One-to-many relationship between CustomUser and Venue
3. **Venue to Services**: One-to-many relationship between Venue and Service
4. **User to Bookings**: One-to-many relationship between CustomUser and Booking
5. **Venue to Bookings**: One-to-many relationship between Venue and Booking
6. **Booking to BookingItems**: One-to-many relationship between Booking and BookingItem
7. **User to Reviews**: One-to-many relationship between CustomUser and Review
8. **Venue to Reviews**: One-to-many relationship between Venue and Review
9. **User to Notifications**: Many-to-many relationship through UserNotification

### Inheritance and Abstract Models

1. **DiscountBase**: Abstract base model for all discount types
2. **ContentBase**: Abstract base model for content types (not shown in examples)

## Database Constraints and Indexes

1. **Unique Constraints**: Email addresses, slugs, booking IDs, transaction IDs
2. **Foreign Key Constraints**: All relationships enforce referential integrity
3. **Indexes**: Created on frequently queried fields for performance
4. **Validation**: Field-level validation through Django's validators
