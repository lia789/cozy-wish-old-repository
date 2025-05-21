# Review App Tests

This directory contains comprehensive tests for the review_app in the CozyWish platform.

## Test Structure

The tests are organized into the following files:

- `simple_test.py`: A simple test to verify that the test setup works correctly.
- `test_models.py`: Tests for all models in the review_app (Review, ReviewResponse, ReviewFlag).
- `test_forms.py`: Tests for all forms in the review_app (ReviewForm, StarRatingForm, ReviewResponseForm, ReviewFlagForm, AdminReviewForm).
- `test_views.py`: Tests for all views in the review_app, organized by user type (customer, service provider, admin).
- `test_urls.py`: Tests for URL routing in the review_app.
- `test_integration.py`: Integration tests that test complete user flows.

## Running the Tests

### Running All Tests

To run all tests for the review_app, use the following command from the project root:

```bash
python manage.py test review_app
```

### Running Specific Test Files

To run tests from a specific file, use:

```bash
python manage.py test review_app.tests.test_models
python manage.py test review_app.tests.test_forms
python manage.py test review_app.tests.test_views
python manage.py test review_app.tests.test_urls
python manage.py test review_app.tests.test_integration
```

### Running Specific Test Classes or Methods

To run a specific test class:

```bash
python manage.py test review_app.tests.test_models.ReviewModelTest
```

To run a specific test method:

```bash
python manage.py test review_app.tests.test_models.ReviewModelTest.test_review_creation
```

## Test Coverage

The tests cover:

1. **Models**: Creation, validation, methods, and relationships between models.
2. **Forms**: Validation, field requirements, and form processing.
3. **Views**: GET and POST requests, context data, redirects, and permissions.
4. **URLs**: URL routing and resolution.
5. **Integration**: Complete user flows from review submission to admin moderation.

## Adding New Tests

When adding new features to the review_app, please add corresponding tests to maintain test coverage. Follow these guidelines:

1. Place model tests in `test_models.py`
2. Place form tests in `test_forms.py`
3. Place view tests in `test_views.py`
4. Place URL tests in `test_urls.py`
5. Place integration tests in `test_integration.py`

## Test Data

The tests create their own test data as needed. This includes:

- Test users (customers, service providers, admins)
- Test venues and services
- Test bookings
- Test reviews, responses, and flags

## Common Test Patterns

### Testing Models

```python
def test_model_creation(self):
    """Test creating a model instance is successful"""
    # Create an instance
    instance = Model.objects.create(...)
    
    # Check that the instance was created with the correct attributes
    self.assertEqual(instance.attribute, expected_value)
    
    # Test string representation
    self.assertEqual(str(instance), expected_string)
```

### Testing Forms

```python
def test_form_valid(self):
    """Test that the form is valid with valid data"""
    form = Form(data=valid_data)
    self.assertTrue(form.is_valid())

def test_form_invalid(self):
    """Test that the form is invalid with invalid data"""
    form = Form(data=invalid_data)
    self.assertFalse(form.is_valid())
    self.assertIn('field_name', form.errors)
```

### Testing Views

```python
def test_view_get(self):
    """Test the view GET request"""
    # Login if needed
    self.client.login(username='user@example.com', password='password')
    
    # Get the page
    response = self.client.get(url)
    
    # Check response
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'template.html')
    self.assertIn('key', response.context)

def test_view_post(self):
    """Test the view POST request"""
    # Login if needed
    self.client.login(username='user@example.com', password='password')
    
    # Post data
    response = self.client.post(url, data)
    
    # Check response
    self.assertRedirects(response, redirect_url)
    
    # Check that the expected changes were made
    self.assertTrue(Model.objects.filter(...).exists())
```
