# CozyWish Project Documentation

## Project Overview

CozyWish is a comprehensive venue booking and management platform that connects customers with service providers. The platform allows service providers to list their venues and services, while customers can browse, book, and review these services. The system includes features for user management, venue management, booking and payment processing, reviews, discounts, and more.

## Project Structure

### Core Django Apps

1. **accounts_app**: Handles user authentication, profiles, and account management
2. **venues_app**: Manages venue listings, services, and related information
3. **booking_cart_app**: Handles the booking process, cart functionality, and booking management
4. **payments_app**: Manages payment processing, invoices, and financial transactions
5. **dashboard_app**: Provides dashboards for customers, service providers, and administrators
6. **review_app**: Handles customer reviews and service provider responses
7. **discount_app**: Manages discounts for venues, services, and platform-wide promotions
8. **cms_app**: Content management system for pages, blog posts, and site configuration
9. **notifications_app**: Handles system notifications and user preferences
10. **admin_app**: Extended admin functionality beyond Django's built-in admin
11. **utils**: Utility functions and services used across the platform

### Project Configuration

- **project_root**: Contains settings, main URL configuration, and WSGI/ASGI configuration
- **templates**: Central directory for all HTML templates
- **static**: Static files (CSS, JavaScript, images)
- **media**: User-uploaded files

## User Types and Authentication

### User Types

1. **Customers**: End-users who book services
2. **Service Providers**: Businesses that offer venues and services
3. **Staff**: Employees of service providers
4. **Administrators**: System administrators with full access

### Authentication Features

- Email-based authentication (no username)
- Custom user model with role-based permissions
- Secure password management with custom validation
- Session management with "Remember me" functionality
- Account deletion with prevention of re-registration
- Activity tracking for security monitoring

## Core Features

### Accounts and Profiles

- **Customer Profiles**: Personal information, contact details, booking history
- **Service Provider Profiles**: Business information, contact details, venue management
- **Staff Management**: Service providers can manage their staff members
- **Profile Management**: Users can update their profiles and account settings

### Venues and Services

- **Venue Management**: Create, edit, and delete venues with detailed information
- **Service Management**: Add, edit, and delete services with pricing and availability
- **Categories and Tags**: Organize venues by categories and tags for better searchability
- **Opening Hours**: Set and manage venue opening hours for each day of the week
- **Team Members**: Add and manage venue team members with profiles
- **FAQs**: Add frequently asked questions for venues
- **Images**: Upload and manage multiple images for venues and services
- **Approval System**: Admin approval for new venues and services

### Booking and Cart

- **Shopping Cart**: Add services to cart with date, time, and quantity selection
- **Cart Management**: Update quantities, remove items, and view cart total
- **Cart Expiration**: Cart items expire after 24 hours
- **Checkout Process**: Multi-venue checkout with grouped services
- **Booking Management**: View, track, and manage bookings
- **Booking Cancellation**: Cancel bookings with reason tracking
- **Service Availability**: Manage and check service availability for specific dates and times

### Payments

- **Payment Processing**: Process payments for bookings
- **Multiple Payment Methods**: Support for various payment methods
- **Invoices**: Generate and manage invoices for bookings
- **Transaction History**: Track payment transactions
- **Refunds**: Process refunds for cancelled bookings

### Reviews and Ratings

- **Review System**: Customers can review venues after completing bookings
- **Rating System**: Rate venues on a scale of 1-5 stars
- **Review Moderation**: Flag inappropriate reviews for admin review
- **Service Provider Responses**: Respond to customer reviews
- **Review Analytics**: View review statistics and insights

### Discounts and Promotions

- **Venue Discounts**: Apply discounts to entire venues
- **Service Discounts**: Apply discounts to specific services
- **Platform Discounts**: Admin-created discounts for categories or all venues
- **Discount Types**: Percentage or fixed amount discounts
- **Discount Approval**: Admin approval for service provider discounts
- **Discount Usage Tracking**: Track discount usage and effectiveness

### Dashboard and Analytics

- **Customer Dashboard**: View bookings, reviews, and account information
- **Service Provider Dashboard**: Manage venues, services, bookings, and view analytics
- **Admin Dashboard**: System-wide analytics, user management, and configuration
- **Booking Analytics**: Track booking trends, revenue, and popular services
- **User Analytics**: Monitor user registration, activity, and engagement
- **System Health Monitoring**: Track system performance and errors

### Content Management

- **Static Pages**: Create and manage static pages with SEO optimization
- **Blog**: Create and publish blog posts with categories and comments
- **Media Library**: Upload and manage media files
- **Announcements**: Create system-wide announcements
- **Site Configuration**: Manage site settings, social media links, and contact information

### Notifications

- **Notification System**: Send notifications to users for various events
- **Notification Categories**: Organize notifications by category
- **Notification Preferences**: Users can set preferences for notification delivery
- **Email Notifications**: Send email notifications for important events
- **In-App Notifications**: Real-time notifications within the application

## Database Models

### accounts_app

- **CustomUser**: Extended user model with email authentication
- **CustomerProfile**: Profile for customers
- **ServiceProviderProfile**: Profile for service providers
- **StaffMember**: Staff members for service providers
- **UserActivity**: Track user activity for security
- **LoginAttempt**: Track login attempts
- **DeletedAccount**: Track deleted accounts to prevent re-registration

### venues_app

- **Category**: Categories for venues
- **Tag**: Tags for venues
- **Venue**: Main venue model with details and location
- **VenueImage**: Images for venues
- **Service**: Services offered by venues
- **OpeningHours**: Opening hours for venues
- **FAQ**: Frequently asked questions for venues
- **TeamMember**: Team members for venues
- **USCity**: US city data for location services

### booking_cart_app

- **CartItem**: Items in a user's cart
- **Booking**: Booking information
- **BookingItem**: Items in a booking
- **ServiceAvailability**: Availability for services

### payments_app

- **PaymentMethod**: User payment methods
- **Transaction**: Payment transactions
- **Invoice**: Invoices for bookings
- **CheckoutSession**: Group related bookings in a checkout session
- **CheckoutSessionBooking**: Link between checkout sessions and bookings

### review_app

- **Review**: Customer reviews for venues
- **ReviewResponse**: Service provider responses to reviews
- **ReviewFlag**: Flag inappropriate reviews

### discount_app

- **VenueDiscount**: Discounts for venues
- **ServiceDiscount**: Discounts for services
- **PlatformDiscount**: Platform-wide discounts
- **DiscountUsage**: Track discount usage

### cms_app

- **Page**: Static pages
- **BlogCategory**: Categories for blog posts
- **BlogPost**: Blog posts
- **BlogComment**: Comments on blog posts
- **MediaItem**: Media files
- **SiteConfiguration**: Site settings
- **Announcement**: System announcements

### notifications_app

- **NotificationCategory**: Categories for notifications
- **Notification**: Notification messages
- **UserNotification**: Link between notifications and users
- **NotificationPreference**: User preferences for notifications

## Development Tools and Utilities

### Make Commands

```bash
# Reset the database completely
make full-reset-db

# Import dummy data for accounts_app
make accounts-app-db-import

# Import dummy data for venues_app
make venues-app-db-import

# Setup complete development environment
make setup-dev-environment
```

### Testing Framework

- **pytest-playwright**: End-to-end testing with video, image, and HTML reports
- **Unit Tests**: Comprehensive unit tests for all apps
- **Integration Tests**: Tests for interactions between apps
- **Test Data**: Dummy data for testing in CSV format

### Deployment

- **GitHub Actions**: CI/CD workflows for automated testing and deployment
- **Staging Environment**: Testing environment before production
- **Production Environment**: Live environment for end users

## URL Structure

- `/`: Home page (venues_app)
- `/accounts/`: User authentication and profile management
- `/venues/`: Venue listings and details
- `/booking/`: Booking and cart functionality
- `/payments/`: Payment processing
- `/dashboard/`: User dashboards
- `/reviews/`: Review system
- `/discounts/`: Discount management
- `/cms/`: Content management
- `/notifications/`: Notification management
- `/super-admin/`: Extended admin functionality

## Next Steps for Development

1. Implement AWS S3 integration for media storage
2. Add payment gateway integration (Stripe, PayPal)
3. Implement Elasticsearch for improved search functionality
4. Add Google/Apple sign-in options
5. Implement real-time notifications with WebSockets
6. Add analytics dashboard with charts and reports
7. Implement multi-language support
8. Add mobile app integration
9. Implement advanced SEO features
10. Add marketing automation tools
