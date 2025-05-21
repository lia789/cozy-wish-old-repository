# CozyWish Technical Architecture

## Technology Stack

### Backend
- **Framework**: Django 5.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Python Version**: 3.10+
- **Authentication**: Custom email-based authentication
- **File Storage**: Local storage (development), AWS S3 (production)
- **Caching**: Django's built-in caching system
- **Task Queue**: Django Cron (commented out due to compatibility issues with Django 5.0)

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5
- **Form Styling**: Crispy Forms with Bootstrap 5 template pack
- **JavaScript**: Vanilla JavaScript with minimal dependencies
- **Icons**: Font Awesome
- **Form Widgets**: Django Widget Tweaks

### Development Tools
- **Version Control**: Git with GitHub
- **CI/CD**: GitHub Actions
- **Testing**: pytest with pytest-playwright for E2E testing
- **Code Quality**: flake8, black, isort
- **Documentation**: Markdown
- **Task Runner**: Make

## Project Structure

### Directory Structure

```
cozywish/
├── project_root/           # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── accounts_app/           # User authentication and profiles
├── venues_app/             # Venue and service management
├── booking_cart_app/       # Booking and cart functionality
├── payments_app/           # Payment processing
├── dashboard_app/          # User dashboards
├── review_app/             # Review system
├── discount_app/           # Discount management
├── cms_app/                # Content management
├── notifications_app/      # Notification system
├── admin_app/              # Extended admin functionality
├── utils/                  # Utility functions and services
├── templates/              # HTML templates
├── static/                 # Static files
├── media/                  # User-uploaded files
├── tests/                  # Test configuration
│   └── e2e/                # End-to-end tests
├── requirements.txt        # Python dependencies
├── Makefile                # Make commands
└── manage.py               # Django management script
```

### Database Schema

The database schema is organized around the core entities of the application:

1. **Users and Profiles**: CustomUser, CustomerProfile, ServiceProviderProfile, StaffMember
2. **Venues and Services**: Venue, Service, Category, Tag, OpeningHours, TeamMember, FAQ
3. **Bookings and Payments**: CartItem, Booking, BookingItem, Transaction, Invoice
4. **Reviews**: Review, ReviewResponse, ReviewFlag
5. **Discounts**: VenueDiscount, ServiceDiscount, PlatformDiscount
6. **Content**: Page, BlogPost, MediaItem, Announcement
7. **Notifications**: Notification, UserNotification, NotificationPreference

## Authentication System

### Custom User Model

The application uses a custom user model (`CustomUser`) that replaces Django's default user model:

- Uses email as the primary identifier instead of username
- Includes role flags: `is_customer`, `is_service_provider`, `is_staff`
- Tracks email verification status
- Includes custom user manager for creating users and superusers

### Authentication Flow

1. **Registration**:
   - Separate forms for customers and service providers
   - Email validation and password strength requirements
   - Automatic profile creation on registration
   - Auto-login after successful registration

2. **Login**:
   - Email and password authentication
   - "Remember me" functionality
   - Failed login attempt tracking
   - Prevention of login for deleted accounts

3. **Password Management**:
   - Password reset via email
   - Password change with current password verification
   - Custom password validation

4. **Session Management**:
   - Session expiration based on "Remember me" setting
   - Session security settings (httponly, samesite)

## Security Features

### Authentication Security

- Custom authentication backend that checks for deleted accounts
- Login attempt tracking for security monitoring
- Password strength validation
- CSRF protection on all forms

### Data Security

- Input validation on all forms
- XSS protection through Django's template system
- SQL injection protection through Django's ORM
- HTTPS enforcement in production

### Access Control

- Role-based access control for all views
- Object-level permissions for venue and service management
- Secure file uploads with validation and sanitization

## Core Application Modules

### User Management (accounts_app)

The accounts_app handles all user-related functionality:

- User registration and authentication
- Profile management for customers and service providers
- Staff management for service providers
- Account security and deletion

#### Key Models

- `CustomUser`: Extended user model with email authentication
- `CustomerProfile`: Profile for customers
- `ServiceProviderProfile`: Profile for service providers
- `StaffMember`: Staff members for service providers
- `UserActivity`: Track user activity for security
- `LoginAttempt`: Track login attempts
- `DeletedAccount`: Track deleted accounts to prevent re-registration

### Venue Management (venues_app)

The venues_app handles all venue and service-related functionality:

- Venue creation, editing, and deletion
- Service management
- Opening hours, team members, and FAQs
- Venue search and filtering

#### Key Models

- `Category`: Categories for venues
- `Tag`: Tags for venues
- `Venue`: Main venue model with details and location
- `VenueImage`: Images for venues
- `Service`: Services offered by venues
- `OpeningHours`: Opening hours for venues
- `FAQ`: Frequently asked questions for venues
- `TeamMember`: Team members for venues
- `USCity`: US city data for location services

### Booking System (booking_cart_app)

The booking_cart_app handles the booking process:

- Shopping cart functionality
- Booking creation and management
- Service availability checking
- Booking analytics

#### Key Models

- `CartItem`: Items in a user's cart
- `Booking`: Booking information
- `BookingItem`: Items in a booking
- `ServiceAvailability`: Availability for services

### Payment Processing (payments_app)

The payments_app handles all payment-related functionality:

- Payment processing
- Invoice generation
- Transaction tracking
- Refund processing

#### Key Models

- `PaymentMethod`: User payment methods
- `Transaction`: Payment transactions
- `Invoice`: Invoices for bookings
- `CheckoutSession`: Group related bookings in a checkout session
- `CheckoutSessionBooking`: Link between checkout sessions and bookings

### Dashboard (dashboard_app)

The dashboard_app provides dashboards for different user types:

- Customer dashboard with booking history and account management
- Service provider dashboard with venue management and analytics
- Admin dashboard with system-wide analytics and management

### Review System (review_app)

The review_app handles the review and rating system:

- Customer reviews for venues
- Rating calculation
- Review moderation
- Service provider responses

#### Key Models

- `Review`: Customer reviews for venues
- `ReviewResponse`: Service provider responses to reviews
- `ReviewFlag`: Flag inappropriate reviews

### Discount System (discount_app)

The discount_app handles all discount-related functionality:

- Venue-wide discounts
- Service-specific discounts
- Platform-wide discounts
- Discount usage tracking

#### Key Models

- `VenueDiscount`: Discounts for venues
- `ServiceDiscount`: Discounts for services
- `PlatformDiscount`: Platform-wide discounts
- `DiscountUsage`: Track discount usage

### Content Management (cms_app)

The cms_app provides a content management system:

- Static page management
- Blog functionality
- Media library
- Site configuration

#### Key Models

- `Page`: Static pages
- `BlogCategory`: Categories for blog posts
- `BlogPost`: Blog posts
- `BlogComment`: Comments on blog posts
- `MediaItem`: Media files
- `SiteConfiguration`: Site settings
- `Announcement`: System announcements

### Notification System (notifications_app)

The notifications_app handles the notification system:

- In-app notifications
- Email notifications
- Notification preferences
- System announcements

#### Key Models

- `NotificationCategory`: Categories for notifications
- `Notification`: Notification messages
- `UserNotification`: Link between notifications and users
- `NotificationPreference`: User preferences for notifications

## Testing Strategy

### Unit Tests

Each app includes comprehensive unit tests for:

- Models: Creation, validation, methods
- Forms: Validation, field requirements
- Views: GET and POST requests, context data, permissions
- URLs: URL routing and resolution
- Utilities: Helper functions and services

### Integration Tests

Integration tests cover interactions between apps:

- Authentication and profile creation
- Venue creation and service management
- Booking process and payment
- Review submission and response
- Discount application

### End-to-End Tests

E2E tests using pytest-playwright cover complete user flows:

- User registration and login
- Venue browsing and filtering
- Service booking and checkout
- Review submission and management
- Dashboard functionality

## Deployment Architecture

### Development Environment

- Local development server
- SQLite database
- Local file storage
- Debug mode enabled
- Django Debug Toolbar

### Staging Environment

- AWS EC2 instance
- PostgreSQL database
- AWS S3 for file storage
- Reduced debug information
- Staging-specific settings

### Production Environment

- AWS EC2 instance with load balancing
- PostgreSQL database with read replicas
- AWS S3 for file storage
- Debug mode disabled
- Production-specific settings
- HTTPS enforcement
- Content delivery network (CDN)

## Continuous Integration and Deployment

GitHub Actions workflows for:

- Code quality checks
- Unit and integration tests
- E2E tests
- Deployment to staging
- Deployment to production

## Future Technical Enhancements

1. **Performance Optimization**:
   - Database query optimization
   - Caching strategy implementation
   - Asset minification and bundling

2. **Scalability Improvements**:
   - Microservices architecture for key components
   - Horizontal scaling for web servers
   - Database sharding for large datasets

3. **Advanced Features**:
   - Real-time notifications with WebSockets
   - Elasticsearch integration for improved search
   - Machine learning for personalized recommendations
   - Mobile app API endpoints
   - Multi-language support
   - Advanced analytics and reporting
