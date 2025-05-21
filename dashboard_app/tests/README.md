# Dashboard App Tests

This directory contains comprehensive tests for the dashboard_app in the CozyWish platform.

## Test Structure

The tests are organized into the following files:

- `simple_test.py`: A simple test to verify that the test setup works correctly.
- `test_models.py`: Tests for all models in the dashboard_app.
- `test_forms.py`: Tests for all forms in the dashboard_app.
- `test_views.py`: Tests for all views in the dashboard_app.
- `test_urls.py`: Tests for URL routing in the dashboard_app.
- `test_integration.py`: Integration tests that test complete user flows.
- `test_commands.py`: Tests for management commands.

## Running the Tests

### Running All Tests

To run all tests for the dashboard_app, use the following command from the project root:

```bash
python manage.py test dashboard_app
```

### Running Specific Test Files

To run tests from a specific file, use:

```bash
python manage.py test dashboard_app.tests.test_models
python manage.py test dashboard_app.tests.test_forms
python manage.py test dashboard_app.tests.test_views
python manage.py test dashboard_app.tests.test_urls
python manage.py test dashboard_app.tests.test_integration
python manage.py test dashboard_app.tests.test_commands
```

### Running Specific Test Classes or Methods

To run a specific test class:

```bash
python manage.py test dashboard_app.tests.test_models.DashboardPreferenceModelTest
```

To run a specific test method:

```bash
python manage.py test dashboard_app.tests.test_models.DashboardPreferenceModelTest.test_dashboard_preference_creation
```

## Test Coverage

The tests cover:

1. **Models**: Creation, validation, methods, and relationships between models.
2. **Forms**: Validation, field requirements, and form processing.
3. **Views**: GET and POST requests, context data, redirects, and permissions.
4. **URLs**: URL routing and resolution.
5. **Integration**: Complete user flows for dashboard customization and widget management.
6. **Commands**: Management commands for creating default widgets and resetting user dashboards.

## Adding New Tests

When adding new features to the dashboard_app, please add corresponding tests to maintain test coverage. Follow these guidelines:

1. Place model tests in `test_models.py`
2. Place form tests in `test_forms.py`
3. Place view tests in `test_views.py`
4. Place URL tests in `test_urls.py`
5. Place integration tests in `test_integration.py`
6. Place command tests in `test_commands.py`

## Test Data

The tests create their own test data and do not rely on fixtures or external data sources. This ensures that tests are self-contained and repeatable.
