# CozyWish Testing Strategy

This document outlines the comprehensive testing strategy for the CozyWish application, covering unit tests, integration tests, end-to-end tests, and manual testing procedures.

## Testing Framework

### Core Testing Technologies

- **pytest**: Primary testing framework
- **pytest-playwright**: End-to-end testing with browser automation
- **Django's TestCase**: For model and view testing
- **Coverage.py**: For measuring test coverage

### Test Directory Structure

```
cozywish/
├── accounts_app/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_forms.py
│   │   ├── test_views.py
│   │   ├── test_urls.py
│   │   ├── test_backends.py
│   │   └── test_integration.py
├── venues_app/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_forms.py
│   │   ├── test_views.py
│   │   ├── test_urls.py
│   │   └── test_integration.py
├── ... (similar structure for other apps)
├── tests/
│   ├── e2e/
│   │   ├── test_auth/
│   │   │   ├── TEST_AUTH_001.py
│   │   │   ├── TEST_AUTH_002.py
│   │   │   └── ...
│   │   ├── test_venues/
│   │   ├── test_booking/
│   │   └── ...
│   ├── conftest.py
│   └── pytest.ini
```

## Unit Testing

### Model Tests

Model tests verify the behavior of database models, including:

1. **Creation**: Test that models can be created with valid data
2. **Validation**: Test that validation rules are enforced
3. **Methods**: Test custom model methods
4. **Relationships**: Test relationships between models
5. **Constraints**: Test unique constraints and other database rules

Example model test:

```python
def test_venue_creation(self):
    """Test that a venue can be created with valid data."""
    venue = Venue.objects.create(
        owner=self.user,
        name="Test Venue",
        category=self.category,
        venue_type="all",
        state="New York",
        county="New York County",
        city="New York",
        street_number="123",
        street_name="Main St",
        about="A test venue.",
        approval_status="approved"
    )
    self.assertEqual(venue.name, "Test Venue")
    self.assertEqual(venue.owner, self.user)
    self.assertEqual(venue.approval_status, "approved")
```

### Form Tests

Form tests verify the behavior of forms, including:

1. **Validation**: Test that forms validate input correctly
2. **Error Messages**: Test that appropriate error messages are displayed
3. **Initial Values**: Test that forms are initialized with correct values
4. **Saving**: Test that forms save data correctly

Example form test:

```python
def test_customer_signup_form_valid(self):
    """Test that the customer signup form validates correctly."""
    form_data = {
        'email': 'test@example.com',
        'password1': 'securepassword123',
        'password2': 'securepassword123',
    }
    form = CustomerSignUpForm(data=form_data)
    self.assertTrue(form.is_valid())
```

### View Tests

View tests verify the behavior of views, including:

1. **GET Requests**: Test that views render correctly
2. **POST Requests**: Test that views process form submissions correctly
3. **Authentication**: Test that views enforce authentication requirements
4. **Permissions**: Test that views enforce permission requirements
5. **Context Data**: Test that views provide correct context data to templates
6. **Redirects**: Test that views redirect correctly

Example view test:

```python
def test_venue_detail_view(self):
    """Test that the venue detail view displays correctly."""
    url = reverse('venues_app:venue_detail', args=[self.venue.slug])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.venue.name)
    self.assertContains(response, self.venue.about)
    self.assertTemplateUsed(response, 'venues_app/venue_detail.html')
```

### URL Tests

URL tests verify the routing configuration, including:

1. **URL Resolution**: Test that URLs resolve to the correct views
2. **URL Reversing**: Test that URL names can be reversed to the correct paths
3. **URL Parameters**: Test that URL parameters are handled correctly

Example URL test:

```python
def test_venue_detail_url(self):
    """Test that the venue detail URL resolves correctly."""
    url = reverse('venues_app:venue_detail', args=['test-venue'])
    self.assertEqual(url, '/venues/test-venue/')
    resolver = resolve(url)
    self.assertEqual(resolver.func, venue_detail_view)
```

## Integration Testing

Integration tests verify the interaction between different components of the application, including:

1. **Cross-App Functionality**: Test interactions between different apps
2. **Database Transactions**: Test complex database operations
3. **Signal Handling**: Test that signals are processed correctly
4. **Middleware**: Test that middleware functions correctly

Example integration test:

```python
def test_booking_creation_from_cart(self):
    """Test that a booking can be created from cart items."""
    # Add items to cart
    self.client.login(email='customer@example.com', password='testpass123')
    service = Service.objects.get(title='Test Service')
    cart_data = {
        'service': service.id,
        'quantity': 1,
        'date': '2023-06-01',
        'time_slot': '10:00:00',
    }
    self.client.post(reverse('booking_cart_app:add_to_cart', args=[service.id]), cart_data)
    
    # Process checkout
    checkout_data = {
        'payment_method': 'credit_card',
        'card_number': '4111111111111111',
        'expiry_date': '12/25',
        'cvv': '123',
    }
    response = self.client.post(reverse('booking_cart_app:checkout'), checkout_data)
    
    # Verify booking was created
    self.assertEqual(response.status_code, 302)
    booking = Booking.objects.filter(user__email='customer@example.com').first()
    self.assertIsNotNone(booking)
    self.assertEqual(booking.status, 'pending')
    self.assertEqual(booking.items.count(), 1)
```

## End-to-End Testing

End-to-end tests verify complete user flows using browser automation with pytest-playwright.

### E2E Test Organization

E2E tests are organized by feature area with ID-based filenames:

- `TEST_AUTH_001.py`: Login flows for different user types
- `TEST_AUTH_002.py`: Registration flows
- `TEST_AUTH_003.py`: Password reset flows
- `TEST_VENUES_001.py`: Venue browsing and filtering
- `TEST_BOOKING_001.py`: Booking process

### E2E Test Configuration

```python
# conftest.py
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 720})
    yield page
    page.close()

@pytest.fixture
def authenticated_customer(page):
    # Login as customer
    page.goto("http://127.0.0.1:8000/accounts/login/")
    page.fill("input[name='username']", "customer@example.com")
    page.fill("input[name='password']", "testpass123")
    page.click("button[type='submit']")
    expect(page).to_have_url("http://127.0.0.1:8000/booking/bookings/")
    return page
```

### Example E2E Test

```python
# TEST_AUTH_001.py
import pytest
from playwright.sync_api import expect

def test_customer_login(page):
    """Test that a customer can log in successfully."""
    # Navigate to login page
    page.goto("http://127.0.0.1:8000/accounts/login/")
    
    # Fill in login form
    page.fill("input[name='username']", "customer@example.com")
    page.fill("input[name='password']", "testpass123")
    
    # Take screenshot before submission
    page.screenshot(path="test_results/TEST_AUTH_001/before_login.png")
    
    # Submit form
    page.click("button[type='submit']")
    
    # Verify redirect to bookings page
    expect(page).to_have_url("http://127.0.0.1:8000/booking/bookings/")
    
    # Take screenshot after successful login
    page.screenshot(path="test_results/TEST_AUTH_001/after_login.png")
    
    # Verify user is logged in
    expect(page.locator(".user-menu")).to_contain_text("customer@example.com")
```

### E2E Test Reporting

E2E tests generate comprehensive reports:

1. **HTML Reports**: Individual HTML reports for each test
2. **Screenshots**: Before, after, and at key points in the test
3. **Videos**: Video recordings of test execution
4. **Console Logs**: Browser console logs for debugging

Reports are stored in a structured directory:

```
test_results/
├── TEST_AUTH_001_test_customer_login/
│   ├── report.html
│   ├── before_login.png
│   ├── after_login.png
│   └── video.webm
├── TEST_AUTH_002_test_service_provider_login/
│   ├── ...
```

## Manual Testing

In addition to automated tests, manual testing procedures are documented for complex scenarios.

### Manual Test Plans

Manual test plans are organized by feature area:

1. **Authentication**: Login, registration, password management
2. **Venue Management**: Creation, editing, approval workflow
3. **Booking Process**: Cart, checkout, payment processing
4. **Review System**: Submission, moderation, responses
5. **Dashboard**: Analytics, reporting, management tools

### Example Manual Test Case

```
Test ID: MT-BOOKING-001
Title: Complete Booking Process
Description: Verify that a customer can browse venues, add services to cart, and complete checkout.

Prerequisites:
- Active customer account
- At least one approved venue with services
- Test payment method configured

Steps:
1. Log in as customer
2. Navigate to venue listing page
3. Select a venue and view details
4. Select a service and click "Book Now"
5. Choose date, time, and quantity
6. Click "Add to Cart"
7. Navigate to cart page
8. Verify service details and price
9. Click "Checkout"
10. Enter payment information
11. Confirm order
12. Verify booking confirmation page

Expected Results:
- Service is added to cart successfully
- Cart displays correct service details and price
- Checkout process completes without errors
- Booking is created with "pending" status
- Confirmation page displays booking details
- Confirmation email is sent to customer
```

## Test Data Management

### Dummy Data

Dummy data for testing is provided in CSV format:

1. **accounts_app_manual_test_dummy_data**: User accounts and profiles
2. **venues_app_manual_test_dummy_data**: Venues, services, categories
3. **review_app_manual_test_dummy_data**: Reviews and responses

### Data Import Commands

Make commands are provided for importing test data:

```bash
# Import accounts data
make accounts-app-db-import

# Import venues data
make venues-app-db-import

# Setup complete test environment
make setup-dev-environment
```

## Test Execution

### Running Unit and Integration Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test venues_app

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

### Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e

# Run specific E2E test
pytest tests/e2e/test_auth/TEST_AUTH_001.py

# Run E2E tests in parallel
pytest tests/e2e -n 3

# Run E2E tests with video recording
pytest tests/e2e --video=on
```

## Continuous Integration

Tests are integrated into the CI/CD pipeline using GitHub Actions:

1. **Pull Request Checks**: Run unit and integration tests
2. **Nightly Builds**: Run full test suite including E2E tests
3. **Deployment Checks**: Run smoke tests after deployment

Example GitHub Actions workflow:

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run unit and integration tests
      run: |
        python manage.py test
        
    - name: Run E2E tests
      run: |
        pytest tests/e2e
```

## Test Coverage Goals

The project aims for the following test coverage:

1. **Models**: 95% coverage
2. **Forms**: 90% coverage
3. **Views**: 85% coverage
4. **URLs**: 100% coverage
5. **Utilities**: 90% coverage
6. **Overall**: 85% minimum coverage

## Conclusion

This comprehensive testing strategy ensures that the CozyWish application is thoroughly tested at all levels, from individual components to complete user flows. By combining automated unit, integration, and end-to-end tests with manual testing procedures, we can maintain high quality and reliability throughout the development process.
