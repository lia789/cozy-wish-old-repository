# COMPREHENSIVE MANUAL TEST PLAN FOR COZYWISH

## Accounts App Tests

### 1. Customer Registration
- **Test ID**: ACC-001
- **Description**: Verify customer registration with valid data
- **Steps**:
  1. Navigate to customer signup page
  2. Fill in valid email and password
  3. Submit the form
  4. Verify successful registration and redirection to bookings page
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/signup/customer/
  - Email: new.customer@example.com
  - Password: SecurePass123!
  - Confirm Password: SecurePass123!

### 2. Service Provider Registration
- **Test ID**: ACC-002
- **Description**: Verify service provider registration with valid data
- **Steps**:
  1. Navigate to service provider signup page
  2. Fill in valid business details and credentials
  3. Submit the form
  4. Verify successful registration and redirection to provider dashboard
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/signup/service-provider/
  - Business Name: Test Wellness Center
  - Email: new.provider@example.com
  - Phone: 555-987-6543
  - Contact Person Name: Jane Smith
  - Password: SecurePass123!
  - Confirm Password: SecurePass123!

### 3. Login Validation
- **Test ID**: ACC-003
- **Description**: Verify login validation for incorrect credentials
- **Steps**:
  1. Navigate to login page
  2. Enter invalid credentials
  3. Verify appropriate error message
  4. Try valid credentials
  5. Verify successful login
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/login/
  - Invalid Email: wrong@example.com
  - Invalid Password: WrongPass123!
  - Valid Email: test.customer@example.com
  - Valid Password: SecurePass123!

### 4. Password Reset Flow
- **Test ID**: ACC-004
- **Description**: Verify complete password reset flow
- **Steps**:
  1. Navigate to login page
  2. Click "Forgot Password"
  3. Enter email address
  4. Check for reset email (check console in development)
  5. Follow reset link
  6. Set new password
  7. Verify login with new password
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Reset URL: http://127.0.0.1:8000/accounts/password/reset/
  - Email: test.customer@example.com
  - New Password: NewSecurePass456!
  - Confirm New Password: NewSecurePass456!

### 5. Account Deletion
- **Test ID**: ACC-005
- **Description**: Verify account deletion functionality
- **Steps**:
  1. Create a temporary account
  2. Login with the account
  3. Navigate to account settings
  4. Request account deletion
  5. Confirm deletion
  6. Verify account is deleted and login is no longer possible
- **Materials**:
  - Signup URL: http://127.0.0.1:8000/accounts/signup/customer/
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Settings URL: http://127.0.0.1:8000/accounts/settings/
  - Email: delete.test@example.com
  - Password: DeleteMe123!

## Venues App Tests

### 6. Venue Creation
- **Test ID**: VEN-001
- **Description**: Verify venue creation with all required fields
- **Steps**:
  1. Login as service provider
  2. Navigate to create venue page
  3. Fill in all required fields
  4. Upload venue images
  5. Submit the form
  6. Verify successful venue creation
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Create Venue URL: http://127.0.0.1:8000/venues/provider/create/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Venue Name: Serenity Wellness Center
  - Category: Wellness
  - Venue Type: All Genders
  - State: New York
  - County: New York County
  - City: New York
  - Street Number: 123
  - Street Name: Wellness Avenue
  - About: A peaceful wellness center offering premium services.

### 7. Venue Editing
- **Test ID**: VEN-002
- **Description**: Verify venue editing functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue management
  3. Select a venue to edit
  4. Update venue details
  5. Submit changes
  6. Verify changes are saved correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Updated Venue Name: Serenity Wellness & Spa Center
  - Updated About: A peaceful wellness center offering premium spa and wellness services.

### 8. Service Creation
- **Test ID**: VEN-003
- **Description**: Verify service creation functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue details
  3. Add a new service
  4. Fill in service details including pricing
  5. Upload service image
  6. Submit the form
  7. Verify service is created successfully
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Service Name: Deep Tissue Massage
  - Description: A therapeutic massage that focuses on realigning deeper layers of muscles.
  - Duration: 60 minutes
  - Price: $95.00
  - Discounted Price: $80.00
  - Service Image: massage.jpg (any small JPG file)

### 9. Opening Hours Management
- **Test ID**: VEN-004
- **Description**: Verify venue opening hours management
- **Steps**:
  1. Login as service provider
  2. Navigate to venue details
  3. Set opening hours for each day of the week
  4. Mark some days as closed
  5. Save changes
  6. Verify opening hours are displayed correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Monday: 9:00 AM - 7:00 PM
  - Tuesday: 9:00 AM - 7:00 PM
  - Wednesday: 9:00 AM - 7:00 PM
  - Thursday: 9:00 AM - 8:00 PM
  - Friday: 9:00 AM - 8:00 PM
  - Saturday: 10:00 AM - 6:00 PM
  - Sunday: Closed

### 10. Team Member Management
- **Test ID**: VEN-005
- **Description**: Verify team member management functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue details
  3. Add team members (up to 5)
  4. Try adding a 6th team member
  5. Verify error message about maximum limit
  6. Edit an existing team member
  7. Delete a team member
  8. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Team Member Name: Michael Johnson
  - Title: Massage Therapist
  - Bio: Certified massage therapist with 7 years of experience.
  - Profile Image: therapist.jpg (any small JPG file)

### 11. FAQ Management
- **Test ID**: VEN-006
- **Description**: Verify FAQ management functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue details
  3. Add FAQs (up to 5)
  4. Try adding a 6th FAQ
  5. Verify error message about maximum limit
  6. Edit an existing FAQ
  7. Delete an FAQ
  8. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Question: What should I wear for my appointment?
  - Answer: Comfortable clothing is recommended. You'll be provided with appropriate coverings during treatments.

### 12. Venue Search and Filtering
- **Test ID**: VEN-007
- **Description**: Verify venue search and filtering functionality
- **Steps**:
  1. Navigate to venue listing page
  2. Test search by keyword
  3. Test filtering by category
  4. Test filtering by location
  5. Test filtering by price range
  6. Test filtering by venue type
  7. Test filtering by tags
  8. Test combined filters
  9. Verify results match criteria
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Search Term: Massage
  - Category: Spa
  - Location: New York, NY
  - Price Range: $50-$150
  - Venue Type: All Genders
  - Tags: Luxury

### 13. Venue Detail View
- **Test ID**: VEN-008
- **Description**: Verify venue detail page displays all information correctly
- **Steps**:
  1. Navigate to a venue detail page
  2. Verify venue information is displayed correctly
  3. Verify services are listed
  4. Verify opening hours are displayed
  5. Verify team members are displayed
  6. Verify FAQs are displayed
  7. Verify reviews are displayed
- **Materials**:
  - Use venue created in VEN-001
  - Venue Detail URL: http://127.0.0.1:8000/venues/serenity-wellness-center/

## Booking and Cart App Tests

### 14. Add Service to Cart
- **Test ID**: BOOK-001
- **Description**: Verify adding a service to cart with date and time selection
- **Steps**:
  1. Login as customer
  2. Navigate to a service detail page
  3. Select date and time
  4. Set quantity
  5. Add to cart
  6. Verify service is added to cart with correct details
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Detail URL: http://127.0.0.1:8000/venues/serenity-wellness-center/services/deep-tissue-massage/
  - Date: [Next business day]
  - Time: 2:00 PM
  - Quantity: 1

### 15. Update Cart Item
- **Test ID**: BOOK-002
- **Description**: Verify updating cart item quantity and recalculating total
- **Steps**:
  1. Login as customer with items in cart
  2. Navigate to cart page
  3. Update quantity of an item
  4. Verify quantity is updated
  5. Verify total price is recalculated correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Updated Quantity: 2

### 16. Remove Cart Item
- **Test ID**: BOOK-003
- **Description**: Verify removing an item from cart
- **Steps**:
  1. Login as customer with items in cart
  2. Navigate to cart page
  3. Remove an item
  4. Verify item is removed
  5. Verify total price is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 17. Cart Expiration
- **Test ID**: BOOK-004
- **Description**: Verify cart items expire after 24 hours
- **Steps**:
  1. Login as customer
  2. Add service to cart
  3. Modify the created_at timestamp in database to be older than 24 hours
  4. Refresh cart page
  5. Verify expired items are removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 18. Checkout Process
- **Test ID**: BOOK-005
- **Description**: Verify checkout process with valid data
- **Steps**:
  1. Login as customer with items in cart
  2. Navigate to checkout
  3. Fill in any additional required information
  4. Submit order
  5. Verify order confirmation
  6. Verify booking is created
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Checkout URL: http://127.0.0.1:8000/booking/checkout/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Notes: Please notify me of any changes to my appointment.

### 19. Multi-Venue Checkout
- **Test ID**: BOOK-006
- **Description**: Verify checkout with services from multiple venues
- **Steps**:
  1. Login as customer
  2. Add services from different venues to cart
  3. Navigate to checkout
  4. Verify services are grouped by venue
  5. Complete checkout
  6. Verify multiple bookings are created
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Checkout URL: http://127.0.0.1:8000/booking/checkout/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service 1: From first venue
  - Service 2: From second venue

### 20. Customer Booking List
- **Test ID**: BOOK-007
- **Description**: Verify customer booking list displays all bookings
- **Steps**:
  1. Login as customer with existing bookings
  2. Navigate to bookings page
  3. Verify all bookings are displayed
  4. Test sorting and filtering options
  5. Verify booking details are correct
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 21. Booking Cancellation
- **Test ID**: BOOK-008
- **Description**: Verify booking cancellation functionality
- **Steps**:
  1. Login as customer with active booking
  2. Navigate to booking detail
  3. Cancel booking
  4. Provide cancellation reason
  5. Verify booking status is updated
  6. Verify cancellation is reflected in provider's view
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Cancellation Reason: Schedule conflict

### 22. Provider Booking Management
- **Test ID**: BOOK-009
- **Description**: Verify service provider booking management
- **Steps**:
  1. Login as service provider
  2. Navigate to bookings management
  3. View list of all bookings for provider's venues
  4. Test sorting and filtering options
  5. View booking details
  6. Update booking status
  7. Verify status change is reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Provider Bookings URL: http://127.0.0.1:8000/booking/provider/bookings/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - New Status: completed

### 23. Service Availability Management
- **Test ID**: BOOK-010
- **Description**: Verify service availability management
- **Steps**:
  1. Login as service provider
  2. Navigate to service availability
  3. Add availability for specific dates and times
  4. Set maximum bookings per slot
  5. Verify availability is saved
  6. Edit existing availability
  7. Delete availability
  8. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Service: Deep Tissue Massage
  - Date: [Next business day]
  - Time Slots: 10:00 AM, 2:00 PM, 4:00 PM
  - Max Bookings: 3

## Payments App Tests

### 24. Payment Processing
- **Test ID**: PAY-001
- **Description**: Verify payment processing for a booking
- **Steps**:
  1. Login as customer
  2. Create a booking through checkout
  3. Process payment with valid payment details
  4. Verify payment confirmation
  5. Verify booking status is updated
  6. Verify transaction record is created
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Payment Method: Credit Card
  - Card Number: 4111 1111 1111 1111 (test card)
  - Expiry Date: 12/25
  - CVV: 123

### 25. Payment Method Management
- **Test ID**: PAY-002
- **Description**: Verify payment method management
- **Steps**:
  1. Login as customer
  2. Navigate to payment methods
  3. Add a new payment method
  4. Set as default
  5. Edit payment method
  6. Delete payment method
  7. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Payment Methods URL: http://127.0.0.1:8000/payments/methods/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Payment Type: Credit Card
  - Name on Card: John Doe
  - Card Number: 4111 1111 1111 1111 (test card)
  - Expiry Date: 12/25

### 26. Payment History
- **Test ID**: PAY-003
- **Description**: Verify payment history display
- **Steps**:
  1. Login as customer with payment history
  2. Navigate to payment history
  3. Verify all transactions are displayed
  4. View transaction details
  5. Verify transaction details are correct
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Payment History URL: http://127.0.0.1:8000/payments/history/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 27. Provider Payment History
- **Test ID**: PAY-004
- **Description**: Verify service provider payment history
- **Steps**:
  1. Login as service provider
  2. Navigate to payment history
  3. Verify all transactions for provider's venues are displayed
  4. View transaction details
  5. Verify transaction details are correct
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Provider Payment History URL: http://127.0.0.1:8000/payments/provider/history/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!

### 28. Invoice Generation
- **Test ID**: PAY-005
- **Description**: Verify invoice generation for bookings
- **Steps**:
  1. Login as customer
  2. Complete a booking with payment
  3. Navigate to booking details
  4. View invoice
  5. Verify invoice details are correct
  6. Download invoice PDF
  7. Verify PDF contains correct information
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/

## Review App Tests

### 29. Submit Review
- **Test ID**: REV-001
- **Description**: Verify review submission functionality
- **Steps**:
  1. Login as customer with completed booking
  2. Navigate to venue page
  3. Submit a review with rating and comments
  4. Verify review is displayed on venue page
  5. Verify rating is reflected in venue's overall rating
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Rating: 4 stars
  - Review Title: Great Experience
  - Review Content: I had a wonderful experience at this venue. The staff was professional and the service was excellent.

### 30. Edit Review
- **Test ID**: REV-002
- **Description**: Verify review editing functionality
- **Steps**:
  1. Login as customer with existing review
  2. Navigate to review history
  3. Edit review
  4. Update rating and comments
  5. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Updated Rating: 5 stars
  - Updated Review Content: After further reflection, I had an exceptional experience. The staff went above and beyond.

### 31. Provider Review Response
- **Test ID**: REV-003
- **Description**: Verify service provider review response functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue reviews
  3. Find a customer review
  4. Submit a response
  5. Verify response is displayed with the review
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Response: Thank you for your feedback! We're glad you enjoyed your experience and look forward to serving you again.

### 32. Flag Inappropriate Review
- **Test ID**: REV-004
- **Description**: Verify flagging inappropriate review functionality
- **Steps**:
  1. Login as customer or service provider
  2. Navigate to a review
  3. Flag review as inappropriate
  4. Provide reason
  5. Verify flag is submitted
  6. Login as admin
  7. Verify flagged review appears in moderation queue
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Flag Reason: Inappropriate language

## Dashboard App Tests

### 33. Customer Dashboard
- **Test ID**: DASH-001
- **Description**: Verify customer dashboard functionality
- **Steps**:
  1. Login as customer
  2. Navigate to dashboard
  3. Verify booking summary is displayed
  4. Verify payment history summary is displayed
  5. Verify review history summary is displayed
  6. Test dashboard widgets and customization
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/customer/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 34. Provider Dashboard
- **Test ID**: DASH-002
- **Description**: Verify service provider dashboard functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to dashboard
  3. Verify venue summary is displayed
  4. Verify booking summary is displayed
  5. Verify revenue summary is displayed
  6. Verify review summary is displayed
  7. Test dashboard widgets and customization
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!

### 35. Dashboard Analytics
- **Test ID**: DASH-003
- **Description**: Verify dashboard analytics functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to analytics section
  3. Test different date ranges
  4. Verify booking analytics are displayed
  5. Verify revenue analytics are displayed
  6. Verify customer analytics are displayed
  7. Test data export functionality
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Analytics URL: http://127.0.0.1:8000/dashboard/provider/analytics/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Date Ranges: Last 7 days, Last 30 days, Last 90 days, Custom range

## CMS App Tests

### 36. Static Page Management
- **Test ID**: CMS-001
- **Description**: Verify static page management functionality
- **Steps**:
  1. Login as admin
  2. Navigate to CMS page management
  3. Create a new page
  4. Edit page content
  5. Publish page
  6. View published page
  7. Verify content is displayed correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - CMS URL: http://127.0.0.1:8000/cms/admin/pages/
  - Page Title: About Us
  - Page Content: Information about CozyWish and its services.

### 37. Blog Management
- **Test ID**: CMS-002
- **Description**: Verify blog management functionality
- **Steps**:
  1. Login as admin
  2. Navigate to blog management
  3. Create a new blog post
  4. Add categories and tags
  5. Upload featured image
  6. Publish blog post
  7. View published post
  8. Verify content is displayed correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - CMS URL: http://127.0.0.1:8000/cms/admin/blog/
  - Post Title: Wellness Tips for Summer
  - Post Content: Article about wellness tips for the summer season.
  - Categories: Wellness, Tips
  - Featured Image: summer.jpg (any small JPG file)

### 38. Media Library
- **Test ID**: CMS-003
- **Description**: Verify media library functionality
- **Steps**:
  1. Login as admin
  2. Navigate to media library
  3. Upload new media files
  4. Edit media metadata
  5. Use media in content
  6. Delete media
  7. Verify changes are reflected
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Media URL: http://127.0.0.1:8000/cms/admin/media/
  - Media Files: Various image files (JPG, PNG)

### 39. Site Configuration
- **Test ID**: CMS-004
- **Description**: Verify site configuration functionality
- **Steps**:
  1. Login as admin
  2. Navigate to site configuration
  3. Update site settings
  4. Update social media links
  5. Update contact information
  6. Save changes
  7. Verify changes are reflected on the site
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Configuration URL: http://127.0.0.1:8000/cms/admin/configuration/
  - Site Name: CozyWish
  - Site Description: A marketplace for spa and wellness services.
  - Contact Email: info@cozywish.com
  - Social Media Links: Facebook, Twitter, Instagram

## Discount App Tests

### 40. Create Venue Discount
- **Test ID**: DISC-001
- **Description**: Verify venue discount creation functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to discounts management
  3. Create a new venue discount
  4. Set discount percentage and validity period
  5. Save discount
  6. Verify discount is applied to venue
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Discounts URL: http://127.0.0.1:8000/discounts/provider/
  - Discount Name: Summer Special
  - Discount Percentage: 15%
  - Valid From: [Current date]
  - Valid To: [Current date + 30 days]

### 41. Create Service Discount
- **Test ID**: DISC-002
- **Description**: Verify service discount creation functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to discounts management
  3. Create a new service discount
  4. Set discount amount and validity period
  5. Save discount
  6. Verify discount is applied to service
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Discounts URL: http://127.0.0.1:8000/discounts/provider/
  - Service: Deep Tissue Massage
  - Discount Amount: $20
  - Valid From: [Current date]
  - Valid To: [Current date + 14 days]

### 42. Platform Discount Management
- **Test ID**: DISC-003
- **Description**: Verify platform-wide discount management
- **Steps**:
  1. Login as admin
  2. Navigate to platform discounts
  3. Create a new platform discount
  4. Set discount code, amount, and validity
  5. Save discount
  6. Test discount code during checkout
  7. Verify discount is applied correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Platform Discounts URL: http://127.0.0.1:8000/discounts/admin/
  - Discount Code: WELCOME20
  - Discount Amount: 20%
  - Valid From: [Current date]
  - Valid To: [Current date + 60 days]

## Notifications App Tests

### 43. Notification Generation
- **Test ID**: NOTIF-001
- **Description**: Verify notification generation for key events
- **Steps**:
  1. Login as customer
  2. Create a booking
  3. Verify booking confirmation notification is generated
  4. Cancel a booking
  5. Verify cancellation notification is generated
  6. Login as service provider
  7. Verify new booking notification is received
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Notifications URL: http://127.0.0.1:8000/notifications/

### 44. Notification Preferences
- **Test ID**: NOTIF-002
- **Description**: Verify notification preferences management
- **Steps**:
  1. Login as customer
  2. Navigate to notification preferences
  3. Update email notification settings
  4. Update in-app notification settings
  5. Save preferences
  6. Verify preferences are applied correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Preferences URL: http://127.0.0.1:8000/notifications/preferences/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 45. System Announcements
- **Test ID**: NOTIF-003
- **Description**: Verify system announcements functionality
- **Steps**:
  1. Login as admin
  2. Create a system announcement
  3. Set announcement visibility and duration
  4. Publish announcement
  5. Login as customer and service provider
  6. Verify announcement is displayed to appropriate users
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Announcements URL: http://127.0.0.1:8000/notifications/admin/announcements/
  - Announcement Title: System Maintenance
  - Announcement Content: The system will be undergoing maintenance on [date]. Please plan accordingly.
  - Visibility: All Users
  - Duration: 7 days

## Admin App Tests

### 46. User Management
- **Test ID**: ADMIN-001
- **Description**: Verify admin user management functionality
- **Steps**:
  1. Login as admin
  2. Navigate to user management
  3. View user list
  4. Filter users by type
  5. Edit user details
  6. Disable/enable user accounts
  7. Verify changes are applied
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - User Management URL: http://127.0.0.1:8000/super-admin/users/

### 47. Venue Approval Workflow
- **Test ID**: ADMIN-002
- **Description**: Verify venue approval workflow
- **Steps**:
  1. Login as service provider
  2. Create a new venue
  3. Logout and login as admin
  4. Navigate to venue approval queue
  5. Review venue details
  6. Approve venue
  7. Verify venue is now visible to customers
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Venue Approval URL: http://127.0.0.1:8000/super-admin/venues/approval/

### 48. System Configuration
- **Test ID**: ADMIN-003
- **Description**: Verify system configuration management
- **Steps**:
  1. Login as admin
  2. Navigate to system configuration
  3. Update system settings
  4. Save changes
  5. Verify changes are applied system-wide
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - System Config URL: http://127.0.0.1:8000/super-admin/system/config/
  - Settings to test: Maintenance Mode, Registration Enabled, Session Timeout

### 49. Admin Dashboard
- **Test ID**: ADMIN-004
- **Description**: Verify admin dashboard functionality
- **Steps**:
  1. Login as admin
  2. Navigate to admin dashboard
  3. Verify key metrics are displayed
  4. Test different date ranges
  5. Verify data visualization components
  6. Test dashboard customization
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Admin Dashboard URL: http://127.0.0.1:8000/super-admin/dashboard/

### 50. Security Event Monitoring
- **Test ID**: ADMIN-005
- **Description**: Verify security event monitoring functionality
- **Steps**:
  1. Login as admin
  2. Navigate to security events
  3. View security event log
  4. Filter events by type and severity
  5. View event details
  6. Mark events as resolved
  7. Verify event status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Security Events URL: http://127.0.0.1:8000/super-admin/security/events/

## Integration Tests

### 51. End-to-End Booking Flow
- **Test ID**: INTEG-001
- **Description**: Verify complete end-to-end booking flow
- **Steps**:
  1. Login as customer
  2. Search for venues by category
  3. Filter results by location and price
  4. Select a venue
  5. View venue details
  6. Select a service
  7. Add service to cart
  8. Proceed to checkout
  9. Complete payment
  10. Verify booking confirmation
  11. Check booking in customer dashboard
  12. Login as service provider
  13. Verify booking appears in provider dashboard
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Category: Spa
  - Location: New York, NY
  - Price Range: $50-$150

### 52. Cross-Module Integration
- **Test ID**: INTEG-002
- **Description**: Verify integration between different modules
- **Steps**:
  1. Login as service provider
  2. Create a venue
  3. Add services with discounts
  4. Login as customer
  5. Book a discounted service
  6. Complete payment
  7. Submit a review
  8. Login as service provider
  9. Respond to review
  10. Check analytics for booking and revenue
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!

### 53. Third-Party Integration
- **Test ID**: INTEG-003
- **Description**: Verify integration with third-party services
- **Steps**:
  1. Test image upload to storage service
  2. Test email notification delivery
  3. Test payment processing integration
  4. Test map/location services integration
  5. Verify all integrations function correctly
- **Materials**:
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Test image files
  - Test email address
  - Test payment card: 4111 1111 1111 1111

## Performance and Security Tests

### 54. Load Testing
- **Test ID**: PERF-001
- **Description**: Verify system performance under load
- **Steps**:
  1. Simulate multiple concurrent users
  2. Test venue search and filtering
  3. Test booking creation
  4. Test checkout process
  5. Monitor response times
  6. Verify system stability under load
- **Materials**:
  - Load testing tool (e.g., JMeter, Locust)
  - Test scenarios for different user types
  - Performance metrics baseline

### 55. Security Testing
- **Test ID**: SEC-001
- **Description**: Verify system security measures
- **Steps**:
  1. Test authentication mechanisms
  2. Test authorization controls
  3. Test input validation
  4. Test protection against common vulnerabilities (XSS, CSRF, SQL Injection)
  5. Test session management
  6. Verify security headers and configurations
- **Materials**:
  - Security testing tools
  - Test accounts with different permission levels
  - List of common security vulnerabilities to test
