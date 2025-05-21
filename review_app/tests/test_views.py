from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from venues_app.models import Category, Venue
from booking_cart_app.models import Booking, BookingItem, Service
from review_app.models import Review, ReviewResponse, ReviewFlag
from review_app.forms import ReviewForm, StarRatingForm, ReviewResponseForm, ReviewFlagForm

User = get_user_model()

# Helper function to create a completed booking
def create_completed_booking(user, venue):
    """Create a completed booking for testing"""
    service = Service.objects.create(
        venue=venue,
        title="Test Service",
        short_description="A test service",
        price=100.00,
        duration=60,
        is_active=True
    )

    booking = Booking.objects.create(
        user=user,
        venue=venue,
        status='completed',
        booking_date=timezone.now() - timedelta(days=7),
        total_price=100.00
    )

    booking_item = BookingItem.objects.create(
        booking=booking,
        service=service,
        price=100.00,
        quantity=1
    )

    return booking


class CustomerViewsTest(TestCase):
    """Test the customer views in the review_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

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

        # Create category
        self.category = Category.objects.create(name="Spa")

        # Create venue
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Test Spa",
            category=self.category,
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city."
        )

        # Create a completed booking
        self.booking = create_completed_booking(self.customer, self.venue)

        # Create a review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )

        # URLs
        self.submit_review_url = reverse('review_app:submit_review', args=[self.venue.id])
        self.edit_review_url = reverse('review_app:edit_review', args=[self.review.id])
        self.flag_review_url = reverse('review_app:flag_review', args=[self.review.id])
        self.customer_review_history_url = reverse('review_app:customer_review_history')
        self.venue_reviews_url = reverse('review_app:venue_reviews', args=[self.venue.id])

    def test_submit_review_view_get(self):
        """Test the submit review view GET request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the submit review page
        response = self.client.get(self.submit_review_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/submit_review.html')
        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertEqual(response.context['venue'], self.venue)

    def test_submit_review_view_post(self):
        """Test the submit review view POST request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Delete existing review to test creation
        self.review.delete()

        # Submit a new review
        response = self.client.post(self.submit_review_url, {
            'rating': 5,
            'comment': 'Excellent service and atmosphere!'
        })

        # Check response
        self.assertRedirects(response, reverse('venues_app:venue_detail', args=[self.venue.id]))

        # Check that the review was created
        self.assertTrue(Review.objects.filter(
            venue=self.venue,
            user=self.customer,
            rating=5,
            comment='Excellent service and atmosphere!'
        ).exists())

    def test_submit_review_without_booking(self):
        """Test submitting a review without a completed booking"""
        # Create a new customer without bookings
        new_customer = User.objects.create_user(
            email='newcustomer@example.com',
            password='testpass123',
            is_customer=True
        )

        # Login as the new customer
        self.client.login(username='newcustomer@example.com', password='testpass123')

        # Try to submit a review
        response = self.client.get(self.submit_review_url)

        # Should redirect with an error message
        self.assertRedirects(response, reverse('venues_app:venue_detail', args=[self.venue.id]))

    def test_edit_review_view_get(self):
        """Test the edit review view GET request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the edit review page
        response = self.client.get(self.edit_review_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/edit_review.html')
        self.assertIsInstance(response.context['form'], StarRatingForm)
        self.assertEqual(response.context['review'], self.review)
        self.assertEqual(response.context['venue'], self.venue)

    def test_edit_review_view_post(self):
        """Test the edit review view POST request"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Edit the review
        response = self.client.post(self.edit_review_url, {
            'rating': 3,
            'comment': 'Updated review content.'
        })

        # Check response
        self.assertRedirects(response, reverse('venues_app:venue_detail', args=[self.venue.id]))

        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, 'Updated review content.')

    def test_flag_review_view_get(self):
        """Test the flag review view GET request"""
        # Create another customer to flag the review
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )

        # Login as the flagger
        self.client.login(username='flagger@example.com', password='testpass123')

        # Get the flag review page
        response = self.client.get(self.flag_review_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/flag_review.html')
        self.assertIsInstance(response.context['form'], ReviewFlagForm)
        self.assertEqual(response.context['review'], self.review)

    def test_flag_review_view_post(self):
        """Test the flag review view POST request"""
        # Create another customer to flag the review
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )

        # Login as the flagger
        self.client.login(username='flagger@example.com', password='testpass123')

        # Flag the review
        response = self.client.post(self.flag_review_url, {
            'reason': 'This review contains inappropriate content.'
        })

        # Check response
        self.assertRedirects(response, self.venue_reviews_url)

        # Check that the flag was created
        self.assertTrue(ReviewFlag.objects.filter(
            review=self.review,
            flagged_by=flagger,
            reason='This review contains inappropriate content.'
        ).exists())

        # Check that the review was flagged
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_flagged)

    def test_customer_review_history_view(self):
        """Test the customer review history view"""
        # Login as customer
        self.client.login(username='customer@example.com', password='testpass123')

        # Get the review history page
        response = self.client.get(self.customer_review_history_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/customer_review_history.html')
        self.assertIn(self.review, response.context['reviews'])

    def test_venue_reviews_view(self):
        """Test the venue reviews view"""
        # Get the venue reviews page
        response = self.client.get(self.venue_reviews_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/venue_reviews.html')
        self.assertEqual(response.context['venue'], self.venue)
        self.assertIn(self.review, response.context['reviews'])
        self.assertEqual(response.context['total_reviews'], 1)
        self.assertEqual(response.context['average_rating'], 4.0)


class ServiceProviderViewsTest(TestCase):
    """Test the service provider views in the review_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

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

        # Create category
        self.category = Category.objects.create(name="Spa")

        # Create venue
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Test Spa",
            category=self.category,
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city."
        )

        # Create a review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )

        # URLs
        self.provider_venue_reviews_url = reverse('review_app:provider_venue_reviews')
        self.provider_respond_to_review_url = reverse('review_app:provider_respond_to_review', args=[self.review.id])
        self.provider_review_summary_url = reverse('review_app:provider_review_summary')

    def test_provider_venue_reviews_view(self):
        """Test the provider venue reviews view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider venue reviews page
        response = self.client.get(self.provider_venue_reviews_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/provider/venue_reviews.html')
        self.assertIn(self.review, response.context['reviews'])

    def test_provider_venue_reviews_view_with_filters(self):
        """Test the provider venue reviews view with filters"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the provider venue reviews page with venue filter
        response = self.client.get(f"{self.provider_venue_reviews_url}?venue={self.venue.id}")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

        # Get the provider venue reviews page with rating filter
        response = self.client.get(f"{self.provider_venue_reviews_url}?rating=4")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

        # Get the provider venue reviews page with status filter
        response = self.client.get(f"{self.provider_venue_reviews_url}?status=all")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

    def test_provider_respond_to_review_view_get(self):
        """Test the provider respond to review view GET request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the respond to review page
        response = self.client.get(self.provider_respond_to_review_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/provider/respond_to_review.html')
        self.assertIsInstance(response.context['form'], ReviewResponseForm)
        self.assertEqual(response.context['review'], self.review)
        self.assertFalse(response.context['is_edit'])

    def test_provider_respond_to_review_view_post(self):
        """Test the provider respond to review view POST request"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Respond to the review
        response = self.client.post(self.provider_respond_to_review_url, {
            'response_text': 'Thank you for your kind review! We appreciate your feedback.'
        })

        # Check response
        self.assertRedirects(response, self.provider_venue_reviews_url)

        # Check that the response was created
        self.assertTrue(ReviewResponse.objects.filter(
            review=self.review,
            response_text='Thank you for your kind review! We appreciate your feedback.'
        ).exists())

    def test_provider_respond_to_review_view_edit(self):
        """Test editing an existing response"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Create a response
        response_obj = ReviewResponse.objects.create(
            review=self.review,
            response_text='Initial response.'
        )

        # Get the respond to review page (should be in edit mode)
        response = self.client.get(self.provider_respond_to_review_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_edit'])

        # Edit the response
        response = self.client.post(self.provider_respond_to_review_url, {
            'response_text': 'Updated response.'
        })

        # Check response
        self.assertRedirects(response, self.provider_venue_reviews_url)

        # Check that the response was updated
        response_obj.refresh_from_db()
        self.assertEqual(response_obj.response_text, 'Updated response.')

    def test_provider_review_summary_view(self):
        """Test the provider review summary view"""
        # Login as provider
        self.client.login(username='provider@example.com', password='testpass123')

        # Get the review summary page
        response = self.client.get(self.provider_review_summary_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/provider/review_summary.html')
        self.assertEqual(response.context['average_rating'], 4.0)
        self.assertEqual(response.context['total_reviews'], 1)


class AdminViewsTest(TestCase):
    """Test the admin views in the review_app"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

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
            is_staff=True,
            is_superuser=True
        )

        self.flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )

        # Create category
        self.category = Category.objects.create(name="Spa")

        # Create venue
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Test Spa",
            category=self.category,
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city."
        )

        # Create a review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )

        # Create a flag
        self.flag = ReviewFlag.objects.create(
            review=self.review,
            flagged_by=self.flagger,
            reason="This review contains inappropriate content"
        )

        # Mark the review as flagged
        self.review.is_flagged = True
        self.review.save()

        # URLs
        self.admin_review_list_url = reverse('review_app:admin_review_list')
        self.admin_review_detail_url = reverse('review_app:admin_review_detail', args=[self.review.id])
        self.admin_review_edit_url = reverse('review_app:admin_review_edit', args=[self.review.id])
        self.admin_review_delete_url = reverse('review_app:admin_review_delete', args=[self.review.id])
        self.admin_flagged_reviews_url = reverse('review_app:admin_flagged_reviews')
        self.admin_approve_flag_url = reverse('review_app:admin_approve_flag', args=[self.flag.id])
        self.admin_reject_flag_url = reverse('review_app:admin_reject_flag', args=[self.flag.id])

    def test_admin_review_list_view(self):
        """Test the admin review list view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin review list page
        response = self.client.get(self.admin_review_list_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/review_list.html')
        self.assertIn(self.review, response.context['reviews'])

    def test_admin_review_list_view_with_filters(self):
        """Test the admin review list view with filters"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin review list page with venue filter
        response = self.client.get(f"{self.admin_review_list_url}?venue={self.venue.id}")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

        # Get the admin review list page with rating filter
        response = self.client.get(f"{self.admin_review_list_url}?rating=4")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

        # Get the admin review list page with status filter
        response = self.client.get(f"{self.admin_review_list_url}?status=flagged")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])

    def test_admin_review_detail_view(self):
        """Test the admin review detail view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin review detail page
        response = self.client.get(self.admin_review_detail_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/review_detail.html')
        self.assertEqual(response.context['review'], self.review)
        self.assertIn(self.flag, response.context['flags'])

    def test_admin_review_edit_view_get(self):
        """Test the admin review edit view GET request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin review edit page
        response = self.client.get(self.admin_review_edit_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/review_edit.html')
        self.assertEqual(response.context['review'], self.review)

    def test_admin_review_edit_view_post(self):
        """Test the admin review edit view POST request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Edit the review
        response = self.client.post(self.admin_review_edit_url, {
            'rating': 3,
            'comment': 'Edited by admin.',
            'is_approved': True,
            'is_flagged': False
        })

        # Check response
        self.assertRedirects(response, self.admin_review_detail_url)

        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, 'Edited by admin.')
        self.assertTrue(self.review.is_approved)
        self.assertFalse(self.review.is_flagged)

    def test_admin_review_delete_view_get(self):
        """Test the admin review delete view GET request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin review delete page
        response = self.client.get(self.admin_review_delete_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/review_delete.html')
        self.assertEqual(response.context['review'], self.review)

    def test_admin_review_delete_view_post(self):
        """Test the admin review delete view POST request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Delete the review
        response = self.client.post(self.admin_review_delete_url)

        # Check response
        self.assertRedirects(response, self.admin_review_list_url)

        # Check that the review was deleted
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_admin_flagged_reviews_view(self):
        """Test the admin flagged reviews view"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin flagged reviews page
        response = self.client.get(self.admin_flagged_reviews_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/flagged_reviews.html')
        self.assertIn(self.flag, response.context['flags'])

    def test_admin_approve_flag_view_get(self):
        """Test the admin approve flag view GET request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin approve flag page
        response = self.client.get(self.admin_approve_flag_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/approve_flag.html')
        self.assertEqual(response.context['flag'], self.flag)

    def test_admin_approve_flag_view_post(self):
        """Test the admin approve flag view POST request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Approve the flag
        response = self.client.post(self.admin_approve_flag_url)

        # Check response
        self.assertRedirects(response, self.admin_flagged_reviews_url)

        # Check that the flag was approved
        self.flag.refresh_from_db()
        self.assertEqual(self.flag.status, 'approved')
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)

        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_approved)

    def test_admin_reject_flag_view_get(self):
        """Test the admin reject flag view GET request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Get the admin reject flag page
        response = self.client.get(self.admin_reject_flag_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_app/admin/reject_flag.html')
        self.assertEqual(response.context['flag'], self.flag)

    def test_admin_reject_flag_view_post(self):
        """Test the admin reject flag view POST request"""
        # Login as admin
        self.client.login(username='admin@example.com', password='testpass123')

        # Reject the flag
        response = self.client.post(self.admin_reject_flag_url)

        # Check response
        self.assertRedirects(response, self.admin_flagged_reviews_url)

        # Check that the flag was rejected
        self.flag.refresh_from_db()
        self.assertEqual(self.flag.status, 'rejected')
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)

        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_flagged)