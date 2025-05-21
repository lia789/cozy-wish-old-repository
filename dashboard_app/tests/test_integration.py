from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from dashboard_app.models import DashboardPreference, DashboardWidget, UserWidget
from venues_app.models import Venue, Service, Review
from booking_cart_app.models import Booking, BookingItem

User = get_user_model()


class CustomerDashboardIntegrationTest(TestCase):
    """Test the complete customer dashboard flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
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
        
        # Create a booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=100.00
        )
        
        self.booking_item = BookingItem.objects.create(
            booking=self.booking,
            service=self.service,
            date=timezone.now().date() + timedelta(days=2),
            time_slot=timezone.now().time(),
            service_price=100.00
        )
        
        # Create a review
        self.review = Review.objects.create(
            user=self.customer,
            venue=self.venue,
            rating=5,
            comment='Excellent service!',
            is_approved=True
        )
        
        # Create dashboard widgets
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
        
        self.widget3 = DashboardWidget.objects.create(
            name='Recent Reviews',
            description='Shows recent reviews',
            widget_type='list',
            template_name='dashboard_app/widgets/recent_reviews.html',
            icon_class='fas fa-star',
            user_type='customer'
        )
    
    def test_customer_dashboard_flow(self):
        """Test the complete customer dashboard flow"""
        # Login
        self.client.login(username='customer@example.com', password='testpass123')
        
        # 1. Visit dashboard
        response = self.client.get(reverse('dashboard_app:customer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/dashboard.html')
        
        # Check that dashboard preference was created automatically
        preference = DashboardPreference.objects.get(user=self.customer)
        self.assertEqual(preference.theme, 'light')  # Default theme
        self.assertFalse(preference.compact_view)  # Default compact_view
        
        # 2. Add widgets
        response = self.client.get(reverse('dashboard_app:add_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/add_widget.html')
        
        # Add widget1
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget1.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))
        
        # Add widget2
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget2.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))
        
        # Add widget3
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget3.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:customer_dashboard'))
        
        # Check that widgets were added
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 3)
        
        # 3. Visit dashboard preferences
        response = self.client.get(reverse('dashboard_app:dashboard_preferences'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/preferences.html')
        
        # 4. Update preferences
        response = self.client.post(
            reverse('dashboard_app:dashboard_preferences'),
            {
                'theme': 'dark',
                'compact_view': 'on'
            }
        )
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))
        
        # Check that preferences were updated
        preference.refresh_from_db()
        self.assertEqual(preference.theme, 'dark')
        self.assertTrue(preference.compact_view)
        
        # 5. Reorder widgets
        response = self.client.post(
            reverse('dashboard_app:reorder_widgets'),
            {
                'widget_order': [
                    user_widgets.get(widget=self.widget3).id,
                    user_widgets.get(widget=self.widget1).id,
                    user_widgets.get(widget=self.widget2).id
                ]
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # AJAX request
        )
        self.assertEqual(response.status_code, 200)
        
        # Check that widgets were reordered
        user_widgets.get(widget=self.widget3).refresh_from_db()
        user_widgets.get(widget=self.widget1).refresh_from_db()
        user_widgets.get(widget=self.widget2).refresh_from_db()
        
        self.assertEqual(user_widgets.get(widget=self.widget3).position, 0)
        self.assertEqual(user_widgets.get(widget=self.widget1).position, 1)
        self.assertEqual(user_widgets.get(widget=self.widget2).position, 2)
        
        # 6. Remove a widget
        response = self.client.get(
            reverse('dashboard_app:remove_widget', args=[user_widgets.get(widget=self.widget2).id])
        )
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))
        
        # Check that widget was removed
        user_widgets = UserWidget.objects.filter(user=self.customer)
        self.assertEqual(user_widgets.count(), 2)
        self.assertFalse(UserWidget.objects.filter(user=self.customer, widget=self.widget2).exists())
        
        # 7. Visit active bookings
        response = self.client.get(reverse('dashboard_app:customer_active_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/active_bookings.html')
        
        # Check that booking is in active bookings
        self.assertIn('active_bookings', response.context)
        self.assertEqual(len(response.context['active_bookings']), 1)
        self.assertIn(self.booking, response.context['active_bookings'])
        
        # 8. Visit booking history
        response = self.client.get(reverse('dashboard_app:customer_booking_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/booking_history.html')
        
        # Check that booking is in booking history
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)
        self.assertIn(self.booking, response.context['bookings'])
        
        # 9. Visit favorite venues
        response = self.client.get(reverse('dashboard_app:customer_favorite_venues'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/favorite_venues.html')
        
        # Check that venue is in favorite venues
        self.assertIn('favorite_venues', response.context)
        self.assertEqual(len(response.context['favorite_venues']), 1)
        self.assertIn(self.venue, response.context['favorite_venues'])
        
        # 10. Visit review history
        response = self.client.get(reverse('dashboard_app:customer_review_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/customer/review_history.html')
        
        # Check that review is in review history
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 1)
        self.assertIn(self.review, response.context['reviews'])


class ProviderDashboardIntegrationTest(TestCase):
    """Test the complete service provider dashboard flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a service provider
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpass123',
            is_service_provider=True
        )
        
        # Create a customer
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            is_customer=True
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
            city='Brooklyn',
            street_number='456',
            street_name='Broadway',
            approval_status='approved',
            is_active=True
        )
        
        # Create services
        self.service1 = Service.objects.create(
            name='Massage',
            venue=self.venue1,
            price=100.00,
            duration=60,
            is_active=True
        )
        
        self.service2 = Service.objects.create(
            name='Facial',
            venue=self.venue1,
            price=80.00,
            duration=45,
            is_active=True
        )
        
        self.service3 = Service.objects.create(
            name='Manicure',
            venue=self.venue2,
            price=50.00,
            duration=30,
            is_active=True
        )
        
        # Create bookings
        self.booking1 = Booking.objects.create(
            user=self.customer,
            venue=self.venue1,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=100.00
        )
        
        self.booking_item1 = BookingItem.objects.create(
            booking=self.booking1,
            service=self.service1,
            date=timezone.now().date(),
            time_slot=timezone.now().time(),
            service_price=100.00
        )
        
        self.booking2 = Booking.objects.create(
            user=self.customer,
            venue=self.venue2,
            booking_date=timezone.now().date(),
            status='confirmed',
            total_price=50.00
        )
        
        self.booking_item2 = BookingItem.objects.create(
            booking=self.booking2,
            service=self.service3,
            date=timezone.now().date() + timedelta(days=1),
            time_slot=timezone.now().time(),
            service_price=50.00
        )
        
        # Create reviews
        self.review1 = Review.objects.create(
            user=self.customer,
            venue=self.venue1,
            rating=5,
            comment='Excellent massage!',
            is_approved=True
        )
        
        self.review2 = Review.objects.create(
            user=self.customer,
            venue=self.venue2,
            rating=4,
            comment='Good manicure.',
            is_approved=True
        )
        
        # Create dashboard widgets
        self.widget1 = DashboardWidget.objects.create(
            name='Today\'s Bookings',
            description='Shows today\'s bookings',
            widget_type='list',
            template_name='dashboard_app/widgets/todays_bookings.html',
            icon_class='fas fa-calendar-day',
            user_type='provider'
        )
        
        self.widget2 = DashboardWidget.objects.create(
            name='Revenue Overview',
            description='Shows revenue overview',
            widget_type='chart',
            template_name='dashboard_app/widgets/revenue_overview.html',
            icon_class='fas fa-chart-line',
            user_type='provider'
        )
        
        self.widget3 = DashboardWidget.objects.create(
            name='Recent Reviews',
            description='Shows recent reviews',
            widget_type='list',
            template_name='dashboard_app/widgets/recent_reviews.html',
            icon_class='fas fa-star',
            user_type='all'
        )
    
    def test_provider_dashboard_flow(self):
        """Test the complete service provider dashboard flow"""
        # Login
        self.client.login(username='provider@example.com', password='testpass123')
        
        # 1. Visit dashboard
        response = self.client.get(reverse('dashboard_app:provider_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/dashboard.html')
        
        # Check that dashboard preference was created automatically
        preference = DashboardPreference.objects.get(user=self.provider)
        self.assertEqual(preference.theme, 'light')  # Default theme
        self.assertFalse(preference.compact_view)  # Default compact_view
        
        # 2. Add widgets
        response = self.client.get(reverse('dashboard_app:add_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/add_widget.html')
        
        # Add widget1
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget1.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))
        
        # Add widget2
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget2.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))
        
        # Add widget3
        response = self.client.post(
            reverse('dashboard_app:add_widget'),
            {'widget': self.widget3.id}
        )
        self.assertRedirects(response, reverse('dashboard_app:provider_dashboard'))
        
        # Check that widgets were added
        user_widgets = UserWidget.objects.filter(user=self.provider)
        self.assertEqual(user_widgets.count(), 3)
        
        # 3. Visit today's bookings
        response = self.client.get(reverse('dashboard_app:provider_todays_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/todays_bookings.html')
        
        # 4. Visit revenue reports
        response = self.client.get(reverse('dashboard_app:provider_revenue_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/revenue_reports.html')
        
        # 5. Visit service performance
        response = self.client.get(reverse('dashboard_app:provider_service_performance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/service_performance.html')
        
        # 6. Visit discount performance
        response = self.client.get(reverse('dashboard_app:provider_discount_performance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/discount_performance.html')
        
        # 7. Visit team management
        response = self.client.get(reverse('dashboard_app:provider_team_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_app/provider/team_management.html')
        
        # 8. Update dashboard preferences
        response = self.client.post(
            reverse('dashboard_app:dashboard_preferences'),
            {
                'theme': 'dark',
                'compact_view': 'on'
            }
        )
        self.assertRedirects(response, reverse('dashboard_app:dashboard_preferences'))
        
        # Check that preferences were updated
        preference.refresh_from_db()
        self.assertEqual(preference.theme, 'dark')
        self.assertTrue(preference.compact_view)
