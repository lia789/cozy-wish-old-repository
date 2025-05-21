from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from dashboard_app.models import DashboardPreference, DashboardWidget, UserWidget
from venues_app.models import Venue, Service, Review
from booking_cart_app.models import Booking, BookingItem

User = get_user_model()


class DashboardRedirectViewTest(TestCase):
    """Test the dashboard redirect view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:dashboard_redirect')

        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )

    def test_dashboard_redirect_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_dashboard_redirect_customer(self):
        """Test that customers are redirected to customer dashboard"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))

    def test_dashboard_redirect_provider(self):
        """Test that service providers are redirected to provider dashboard"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))

    def test_dashboard_redirect_admin(self):
        """Test that admins are redirected to admin dashboard"""
        self.client.login(username='admin@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard_app:admin_dashboard'))


class CustomerDashboardViewTest(TestCase):
    """Test the customer dashboard view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:customer_dashboard')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create dashboard preference
        self.preference = DashboardPreference.objects.create(
            user=self.customer,
            theme='light',
            compact_view=False
        )

        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Recent Bookings',
            description='Shows recent bookings',
            widget_type='list',
            template_name='dashboard_app/widgets/recent_bookings.html',
            icon_class='fas fa-calendar',
            user_type='customer'
        )

        self.widget2 = DashboardWidget.objects.create(
            name='Favorite Venues',
            description='Shows favorite venues',
            widget_type='list',
            template_name='dashboard_app/widgets/favorite_venues.html',
            icon_class='fas fa-heart',
            user_type='customer'
        )

        # Add widgets to user
        self.user_widget1 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

        self.user_widget2 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget2,
            position=1,
            is_visible=True
        )

    def test_customer_dashboard_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_customer_dashboard_authenticated_non_customer(self):
        """Test that non-customers cannot access customer dashboard"""
        # Create a service provider
        provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected

    def test_customer_dashboard_authenticated_customer(self):
        """Test that customers can access customer dashboard"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/dashboard.html')

        # Check context
        self.assertEqual(response.context['preference'], self.preference)
        self.assertIn(self.user_widget1, response.context['user_widgets'])
        self.assertIn(self.user_widget2, response.context['user_widgets'])


class CustomerBookingHistoryViewTest(TestCase):
    """Test the customer booking history view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:customer_booking_history')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a service provider
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name='Test Spa',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='123',
            street_name='Main St',
            approval_status='approved',
            is_active=True
        )

        # Create a service
        self.service = Service.objects.create(
            name='Test Service',
            venue=self.venue,
            price=100.00,
            duration=60,
            is_active=True
        )

        # Create bookings
        self.booking1 = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=100.00
        )

        self.booking_item1 = BookingItem.objects.create(
            booking=self.booking1,
            service=self.service,
            date=timezone.now().date(),
            time_slot=timezone.now().time(),
            service_price=100.00
        )

        self.booking2 = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            booking_date=timezone.now().date() - timedelta(days=7),
            status='completed',
            total_price=100.00
        )

        self.booking_item2 = BookingItem.objects.create(
            booking=self.booking2,
            service=self.service,
            date=timezone.now().date() - timedelta(days=7),
            time_slot=timezone.now().time(),
            service_price=100.00
        )

    def test_customer_booking_history_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_customer_booking_history_authenticated_non_customer(self):
        """Test that non-customers cannot access customer booking history"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected

    def test_customer_booking_history_authenticated_customer(self):
        """Test that customers can access booking history"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/booking_history.html')

        # Check context
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 2)
        self.assertIn(self.booking1, response.context['bookings'])
        self.assertIn(self.booking2, response.context['bookings'])

    def test_customer_booking_history_filter(self):
        """Test filtering booking history"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Filter by period (last 7 days)
        response = self.client.get(f"{self.url}?period=last_7_days")
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)  # Only booking1 is within last 7 days
        self.assertIn(self.booking1, response.context['bookings'])

        # Filter by custom date range
        start_date = (timezone.now().date() - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (timezone.now().date() - timedelta(days=5)).strftime('%Y-%m-%d')
        response = self.client.get(f"{self.url}?period=custom&start_date={start_date}&end_date={end_date}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)  # Only booking2 is within this range
        self.assertIn(self.booking2, response.context['bookings'])


class CustomerActiveBookingsViewTest(TestCase):
    """Test the customer active bookings view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:customer_active_bookings')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a service provider
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            name='Test Spa',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='123',
            street_name='Main St',
            approval_status='approved',
            is_active=True
        )

        # Create a service
        self.service = Service.objects.create(
            name='Test Service',
            venue=self.venue,
            price=100.00,
            duration=60,
            is_active=True
        )

        # Create active booking (confirmed)
        self.active_booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=100.00
        )

        # Create booking item for today
        self.today_booking_item = BookingItem.objects.create(
            booking=self.active_booking,
            service=self.service,
            date=timezone.now().date(),
            time_slot=timezone.now().time(),
            service_price=100.00
        )

        # Create booking item for future
        self.future_booking_item = BookingItem.objects.create(
            booking=self.active_booking,
            service=self.service,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time(),
            service_price=100.00
        )

        # Create inactive booking (completed)
        self.inactive_booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            booking_date=timezone.now().date() - timedelta(days=7),
            status='completed',
            total_price=100.00
        )

        self.inactive_booking_item = BookingItem.objects.create(
            booking=self.inactive_booking,
            service=self.service,
            date=timezone.now().date() - timedelta(days=7),
            time_slot=timezone.now().time(),
            service_price=100.00
        )

    def test_customer_active_bookings_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_customer_active_bookings_authenticated_non_customer(self):
        """Test that non-customers cannot access customer active bookings"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected

    def test_customer_active_bookings_authenticated_customer(self):
        """Test that customers can access active bookings"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/active_bookings.html')

        # Check context
        self.assertIn('active_bookings', response.context)
        self.assertEqual(len(response.context['active_bookings']), 1)
        self.assertIn(self.active_booking, response.context['active_bookings'])
        self.assertNotIn(self.inactive_booking, response.context['active_bookings'])

        # Check upcoming booking items
        self.assertIn('upcoming_booking_items', response.context)
        self.assertEqual(len(response.context['upcoming_booking_items']), 2)

        # Check that the current time is in the context
        self.assertIn('now', response.context)


class CustomerFavoriteVenuesViewTest(TestCase):
    """Test the customer favorite venues view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:customer_favorite_venues')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a service provider
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create venues
        self.venue1 = Venue.objects.create(
            name='Test Spa 1',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='123',
            street_name='Main St',
            approval_status='approved',
            is_active=True
        )

        self.venue2 = Venue.objects.create(
            name='Test Spa 2',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='456',
            street_name='Broadway',
            approval_status='approved',
            is_active=True
        )

        # Create bookings for venue1
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue1,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=100.00
        )

        # Create review for venue2
        self.review = Review.objects.create(
            user=self.customer,
            venue=self.venue2,
            rating=4,
            comment='Great service!',
            is_approved=True
        )

    def test_customer_favorite_venues_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_customer_favorite_venues_authenticated_non_customer(self):
        """Test that non-customers cannot access customer favorite venues"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected

    def test_customer_favorite_venues_authenticated_customer(self):
        """Test that customers can access favorite venues"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/favorite_venues.html')

        # Check context
        self.assertIn('favorite_venues', response.context)
        self.assertEqual(len(response.context['favorite_venues']), 2)
        self.assertIn(self.venue1, response.context['favorite_venues'])  # Booked venue
        self.assertIn(self.venue2, response.context['favorite_venues'])  # Reviewed venue

        # Check venue booking counts
        self.assertIn('venue_booking_counts', response.context)
        self.assertEqual(response.context['venue_booking_counts'][self.venue1.id], 1)

        # Check venue reviews
        self.assertIn('venue_reviews', response.context)
        self.assertEqual(response.context['venue_reviews'][self.venue2.id], self.review)


class CustomerReviewHistoryViewTest(TestCase):
    """Test the customer review history view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:customer_review_history')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create a service provider
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        # Create venues
        self.venue1 = Venue.objects.create(
            name='Test Spa 1',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='123',
            street_name='Main St',
            approval_status='approved',
            is_active=True
        )

        self.venue2 = Venue.objects.create(
            name='Test Spa 2',
            owner=self.provider,
            state='New York',
            city='New York City',
            street_number='456',
            street_name='Broadway',
            approval_status='approved',
            is_active=True
        )

        # Create reviews
        self.review1 = Review.objects.create(
            user=self.customer,
            venue=self.venue1,
            rating=5,
            comment='Excellent service!',
            is_approved=True
        )

        self.review2 = Review.objects.create(
            user=self.customer,
            venue=self.venue2,
            rating=3,
            comment='Average service.',
            is_approved=False
        )

    def test_customer_review_history_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_customer_review_history_authenticated_non_customer(self):
        """Test that non-customers cannot access customer review history"""
        self.client.login(username='provider@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected

    def test_customer_review_history_authenticated_customer(self):
        """Test that customers can access review history"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/review_history.html')

        # Check context
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 2)
        self.assertIn(self.review1, response.context['reviews'])
        self.assertIn(self.review2, response.context['reviews'])


class DashboardPreferencesViewTest(TestCase):
    """Test the dashboard preferences view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:dashboard_preferences')

        # Create users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )

        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )

        # Create preferences
        self.customer_preference = DashboardPreference.objects.create(
            user=self.customer,
            theme='light',
            compact_view=False
        )

        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Widget 1',
            description='First widget',
            widget_type='stats',
            template_name='dashboard_app/widgets/widget1.html',
            icon_class='fas fa-chart-bar',
            user_type='all'
        )

        self.widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            description='Second widget',
            widget_type='chart',
            template_name='dashboard_app/widgets/widget2.html',
            icon_class='fas fa-chart-line',
            user_type='all'
        )

        # Add widgets to user
        self.user_widget1 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

        self.user_widget2 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget2,
            position=1,
            is_visible=True
        )

    def test_dashboard_preferences_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_dashboard_preferences_get(self):
        """Test getting dashboard preferences"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/preferences.html')

        # Check context
        self.assertIn('form', response.context)
        self.assertIn('user_widgets', response.context)
        self.assertEqual(len(response.context['user_widgets']), 2)
        self.assertIn(self.user_widget1, response.context['user_widgets'])
        self.assertIn(self.user_widget2, response.context['user_widgets'])

    def test_dashboard_preferences_post(self):
        """Test updating dashboard preferences"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Update preferences
        response = self.client.post(self.url, {
            'theme': 'dark',
            'compact_view': 'on'
        })

        # Should redirect back to preferences page
        self.assertRedirects(response, self.url)

        # Check that preferences were updated
        self.customer_preference.refresh_from_db()
        self.assertEqual(self.customer_preference.theme, 'dark')
        self.assertTrue(self.customer_preference.compact_view)

    def test_dashboard_preferences_post_invalid(self):
        """Test updating dashboard preferences with invalid data"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Update preferences with invalid theme
        response = self.client.post(self.url, {
            'theme': 'invalid_theme',
            'compact_view': 'on'
        })

        # Should stay on preferences page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/preferences.html')

        # Check that preferences were not updated
        self.customer_preference.refresh_from_db()
        self.assertEqual(self.customer_preference.theme, 'light')
        self.assertFalse(self.customer_preference.compact_view)

        # Check for form errors
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)


class AddWidgetViewTest(TestCase):
    """Test the add widget view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:add_widget')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Customer Widget',
            description='Widget for customers',
            widget_type='stats',
            template_name='dashboard_app/widgets/customer_widget.html',
            icon_class='fas fa-user',
            user_type='customer'
        )

        self.widget2 = DashboardWidget.objects.create(
            name='All Users Widget',
            description='Widget for all users',
            widget_type='list',
            template_name='dashboard_app/widgets/all_users_widget.html',
            icon_class='fas fa-users',
            user_type='all'
        )

        self.widget3 = DashboardWidget.objects.create(
            name='Provider Widget',
            description='Widget for providers',
            widget_type='chart',
            template_name='dashboard_app/widgets/provider_widget.html',
            icon_class='fas fa-store',
            user_type='provider'
        )

        # Add widget1 to user
        self.user_widget = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

    def test_add_widget_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_add_widget_get(self):
        """Test getting the add widget page"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/add_widget.html')

        # Check context
        self.assertIn('available_widgets', response.context)
        self.assertEqual(len(response.context['available_widgets']), 1)  # Only widget2 is available (widget1 is already added)
        self.assertIn(self.widget2, response.context['available_widgets'])
        self.assertNotIn(self.widget1, response.context['available_widgets'])  # Already added
        self.assertNotIn(self.widget3, response.context['available_widgets'])  # Not for customers

    def test_add_widget_post(self):
        """Test adding a widget"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Add widget2
        response = self.client.post(self.url, {
            'widget': self.widget2.id
        })

        # Should redirect back to dashboard
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))

        # Check that widget was added
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 2)
        self.assertTrue(user_widgets.filter(widget=self.widget2).exists())

        # Check position
        new_widget = user_widgets.get(widget=self.widget2)
        self.assertEqual(new_widget.position, 1)  # Should be after existing widget

    def test_add_widget_post_invalid(self):
        """Test adding a widget with invalid data"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Add non-existent widget
        response = self.client.post(self.url, {
            'widget': 999  # Non-existent widget ID
        })

        # Should stay on add widget page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/add_widget.html')

        # Check that no widget was added
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 1)

        # Check for form errors
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_add_widget_post_already_added(self):
        """Test adding a widget that is already added"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Try to add widget1 again
        response = self.client.post(self.url, {
            'widget': self.widget1.id
        })

        # Should stay on add widget page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/add_widget.html')

        # Check that no additional widget was added
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 1)

        # Check for form errors or messages
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)


class RemoveWidgetViewTest(TestCase):
    """Test the remove widget view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create another customer
        self.other_customer = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Widget 1',
            description='First widget',
            widget_type='stats',
            template_name='dashboard_app/widgets/widget1.html',
            icon_class='fas fa-chart-bar',
            user_type='all'
        )

        self.widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            description='Second widget',
            widget_type='chart',
            template_name='dashboard_app/widgets/widget2.html',
            icon_class='fas fa-chart-line',
            user_type='all'
        )

        # Add widgets to user
        self.user_widget1 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

        self.user_widget2 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget2,
            position=1,
            is_visible=True
        )

        # Add widget to other customer
        self.other_user_widget = UserWidget.objects.create(
            user=self.other_customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

        # URL for removing widget1
        self.url = reverse('dashboard_app:remove_widget', args=[self.user_widget1.id])

    def test_remove_widget_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_remove_widget_get(self):
        """Test removing a widget with GET request"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)

        # Should redirect back to dashboard preferences
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))

        # Check that widget was removed
        self.assertFalse(UserWidget.objects.filter(id=self.user_widget1.id).exists())

        # Check that other widget still exists
        self.assertTrue(UserWidget.objects.filter(id=self.user_widget2.id).exists())

        # Check that other user's widget still exists
        self.assertTrue(UserWidget.objects.filter(id=self.other_user_widget.id).exists())

    def test_remove_widget_post(self):
        """Test removing a widget with POST request"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.post(self.url)

        # Should redirect back to dashboard preferences
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))

        # Check that widget was removed
        self.assertFalse(UserWidget.objects.filter(id=self.user_widget1.id).exists())

    def test_remove_widget_other_user(self):
        """Test that a user cannot remove another user's widget"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Try to remove other user's widget
        url = reverse('dashboard_app:remove_widget', args=[self.other_user_widget.id])
        response = self.client.get(url)

        # Should redirect back to dashboard preferences
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))

        # Check that widget was not removed
        self.assertTrue(UserWidget.objects.filter(id=self.other_user_widget.id).exists())


class ReorderWidgetsViewTest(TestCase):
    """Test the reorder widgets view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.url = reverse('dashboard_app:reorder_widgets')

        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Widget 1',
            description='First widget',
            widget_type='stats',
            template_name='dashboard_app/widgets/widget1.html',
            icon_class='fas fa-chart-bar',
            user_type='all'
        )

        self.widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            description='Second widget',
            widget_type='chart',
            template_name='dashboard_app/widgets/widget2.html',
            icon_class='fas fa-chart-line',
            user_type='all'
        )

        self.widget3 = DashboardWidget.objects.create(
            name='Widget 3',
            description='Third widget',
            widget_type='table',
            template_name='dashboard_app/widgets/widget3.html',
            icon_class='fas fa-table',
            user_type='all'
        )

        # Add widgets to user
        self.user_widget1 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget1,
            position=0,
            is_visible=True
        )

        self.user_widget2 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget2,
            position=1,
            is_visible=True
        )

        self.user_widget3 = UserWidget.objects.create(
            user=self.customer,
            widget=self.widget3,
            position=2,
            is_visible=True
        )

    def test_reorder_widgets_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts_app:login")}?next={self.url}'
        )

    def test_reorder_widgets_get(self):
        """Test getting the reorder widgets page"""
        self.client.login(username='customer@example.com', password='testpass123')
        response = self.client.get(self.url)

        # Should redirect to dashboard preferences
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))

    def test_reorder_widgets_post(self):
        """Test reordering widgets"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Reorder widgets: 3, 1, 2
        response = self.client.post(
            self.url,
            {
                'widget_order': [self.user_widget3.id, self.user_widget1.id, self.user_widget2.id]
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # AJAX request
        )

        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Check response data
        data = response.json()
        self.assertEqual(data['status'], 'success')

        # Check that widgets were reordered
        self.user_widget1.refresh_from_db()
        self.user_widget2.refresh_from_db()
        self.user_widget3.refresh_from_db()

        self.assertEqual(self.user_widget3.position, 0)
        self.assertEqual(self.user_widget1.position, 1)
        self.assertEqual(self.user_widget2.position, 2)

    def test_reorder_widgets_post_invalid(self):
        """Test reordering widgets with invalid data"""
        self.client.login(username='customer@example.com', password='testpass123')

        # Invalid widget IDs
        response = self.client.post(
            self.url,
            {
                'widget_order': [999, 888, 777]  # Non-existent widget IDs
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # AJAX request
        )

        # Should return JSON response with error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Check response data
        data = response.json()
        self.assertEqual(data['status'], 'error')

        # Check that widgets were not reordered
        self.user_widget1.refresh_from_db()
        self.user_widget2.refresh_from_db()
        self.user_widget3.refresh_from_db()

        self.assertEqual(self.user_widget1.position, 0)
        self.assertEqual(self.user_widget2.position, 1)
        self.assertEqual(self.user_widget3.position, 2)