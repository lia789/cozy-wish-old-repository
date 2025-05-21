# Booking Cart App Tests

This directory contains comprehensive tests for the `booking_cart_app`. The tests are organized into different files based on the components they test.

## Test Files

- `simple_test.py`: A simple test to verify that the test setup is working correctly.
- `test_models.py`: Tests for the models in the booking_cart_app.
- `test_forms.py`: Tests for the forms in the booking_cart_app.
- `test_views.py`: Tests for the views in the booking_cart_app.
- `test_utils.py`: Tests for the utility functions in the booking_cart_app.
- `test_urls.py`: Tests for the URL patterns in the booking_cart_app.
- `test_admin.py`: Tests for the admin configuration in the booking_cart_app.
- `test_signals.py`: Tests for the signals in the booking_cart_app.
- `test_management_commands.py`: Tests for the management commands in the booking_cart_app.
- `test_middleware.py`: Tests for the middleware in the booking_cart_app.
- `test_context_processors.py`: Tests for the context processors in the booking_cart_app.
- `test_templatetags.py`: Tests for the template tags in the booking_cart_app.
- `test_permissions.py`: Tests for the permissions in the booking_cart_app.
- `test_integration.py`: Tests for the integration between different components of the booking_cart_app.
- `test_manual_test_checklist.py`: Generates a manual test checklist for the booking_cart_app.

## Running the Tests

You can run all the tests for the booking_cart_app using the following command:

```bash
python manage.py test booking_cart_app
```

To run a specific test file, use:

```bash
python manage.py test booking_cart_app.tests.test_models
```

To run a specific test class, use:

```bash
python manage.py test booking_cart_app.tests.test_models.CartItemModelTest
```

To run a specific test method, use:

```bash
python manage.py test booking_cart_app.tests.test_models.CartItemModelTest.test_cart_item_creation
```

## Manual Testing Resources

### Generating the Manual Test Checklist

To generate the manual test checklist, run:

```bash
python manage.py test booking_cart_app.tests.test_manual_test_checklist
```

This will create a CSV file at `booking_cart_app_manual_test_dummy_data/booking_cart_app_manual_test_checklist.csv` with a list of manual test cases for the booking_cart_app.

### Dummy Test Data

Dummy data for manual testing is available in the `booking_cart_app_manual_test_dummy_data` directory. This includes:

- `cart_items.csv`: 15 cart items for different customers
- `bookings.csv`: 20 bookings with different statuses
- `booking_items.csv`: 30 booking items linked to the bookings
- `service_availability.csv`: 50 availability records for different services

To import this dummy data, use the provided management command:

```bash
python manage.py import_booking_cart_dummy_data
```

Or use the Makefile target:

```bash
make import-booking-cart-data
```

### Playwright Tests

Automated UI tests using Playwright are available in the `playwright-directory/booking_cart_app_playwright_test.py` script. These tests automate the manual testing checklist and provide screenshots for visual verification.

To run the Playwright tests:

```bash
cd playwright-directory
python booking_cart_app_playwright_test.py
```

## Test Coverage

To check the test coverage, you can use the `coverage` tool:

```bash
coverage run --source='booking_cart_app' manage.py test booking_cart_app
coverage report
```

This will show you the percentage of code that is covered by the tests.

## Continuous Integration

These tests are designed to be run in a continuous integration environment. They should be run automatically whenever changes are made to the codebase to ensure that the booking_cart_app continues to function correctly.
