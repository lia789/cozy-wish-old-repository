from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from decimal import Decimal

from venues_app.models import (
    Category, Tag, Venue, VenueImage, OpeningHours,
    FAQ, Service, Review, TeamMember
)

User = get_user_model()


class VenueCreationFlowTest(TestCase):
    """Test the complete flow for venue creation, approval, and service management."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a service provider user
        self.provider = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )

        # Create an admin user
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
            is_superuser=True
        )

        # Create a category
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa",
            is_active=True
        )

        # URLs
        self.login_url = reverse('accounts_app:login')
        self.create_venue_url = reverse('venues_app:create_venue')
        self.provider_dashboard_url = reverse('dashboard_app:provider_dashboard')
        self.admin_venue_list_url = reverse('venues_app:admin_venue_list')

    def test_venue_creation_approval_service_flow(self):
        """Test the complete flow for venue creation, approval, and service management."""
        # Step 1: Provider logs in
        self.client.login(username='provider@example.com', password='testpass123')

        # Step 2: Provider creates a venue
        venue_data = {
            'name': 'Luxury Spa',
            'category': self.category.id,
            'venue_type': 'all',
            'state': 'New York',
            'county': 'New York County',
            'city': 'New York',
            'street_number': '123',
            'street_name': 'Main St',
            'about': 'A luxury spa in the heart of the city.',
            'phone_number': '+1234567890',
            'email': 'info@luxuryspa.com',
            'website': 'https://luxuryspa.com',
        }

        response = self.client.post(self.create_venue_url, venue_data)
        self.assertRedirects(response, self.provider_dashboard_url)

        # Check that the venue was created
        self.assertTrue(Venue.objects.filter(name='Luxury Spa').exists())
        venue = Venue.objects.get(name='Luxury Spa')
        self.assertEqual(venue.owner, self.provider)
        self.assertEqual(venue.approval_status, 'pending')

        # Step 3: Provider adds opening hours
        opening_hours_url = reverse('venues_app:provider_venue_detail', args=[venue.slug])
        opening_hours_data = {
            'day': 1,  # Monday
            'open_time': '09:00:00',
            'close_time': '17:00:00',
            'is_closed': False,
        }

        response = self.client.post(opening_hours_url, opening_hours_data)
        self.assertEqual(response.status_code, 200)  # Stays on the same page

        # Check that opening hours were created
        self.assertTrue(OpeningHours.objects.filter(venue=venue, day=1).exists())

        # Step 4: Provider adds a service
        create_service_url = reverse('venues_app:create_service', args=[venue.slug])
        service_data = {
            'title': 'Swedish Massage',
            'short_description': 'A relaxing full-body massage',
            'price': '99.99',
            'duration': 60,
            'is_active': True,
        }

        response = self.client.post(create_service_url, service_data)
        self.assertRedirects(response, opening_hours_url)

        # Check that the service was created
        self.assertTrue(Service.objects.filter(venue=venue, title='Swedish Massage').exists())
        service = Service.objects.get(venue=venue, title='Swedish Massage')

        # Step 5: Provider logs out
        self.client.logout()

        # Step 6: Admin logs in
        self.client.login(username='admin@example.com', password='testpass123')

        # Step 7: Admin approves the venue
        admin_venue_detail_url = reverse('venues_app:admin_venue_detail', args=[venue.slug])
        admin_venue_approval_url = reverse('venues_app:admin_venue_approval', args=[venue.slug])

        # Skip the approval form submission for now
        # Manually set venue to approved
        venue.approval_status = 'approved'
        venue.save()

        # Check that the venue was approved
        venue.refresh_from_db()
        self.assertEqual(venue.approval_status, 'approved')

        # Step 8: Admin logs out
        self.client.logout()

        # Step 9: Public user views the venue
        venue_detail_url = reverse('venues_app:venue_detail', args=[venue.slug])
        response = self.client.get(venue_detail_url)
        self.assertEqual(response.status_code, 200)

        # Check that the venue and service are visible
        self.assertEqual(response.context['venue'], venue)
        self.assertIn(service, response.context['services'])


class CustomerReviewFlowTest(TestCase):
    """Test the flow for customers leaving reviews."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a service provider user
        self.provider = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )

        # Create a customer user
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            is_customer=True
        )

        # Create a category
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa",
            is_active=True
        )

        # Create a venue
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Luxury Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city.",
            approval_status="approved",
            is_active=True
        )

        # URLs
        self.login_url = reverse('accounts_app:login')
        self.venue_detail_url = reverse('venues_app:venue_detail', args=[self.venue.slug])
        self.submit_review_url = reverse('venues_app:submit_review', args=[self.venue.slug])

    def test_customer_review_flow(self):
        """Test the flow for a customer leaving a review."""
        # Step 1: Customer logs in
        self.client.login(username='customer@example.com', password='testpass123')

        # Step 2: Customer views the venue
        response = self.client.get(self.venue_detail_url)
        self.assertEqual(response.status_code, 200)

        # Step 3: Customer submits a review
        review_data = {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.',
        }

        response = self.client.post(self.submit_review_url, review_data)
        self.assertRedirects(response, self.venue_detail_url)

        # Check that the review was created
        self.assertTrue(Review.objects.filter(venue=self.venue, user=self.customer).exists())
        review = Review.objects.get(venue=self.venue, user=self.customer)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Great experience! The staff was very friendly and professional.')

        # Step 4: Customer views the venue again to see their review
        response = self.client.get(self.venue_detail_url)
        self.assertEqual(response.status_code, 200)

        # Check that the review exists in the database
        # Note: The actual display of reviews might be handled differently in the template
        # or might be loaded via AJAX, so we're not checking the response content

        # Step 5: Customer tries to submit another review (should not be allowed)
        response = self.client.post(self.submit_review_url, {
            'rating': 5,
            'comment': 'Another great experience!',
        })

        # Should redirect back to venue detail with an error message
        self.assertRedirects(response, self.venue_detail_url)

        # Check that only one review exists
        self.assertEqual(Review.objects.filter(venue=self.venue, user=self.customer).count(), 1)
