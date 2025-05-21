# MANUAL TEST CASES FOR VENUES_APP

## Venue Management Tests

### 1. Create Venue
- **Test ID**: VENUE-001
- **Description**: Verify venue creation with valid data
- **Steps**:
  1. Login as service provider
  2. Navigate to create venue page
  3. Fill in valid venue details
  4. Submit the form
  5. Verify successful venue creation
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Create Venue URL: http://127.0.0.1:8000/venues/provider/create/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Venue Name: Tranquility Spa
  - Category: Spa
  - Venue Type: All Genders
  - State: California
  - County: Los Angeles County
  - City: Los Angeles
  - Street Number: 123
  - Street Name: Wellness Avenue
  - About: A peaceful sanctuary offering premium spa services in the heart of Los Angeles.

### 2. Edit Venue
- **Test ID**: VENUE-002
- **Description**: Verify venue editing functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue list
  3. Select a venue to edit
  4. Update venue details
  5. Verify changes are saved
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Updated Venue Name: Tranquility Wellness Spa
  - Updated About: A peaceful sanctuary offering premium spa and wellness services in the heart of Los Angeles.

### 3. Delete Venue
- **Test ID**: VENUE-003
- **Description**: Verify venue deletion functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue list
  3. Select a venue to delete
  4. Confirm deletion
  5. Verify venue is removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Use venue created in VENUE-001

## Service Management Tests

### 4. Create Service
- **Test ID**: SERVICE-001
- **Description**: Verify service creation with valid data
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Add a new service
  4. Fill in valid service details
  5. Verify successful service creation
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Service Name: Swedish Massage
  - Description: A gentle full body massage that relaxes the muscles and improves circulation.
  - Duration: 60 minutes
  - Price: $85.00
  - Discounted Price: $75.00
  - Service Image: massage.jpg (any small JPG file)

### 5. Edit Service
- **Test ID**: SERVICE-002
- **Description**: Verify service editing functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Select a service to edit
  4. Update service details
  5. Verify changes are saved
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Updated Service Name: Premium Swedish Massage
  - Updated Duration: 75 minutes
  - Updated Price: $95.00
  - Updated Discounted Price: $80.00

### 6. Delete Service
- **Test ID**: SERVICE-003
- **Description**: Verify service deletion functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Select a service to delete
  4. Confirm deletion
  5. Verify service is removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Use service created in SERVICE-001

## Venue Details Management Tests

### 7. Add Opening Hours
- **Test ID**: HOURS-001
- **Description**: Verify adding opening hours functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Add opening hours for different days
  4. Verify hours are saved correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Monday: 9:00 AM - 6:00 PM
  - Tuesday: 9:00 AM - 6:00 PM
  - Wednesday: 9:00 AM - 6:00 PM
  - Thursday: 9:00 AM - 8:00 PM
  - Friday: 9:00 AM - 8:00 PM
  - Saturday: 10:00 AM - 5:00 PM
  - Sunday: Closed

### 8. Add FAQ
- **Test ID**: FAQ-001
- **Description**: Verify adding FAQ functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Add FAQs
  4. Verify FAQs are saved correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Question 1: What should I wear for a massage?
  - Answer 1: Wear comfortable clothing. You'll be provided with appropriate coverings during the massage.
  - Question 2: How early should I arrive for my appointment?
  - Answer 2: Please arrive 15 minutes before your scheduled appointment to complete any necessary paperwork.

### 9. Add Team Member
- **Test ID**: TEAM-001
- **Description**: Verify adding team member functionality
- **Steps**:
  1. Login as service provider
  2. Navigate to venue detail page
  3. Add a team member
  4. Verify team member is added correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Dashboard URL: http://127.0.0.1:8000/dashboard/provider/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Name: Lisa Johnson
  - Role: Massage Therapist
  - Bio: Lisa is a certified massage therapist with over 5 years of experience specializing in Swedish and deep tissue massage.
  - Team Member Image: therapist.jpg (any small JPG file)

## Public Venue Browsing Tests

### 10. Home Page Display
- **Test ID**: PUBLIC-001
- **Description**: Verify home page displays correctly with all sections
- **Steps**:
  1. Navigate to home page
  2. Verify hero section with search form displays correctly
  3. Verify categories section displays correctly
  4. Verify top venues section displays correctly
  5. Verify trending venues section displays correctly
  6. Verify discounted venues section displays correctly
- **Materials**:
  - Home URL: http://127.0.0.1:8000/

### 11. Home Page Search
- **Test ID**: PUBLIC-002
- **Description**: Verify home page search functionality
- **Steps**:
  1. Navigate to home page
  2. Enter search term in the search box
  3. Select category from dropdown (if available)
  4. Select location from dropdown (if available)
  5. Submit search
  6. Verify search results display correctly
- **Materials**:
  - Home URL: http://127.0.0.1:8000/
  - Search Term: Massage
  - Category: Spa
  - Location: Los Angeles, CA

### 12. Category Navigation
- **Test ID**: PUBLIC-003
- **Description**: Verify category navigation from home page
- **Steps**:
  1. Navigate to home page
  2. Click on a category card
  3. Verify redirection to venue listing with correct category filter
- **Materials**:
  - Home URL: http://127.0.0.1:8000/
  - Category: Spa

### 13. Venue Listing Basic Display
- **Test ID**: PUBLIC-004
- **Description**: Verify venue listing page displays correctly
- **Steps**:
  1. Navigate to venue listing page
  2. Verify filter sidebar displays correctly
  3. Verify venue cards display correctly with images, names, ratings, and basic info
  4. Verify pagination controls display correctly
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/

### 14. Venue Filtering by Category
- **Test ID**: PUBLIC-005
- **Description**: Verify venue filtering by category
- **Steps**:
  1. Navigate to venue listing page
  2. Select a category from the filter sidebar
  3. Apply filter
  4. Verify only venues from selected category are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Categories to test: Spa, Massage, Yoga

### 15. Venue Filtering by Venue Type
- **Test ID**: PUBLIC-006
- **Description**: Verify venue filtering by venue type
- **Steps**:
  1. Navigate to venue listing page
  2. Select a venue type from the filter sidebar
  3. Apply filter
  4. Verify only venues of selected type are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Venue Types to test: All Genders, Male Only, Female Only

### 16. Venue Filtering by Tags
- **Test ID**: PUBLIC-007
- **Description**: Verify venue filtering by tags
- **Steps**:
  1. Navigate to venue listing page
  2. Select one or more tags from the filter sidebar
  3. Apply filter
  4. Verify only venues with selected tags are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Tags to test: Luxury, Eco-friendly, Couples

### 17. Venue Filtering by Location
- **Test ID**: PUBLIC-008
- **Description**: Verify venue filtering by location
- **Steps**:
  1. Navigate to venue listing page
  2. Enter city, state, or zip code in location filter
  3. Apply filter
  4. Verify only venues in selected location are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Locations to test:
    - Los Angeles, CA
    - New York, NY
    - 90210 (ZIP code)

### 18. Venue Sorting Options
- **Test ID**: PUBLIC-009
- **Description**: Verify venue sorting functionality
- **Steps**:
  1. Navigate to venue listing page
  2. Select different sorting options
  3. Verify venues are sorted correctly according to selected option
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Sort options to test:
    - Rating: High to Low
    - Rating: Low to High
    - Price: High to Low
    - Price: Low to High
    - Discount: High to Low

### 19. Combined Filtering and Sorting
- **Test ID**: PUBLIC-010
- **Description**: Verify combined filtering and sorting functionality
- **Steps**:
  1. Navigate to venue listing page
  2. Apply multiple filters (category, venue type, tags, location)
  3. Apply sorting
  4. Verify results match all criteria
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Category: Spa
  - Venue Type: All Genders
  - Tags: Luxury
  - Location: Los Angeles, CA
  - Sort by: Rating: High to Low

### 20. Venue Search Functionality
- **Test ID**: PUBLIC-011
- **Description**: Verify venue search functionality
- **Steps**:
  1. Navigate to venue search page
  2. Enter search term
  3. Submit search
  4. Verify search results display venues matching the search term
- **Materials**:
  - Venue Search URL: http://127.0.0.1:8000/venues/search/
  - Search terms to test:
    - Spa
    - Massage
    - Yoga
    - Wellness

### 21. Venue Detail
- **Test ID**: PUBLIC-012
- **Description**: Verify venue detail page displays correctly
- **Steps**:
  1. Navigate to venue detail page
  2. Verify venue information, services, opening hours, team members, and FAQs display correctly
  3. Test service booking functionality
- **Materials**:
  - Use venue created in VENUE-001
  - Venue Detail URL: http://127.0.0.1:8000/venues/tranquility-spa/

### 22. Service Detail
- **Test ID**: PUBLIC-013
- **Description**: Verify service detail page displays correctly
- **Steps**:
  1. Navigate to service detail page
  2. Verify service information displays correctly
  3. Test add to cart functionality
- **Materials**:
  - Use service created in SERVICE-001
  - Service Detail URL: http://127.0.0.1:8000/venues/tranquility-spa/services/swedish-massage/

## Advanced Search and Filter Tests

### 23. Advanced Search Combinations
- **Test ID**: SEARCH-001
- **Description**: Verify advanced search with multiple parameters
- **Steps**:
  1. Navigate to venue search page
  2. Enter search term
  3. Select category
  4. Select location
  5. Submit search
  6. Verify search results match all criteria
- **Materials**:
  - Venue Search URL: http://127.0.0.1:8000/venues/search/
  - Search Term: Relaxation
  - Category: Spa
  - Location: Los Angeles, CA

### 24. Price Range Filtering
- **Test ID**: SEARCH-002
- **Description**: Verify filtering venues by price range
- **Steps**:
  1. Navigate to venue listing page
  2. Set minimum and maximum price in filter
  3. Apply filter
  4. Verify only venues with services in the specified price range are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/
  - Min Price: $50
  - Max Price: $150

### 25. Discounted Services Filter
- **Test ID**: SEARCH-003
- **Description**: Verify filtering venues with discounted services
- **Steps**:
  1. Navigate to venue listing page
  2. Enable "Discounted Services Only" filter
  3. Apply filter
  4. Verify only venues with discounted services are displayed
- **Materials**:
  - Venue List URL: http://127.0.0.1:8000/venues/

### 26. Availability-Based Search
- **Test ID**: SEARCH-004
- **Description**: Verify searching venues by availability
- **Steps**:
  1. Navigate to venue search page
  2. Select date and time for availability search
  3. Submit search
  4. Verify only venues with available services at the specified time are displayed
- **Materials**:
  - Venue Search URL: http://127.0.0.1:8000/venues/search/
  - Date: [Next business day]
  - Time: 2:00 PM

### 27. Search Results Pagination
- **Test ID**: SEARCH-005
- **Description**: Verify pagination of search results
- **Steps**:
  1. Perform a search that returns multiple pages of results
  2. Navigate through pagination controls
  3. Verify correct results are displayed on each page
- **Materials**:
  - Venue Search URL: http://127.0.0.1:8000/venues/search/
  - Search Term: Spa (or any term that returns many results)

## Review Management Tests

### 28. Submit Review
- **Test ID**: REVIEW-001
- **Description**: Verify review submission functionality
- **Steps**:
  1. Login as customer
  2. Navigate to venue detail page
  3. Submit a review
  4. Verify review is displayed correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Use venue created in VENUE-001
  - Rating: 5 stars
  - Review Title: Excellent Experience
  - Review Content: I had an amazing experience at this spa. The staff was friendly and professional, and the massage was perfect.

## Admin Management Tests

### 29. Admin Venue Approval
- **Test ID**: ADMIN-001
- **Description**: Verify admin venue approval functionality
- **Steps**:
  1. Login as admin
  2. Navigate to admin venue list
  3. Review and approve a pending venue
  4. Verify venue status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Admin Venue List URL: http://127.0.0.1:8000/venues/admin/
  - Use venue created in VENUE-001 (if pending) or create a new venue

### 30. Admin Venue Rejection
- **Test ID**: ADMIN-002
- **Description**: Verify admin venue rejection functionality
- **Steps**:
  1. Login as admin
  2. Navigate to admin venue list
  3. Review and reject a pending venue
  4. Provide rejection reason
  5. Verify venue status is updated
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Admin Venue List URL: http://127.0.0.1:8000/venues/admin/
  - Create a new venue for testing rejection

### 31. Admin Venue Detail Review
- **Test ID**: ADMIN-003
- **Description**: Verify admin venue detail review functionality
- **Steps**:
  1. Login as admin
  2. Navigate to admin venue list
  3. Select a venue to review details
  4. Verify all venue information is displayed correctly
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Admin Venue List URL: http://127.0.0.1:8000/venues/admin/
  - Use venue created in VENUE-001

## Integration Tests

### 32. Venue Creation to Approval Flow
- **Test ID**: INTEG-001
- **Description**: Verify complete flow from venue creation to approval
- **Steps**:
  1. Login as service provider
  2. Create a new venue
  3. Add services, opening hours, FAQs, and team members
  4. Login as admin
  5. Review and approve the venue
  6. Login as customer
  7. Search for the venue
  8. View venue details
  9. Book a service
- **Materials**:
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Admin Email: admin@example.com
  - Admin Password: AdminPass123!
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Venue Name: Integration Test Spa
  - Service Name: Test Massage

### 33. Venue Search to Booking Flow
- **Test ID**: INTEG-002
- **Description**: Verify complete flow from venue search to service booking
- **Steps**:
  1. Login as customer
  2. Search for venues by category and location
  3. Filter results by price range
  4. Select a venue
  5. View venue details
  6. Select a service
  7. Add service to cart
  8. Complete booking
- **Materials**:
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Search Category: Spa
  - Search Location: Los Angeles, CA
  - Price Range: $50-$150
