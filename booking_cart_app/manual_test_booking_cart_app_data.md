# MANUAL TEST CASES FOR BOOKING_CART_APP

## Cart Management Tests

### 1. Add Service to Cart
- **Test ID**: CART-001
- **Description**: Verify adding a service to cart with valid data
- **Steps**:
  1. Login as customer
  2. Navigate to a service detail page
  3. Select date and time slot
  4. Set quantity
  5. Add to cart
  6. Verify service is added to cart
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Detail URL: http://127.0.0.1:8000/venues/tranquility-spa/services/swedish-massage/
  - Date: [Next business day]
  - Time Slot: 2:00 PM
  - Quantity: 1

### 2. Update Cart Item
- **Test ID**: CART-002
- **Description**: Verify updating cart item quantity
- **Steps**:
  1. Login as customer
  2. Navigate to cart
  3. Update quantity of a cart item
  4. Verify quantity and total price are updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Updated Quantity: 2

### 3. Remove from Cart
- **Test ID**: CART-003
- **Description**: Verify removing an item from cart
- **Steps**:
  1. Login as customer
  2. Navigate to cart
  3. Remove an item from cart
  4. Verify item is removed and total price is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 4. Cart Expiration
- **Test ID**: CART-004
- **Description**: Verify cart items expire after 24 hours
- **Steps**:
  1. Login as customer
  2. Add service to cart
  3. Wait for 24 hours (or modify expiration time in database for testing)
  4. Refresh cart page
  5. Verify expired items are removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

## Checkout Process Tests

### 5. Checkout Process
- **Test ID**: CHECKOUT-001
- **Description**: Verify checkout process with valid data
- **Steps**:
  1. Login as customer
  2. Add service to cart
  3. Navigate to checkout
  4. Fill in checkout form
  5. Submit order
  6. Verify redirection to payment page
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Cart URL: http://127.0.0.1:8000/booking/cart/
  - Checkout URL: http://127.0.0.1:8000/booking/checkout/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Notes: Please prepare for a relaxing experience.

### 6. Multi-Venue Checkout
- **Test ID**: CHECKOUT-002
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
  - Service 1: Swedish Massage at Tranquility Spa
  - Service 2: Yoga Class at Wellness Center

### 7. Empty Cart Checkout
- **Test ID**: CHECKOUT-003
- **Description**: Verify checkout with empty cart
- **Steps**:
  1. Login as customer
  2. Navigate to checkout with empty cart
  3. Verify appropriate error message
  4. Verify redirection to cart page
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Checkout URL: http://127.0.0.1:8000/booking/checkout/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

## Booking Management Tests

### 8. Booking List
- **Test ID**: BOOKING-001
- **Description**: Verify customer booking list display
- **Steps**:
  1. Login as customer
  2. Navigate to bookings page
  3. Verify all bookings are displayed with correct information
  4. Verify sorting and filtering options work correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!

### 9. Booking Detail
- **Test ID**: BOOKING-002
- **Description**: Verify booking detail display
- **Steps**:
  1. Login as customer
  2. Navigate to booking detail page
  3. Verify booking information is displayed correctly
  4. Verify all booking items are listed with correct details
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Use booking created in CHECKOUT-001

### 10. Cancel Booking
- **Test ID**: BOOKING-003
- **Description**: Verify booking cancellation functionality
- **Steps**:
  1. Login as customer
  2. Navigate to booking detail page
  3. Cancel booking
  4. Provide cancellation reason
  5. Verify booking status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Bookings URL: http://127.0.0.1:8000/booking/bookings/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Cancellation Reason: Schedule conflict
  - Use booking created in CHECKOUT-001

## Service Provider Booking Management Tests

### 11. Provider Booking List
- **Test ID**: PROVIDER-001
- **Description**: Verify service provider booking list display
- **Steps**:
  1. Login as service provider
  2. Navigate to provider bookings page
  3. Verify all bookings for provider's venues are displayed
  4. Verify sorting and filtering options work correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Provider Bookings URL: http://127.0.0.1:8000/booking/provider/bookings/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!

### 12. Provider Booking Detail
- **Test ID**: PROVIDER-002
- **Description**: Verify service provider booking detail display
- **Steps**:
  1. Login as service provider
  2. Navigate to provider booking detail page
  3. Verify booking information is displayed correctly
  4. Verify all booking items are listed with correct details
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Provider Bookings URL: http://127.0.0.1:8000/booking/provider/bookings/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Use booking created in CHECKOUT-001

### 13. Update Booking Status
- **Test ID**: PROVIDER-003
- **Description**: Verify updating booking status functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to provider booking detail page
  3. Update booking status
  4. Verify status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Provider Bookings URL: http://127.0.0.1:8000/booking/provider/bookings/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - New Status: completed
  - Use booking created in CHECKOUT-001

## Service Availability Management Tests

### 14. Add Service Availability
- **Test ID**: AVAILABILITY-001
- **Description**: Verify adding service availability
- **Steps**:
  1. Login as service provider
  2. Navigate to service availability page
  3. Add availability for a specific date and time
  4. Verify availability is added
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Service: Swedish Massage
  - Date: [Next business day]
  - Time Slot: 2:00 PM
  - Max Bookings: 3

### 15. Bulk Service Availability
- **Test ID**: AVAILABILITY-002
- **Description**: Verify adding bulk service availability
- **Steps**:
  1. Login as service provider
  2. Navigate to bulk service availability page
  3. Add availability for a date range
  4. Verify availabilities are added for all dates in range
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Service: Swedish Massage
  - Start Date: [Next Monday]
  - End Date: [Next Friday]
  - Time Slots: 10:00 AM, 2:00 PM, 4:00 PM
  - Max Bookings: 3

### 16. Delete Service Availability
- **Test ID**: AVAILABILITY-003
- **Description**: Verify deleting service availability
- **Steps**:
  1. Login as service provider
  2. Navigate to service availability page
  3. Delete an availability
  4. Verify availability is removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Use availability created in AVAILABILITY-001

## Admin Booking Management Tests

### 17. Admin Booking List
- **Test ID**: ADMIN-001
- **Description**: Verify admin booking list display
- **Steps**:
  1. Login as admin
  2. Navigate to admin bookings page
  3. Verify all bookings are displayed
  4. Verify sorting and filtering options work correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Bookings URL: http://127.0.0.1:8000/booking/admin/bookings/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!

### 18. Admin Booking Detail
- **Test ID**: ADMIN-002
- **Description**: Verify admin booking detail display
- **Steps**:
  1. Login as admin
  2. Navigate to admin booking detail page
  3. Verify booking information is displayed correctly
  4. Verify all booking items are listed with correct details
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Bookings URL: http://127.0.0.1:8000/booking/admin/bookings/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Use booking created in CHECKOUT-001

### 19. Admin Update Booking Status
- **Test ID**: ADMIN-003
- **Description**: Verify admin updating booking status functionality
- **Steps**:
  1. Login as admin
  2. Navigate to admin booking detail page
  3. Update booking status
  4. Verify status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Bookings URL: http://127.0.0.1:8000/booking/admin/bookings/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - New Status: refunded
  - Use booking created in CHECKOUT-001

### 20. Booking Analytics
- **Test ID**: ADMIN-004
- **Description**: Verify booking analytics display
- **Steps**:
  1. Login as admin
  2. Navigate to booking analytics page
  3. Verify analytics data is displayed correctly
  4. Test different date range filters
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Analytics URL: http://127.0.0.1:8000/booking/admin/bookings/analytics/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Date Ranges: Last 7 days, Last 30 days, Last 90 days, Custom range
