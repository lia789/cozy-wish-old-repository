# CMS App Tests

This directory contains comprehensive tests for the cms_app in the CozyWish platform.

## Test Structure

The tests are organized into the following files:

- `simple_test.py`: A simple test to verify that the test setup works correctly.
- `test_models.py`: Tests for all models in the cms_app.
- `test_forms.py`: Tests for all forms in the cms_app.
- `test_views.py`: Tests for all views in the cms_app.
- `test_urls.py`: Tests for URL routing in the cms_app.
- `test_templatetags.py`: Tests for custom template tags.
- `test_context_processors.py`: Tests for context processors.
- `test_sitemaps.py`: Tests for sitemaps.
- `test_structured_data.py`: Tests for structured data.
- `test_security.py`: Tests for security measures.
- `test_commands.py`: Tests for management commands.

## Running the Tests

### Running All Tests

To run all tests for the cms_app, use the following command from the project root:

```bash
python manage.py test cms_app
```

### Running Specific Test Files

To run tests from a specific file, use:

```bash
python manage.py test cms_app.tests.test_models
python manage.py test cms_app.tests.test_forms
python manage.py test cms_app.tests.test_views
python manage.py test cms_app.tests.test_urls
python manage.py test cms_app.tests.test_templatetags
python manage.py test cms_app.tests.test_context_processors
python manage.py test cms_app.tests.test_sitemaps
python manage.py test cms_app.tests.test_structured_data
python manage.py test cms_app.tests.test_security
python manage.py test cms_app.tests.test_commands
```

### Running Specific Test Classes or Methods

To run a specific test class:

```bash
python manage.py test cms_app.tests.test_models.PageModelTest
```

To run a specific test method:

```bash
python manage.py test cms_app.tests.test_models.PageModelTest.test_page_creation
```

## Test Coverage

The tests cover:

1. **Models**: Creation, validation, methods, and relationships between models.
2. **Forms**: Validation, field requirements, and form processing.
3. **Views**: GET and POST requests, context data, redirects, and permissions.
4. **URLs**: URL routing and resolution.
5. **Template Tags**: Custom template tags functionality.
6. **Context Processors**: Context data added to templates.
7. **Sitemaps**: Sitemap generation and content.
8. **Structured Data**: JSON-LD structured data generation.
9. **Security**: Access control and permissions.
10. **Commands**: Management command functionality.

## Adding New Tests

When adding new features to the cms_app, please add corresponding tests to maintain test coverage. Follow these guidelines:

1. Place model tests in `test_models.py`
2. Place form tests in `test_forms.py`
3. Place view tests in `test_views.py`
4. Place URL tests in `test_urls.py`
5. Place template tag tests in `test_templatetags.py`
6. Place context processor tests in `test_context_processors.py`
7. Place sitemap tests in `test_sitemaps.py`
8. Place structured data tests in `test_structured_data.py`
9. Place security tests in `test_security.py`
10. Place command tests in `test_commands.py`

## Test Data

The tests create their own test data and do not rely on fixtures or external data sources. This ensures that tests are self-contained and repeatable.
