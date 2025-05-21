# CozyWish Features and User Flows

This document outlines the key features and user flows in the CozyWish application, organized by user type and functionality.

## User Types

### Customers

Customers are end-users who browse venues, book services, and leave reviews.

**Key Characteristics:**
- Register with email and password
- Browse and search for venues
- Book services
- Leave reviews
- Manage bookings and payments

### Service Providers

Service providers are businesses that offer venues and services.

**Key Characteristics:**
- Register with business information
- Create and manage venues
- Add services with pricing and availability
- Respond to reviews
- Manage bookings and staff

### Administrators

Administrators manage the platform and ensure quality control.

**Key Characteristics:**
- Approve venues and services
- Manage users and content
- Monitor system health
- Create platform-wide discounts
- Access analytics and reports

## Core Features and User Flows

### 1. Authentication and Account Management

#### Customer Registration

1. User navigates to the customer signup page
2. User enters email, password, and basic profile information
3. System validates input and creates account
4. User is automatically logged in and redirected to the bookings page
5. System sends welcome email

#### Service Provider Registration

1. User navigates to the service provider signup page
2. User enters business name, contact person name, email, phone, and password
3. System validates input and creates account
4. User is automatically logged in and redirected to the provider dashboard
5. System sends welcome email

#### Login Process

1. User navigates to the login page
2. User enters email and password
3. System validates credentials
4. If "Remember me" is checked, session is set to expire after 2 weeks
5. User is redirected based on role:
   - Customers to bookings page
   - Service providers to provider dashboard
   - Admins to admin dashboard

#### Password Reset

1. User clicks "Forgot Password" on login page
2. User enters email address
3. System sends password reset link
4. User clicks link and enters new password
5. System updates password and redirects to login

#### Account Deletion

1. User navigates to account settings
2. User clicks "Delete Account"
3. System displays confirmation dialog
4. User confirms deletion
5. System marks account as deleted and logs user out
6. Email is added to DeletedAccount to prevent re-registration

### 2. Venue Management

#### Venue Creation (Service Provider)

1. Service provider navigates to "Create Venue" page
2. Provider enters venue details:
   - Name
   - Category
   - Location information
   - Description
   - Tags
3. Provider submits the form
4. System creates venue in "pending" status
5. Provider is redirected to venue detail page to add:
   - Images
   - Services
   - Opening hours
   - Team members
   - FAQs

#### Venue Approval (Admin)

1. Admin navigates to pending venues list
2. Admin reviews venue details
3. Admin approves or rejects venue
4. If rejected, admin provides reason
5. System notifies service provider of decision

#### Venue Editing (Service Provider)

1. Provider navigates to venue detail page
2. Provider clicks "Edit" button
3. Provider updates venue information
4. System saves changes
5. If significant changes, venue may require re-approval

#### Venue Deletion (Service Provider)

1. Provider navigates to venue detail page
2. Provider clicks "Delete" button
3. System displays confirmation dialog
4. Provider confirms deletion
5. System marks venue as deleted and removes from public view

### 3. Service Management

#### Service Creation (Service Provider)

1. Provider navigates to venue detail page
2. Provider clicks "Add Service"
3. Provider enters service details:
   - Title
   - Description
   - Price
   - Duration
4. Provider submits the form
5. System creates service and associates with venue

#### Service Availability Management

1. Provider navigates to service detail page
2. Provider clicks "Manage Availability"
3. Provider sets available dates and times
4. Provider sets maximum bookings per time slot
5. System saves availability settings

### 4. Venue Discovery and Search

#### Home Page Browsing

1. User visits the home page
2. User sees:
   - Hero section with search form
   - Featured categories
   - Top-rated venues
   - Trending venues
   - Discounted venues
3. User can click on any venue to view details

#### Search and Filtering

1. User enters search criteria (location, category, etc.)
2. System displays matching venues
3. User can apply additional filters:
   - Price range
   - Rating
   - Tags
   - Venue type
4. System updates results in real-time
5. User can sort results by various criteria

#### Venue Detail View

1. User clicks on a venue from search results
2. User views venue details:
   - Description
   - Images
   - Services
   - Opening hours
   - Team members
   - FAQs
   - Reviews
3. User can click on services to view details or add to cart

### 5. Booking Process

#### Adding to Cart

1. User views service details
2. User selects date, time, and quantity
3. System checks availability
4. User clicks "Add to Cart"
5. System adds item to cart with 24-hour expiration
6. User is redirected to cart or can continue shopping

#### Cart Management

1. User navigates to cart page
2. User views cart items with:
   - Service details
   - Date and time
   - Quantity
   - Price
   - Subtotal
3. User can update quantities or remove items
4. System recalculates total price
5. User clicks "Checkout" to proceed

#### Checkout Process

1. User reviews cart items grouped by venue
2. User enters or selects payment method
3. System validates payment information
4. User confirms order
5. System processes payment and creates bookings
6. User is redirected to confirmation page
7. System sends booking confirmation email

#### Booking Management (Customer)

1. Customer navigates to bookings page
2. Customer views list of bookings with status
3. Customer can click on booking to view details
4. Customer can cancel booking if eligible
5. System updates booking status and notifies service provider

#### Booking Management (Service Provider)

1. Provider navigates to bookings page
2. Provider views list of bookings for their venues
3. Provider can filter by status, date, or venue
4. Provider can update booking status:
   - Confirm
   - Complete
   - Cancel
5. System updates status and notifies customer

### 6. Review System

#### Submitting a Review

1. Customer completes a booking
2. Customer navigates to venue page or booking details
3. Customer clicks "Leave Review"
4. Customer enters rating (1-5 stars) and comment
5. System validates and saves review
6. Review appears on venue page
7. System recalculates venue's average rating

#### Responding to Reviews (Service Provider)

1. Provider navigates to reviews page
2. Provider views all reviews for their venues
3. Provider clicks "Respond" on a review
4. Provider enters response text
5. System saves response and displays it with the review
6. System notifies customer of response

#### Flagging Inappropriate Reviews

1. User views a review they find inappropriate
2. User clicks "Flag Review"
3. User selects reason and provides details
4. System marks review as flagged for admin review
5. Admin reviews flagged review and takes action

### 7. Discount Management

#### Creating Venue Discounts (Service Provider)

1. Provider navigates to discounts page
2. Provider clicks "Create Venue Discount"
3. Provider enters discount details:
   - Name
   - Description
   - Discount type (percentage or fixed amount)
   - Discount value
   - Start and end dates
4. Provider submits the form
5. System creates discount in "pending" status
6. Admin approves or rejects discount

#### Creating Service Discounts (Service Provider)

1. Provider navigates to discounts page
2. Provider clicks "Create Service Discount"
3. Provider selects service and enters discount details
4. Provider submits the form
5. System creates discount in "pending" status
6. Admin approves or rejects discount

#### Creating Platform Discounts (Admin)

1. Admin navigates to discounts page
2. Admin clicks "Create Platform Discount"
3. Admin enters discount details and optionally selects category
4. Admin submits the form
5. System creates active platform discount
6. Discount is applied automatically to eligible bookings

#### Viewing and Using Discounts (Customer)

1. Customer browses venues or services
2. System displays discounted prices when applicable
3. Customer can view all discounts for a venue
4. Discounts are automatically applied during checkout
5. Customer sees discount details on order summary

### 8. Dashboard and Analytics

#### Customer Dashboard

1. Customer navigates to dashboard
2. Customer views:
   - Recent bookings
   - Upcoming bookings
   - Review history
   - Account information
3. Customer can navigate to detailed views for each section

#### Service Provider Dashboard

1. Provider navigates to dashboard
2. Provider views:
   - Venue statistics
   - Today's bookings
   - Recent bookings
   - Revenue summary
   - Recent reviews
3. Provider can navigate to detailed views for each section

#### Admin Dashboard

1. Admin navigates to dashboard
2. Admin views:
   - User statistics
   - Venue statistics
   - Booking statistics
   - Revenue statistics
   - Recent activity
3. Admin can navigate to detailed reports and management tools

### 9. Content Management

#### Static Page Management (Admin)

1. Admin navigates to CMS section
2. Admin creates or edits static pages
3. Admin enters page content with formatting
4. Admin sets SEO metadata
5. Admin publishes page
6. Page becomes available at its URL

#### Blog Management

1. Admin or service provider navigates to blog section
2. User creates new blog post
3. User enters title, content, and selects categories
4. User uploads featured image
5. User sets SEO metadata
6. User publishes post or saves as draft
7. Published posts appear in blog section

### 10. Notification System

#### Notification Types

1. **Booking Notifications**:
   - New booking created
   - Booking status changed
   - Booking cancelled
   
2. **Review Notifications**:
   - New review received
   - Review response received
   
3. **Account Notifications**:
   - Password changed
   - Profile updated
   - Account security alerts
   
4. **System Announcements**:
   - Platform updates
   - Maintenance notifications
   - Special promotions

#### Notification Preferences

1. User navigates to notification settings
2. User sets preferences for each notification category:
   - In-app only
   - Email only
   - Both
   - None
3. System saves preferences and applies to future notifications

## Mobile Responsiveness

All user flows are designed to work seamlessly on mobile devices, with responsive layouts that adapt to different screen sizes.

## Accessibility

The application follows accessibility best practices to ensure usability for all users, including:

1. Proper heading structure
2. Alt text for images
3. ARIA attributes where needed
4. Keyboard navigation support
5. Sufficient color contrast

## Performance Optimization

User flows are optimized for performance through:

1. Efficient database queries
2. Pagination for large result sets
3. Lazy loading of images
4. Caching of frequently accessed data
5. Asynchronous loading of non-critical content
