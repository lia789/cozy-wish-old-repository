# Notifications App Tests

This directory contains comprehensive tests for the notifications_app. The tests are organized into different files based on the component being tested.

## Test Files

1. **test_models.py**: Tests for all models in the notifications_app
   - `NotificationCategoryModelTest`: Tests for the NotificationCategory model
   - `NotificationModelTest`: Tests for the Notification model
   - `UserNotificationModelTest`: Tests for the UserNotification model
   - `NotificationPreferenceModelTest`: Tests for the NotificationPreference model

2. **test_utils.py**: Tests for utility functions in the notifications_app
   - `CreateNotificationTest`: Tests for the create_notification function
   - `ShouldNotifyUserTest`: Tests for the should_notify_user function
   - `SendNotificationEmailTest`: Tests for the send_notification_email function
   - `GetUserNotificationsTest`: Tests for the get_user_notifications function
   - `GetUnreadCountTest`: Tests for the get_unread_count function
   - `MarkAllAsReadTest`: Tests for the mark_all_as_read function
   - `CreateSystemAnnouncementTest`: Tests for the create_system_announcement function
   - `NotificationEventTest`: Tests for notification event utility functions

3. **test_forms.py**: Tests for forms in the notifications_app
   - `NotificationPreferenceFormTest`: Tests for the NotificationPreferenceForm
   - `SystemAnnouncementFormTest`: Tests for the SystemAnnouncementForm
   - `NotificationCategoryFormTest`: Tests for the NotificationCategoryForm

4. **test_views.py**: Tests for views in the notifications_app
   - `NotificationListViewTest`: Tests for the notification list view
   - `NotificationDetailViewTest`: Tests for the notification detail view
   - `NotificationActionViewsTest`: Tests for notification action views
   - `NotificationPreferencesViewTest`: Tests for the notification preferences view
   - `GetUnreadNotificationsViewTest`: Tests for the get_unread_notifications view
   - `AdminNotificationViewsTest`: Tests for admin notification views

5. **test_urls.py**: Tests for URL patterns in the notifications_app
   - `UrlsTest`: Tests for all URL patterns

6. **test_signals.py**: Tests for signals in the notifications_app
   - `BookingSignalTest`: Tests for booking-related signals
   - `ReviewSignalTest`: Tests for review-related signals
   - `ServiceProviderSignalTest`: Tests for service provider-related signals

7. **test_admin.py**: Tests for Django admin in the notifications_app
   - `NotificationAdminTest`: Tests for admin classes and views

8. **test_integration.py**: Integration tests for the notifications_app
   - `NotificationIntegrationTest`: Tests for complete notification flows

9. **test_security.py**: Security tests for the notifications_app
   - `NotificationSecurityTest`: Tests for access control and security features

10. **test_commands.py**: Tests for management commands in the notifications_app
    - `CleanExpiredNotificationsCommandTest`: Tests for the clean_expired_notifications command

## Running the Tests

You can run the tests using the provided `run_tests.py` script in the notifications_app directory:

```bash
# Run all tests
./run_tests.py

# Run tests with verbose output
./run_tests.py --verbose

# Run tests with coverage report
./run_tests.py --coverage

# Run tests with coverage report and generate HTML report
./run_tests.py --coverage --html

# Run specific test file
./run_tests.py --specific=test_models
```

Alternatively, you can use Django's test runner:

```bash
# Run all tests for the notifications_app
python manage.py test notifications_app

# Run specific test file
python manage.py test notifications_app.tests.test_models
```
