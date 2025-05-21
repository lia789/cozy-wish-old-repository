from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from venues_app.models import Category, Venue, Service
from booking_cart_app.models import Booking, BookingItem
from review_app.models import Review, ReviewResponse, ReviewFlag

User = get_user_model()

class ReviewIntegrationTest(TestCase):
    """Integration tests for the review_app"""
    
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
        
        # Create service
        self.service = Service.objects.create(
            venue=self.venue,
            title="Test Service",
            short_description="A test service",
            price=100.00,
            duration=60,
            is_active=True
        )
        
        # Create a completed booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            status='completed',
            booking_date=timezone.now() - timedelta(days=7),
            total_price=100.00
        )
        
        self.booking_item = BookingItem.objects.create(
            booking=self.booking,
            service=self.service,
            price=100.00,
            quantity=1
        )
    
    def test_full_review_lifecycle(self):
        """Test the full lifecycle of a review from creation to deletion"""
        # 1. Customer submits a review
        self.client.login(username='customer@example.com', password='testpass123')
        
        submit_review_url = reverse('review_app:submit_review', args=[self.venue.id])
        response = self.client.post(submit_review_url, {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.'
        })
        
        # Check that the review was created
        self.assertTrue(Review.objects.filter(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment='Great experience! The staff was very friendly and professional.'
        ).exists())
        
        review = Review.objects.get(venue=self.venue, user=self.customer)
        
        # 2. Customer edits the review
        edit_review_url = reverse('review_app:edit_review', args=[review.id])
        response = self.client.post(edit_review_url, {
            'rating': 5,
            'comment': 'Updated review: Excellent service and atmosphere!'
        })
        
        # Check that the review was updated
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Updated review: Excellent service and atmosphere!')
        
        # 3. Provider responds to the review
        self.client.logout()
        self.client.login(username='provider@example.com', password='testpass123')
        
        respond_to_review_url = reverse('review_app:provider_respond_to_review', args=[review.id])
        response = self.client.post(respond_to_review_url, {
            'response_text': 'Thank you for your kind review! We appreciate your feedback.'
        })
        
        # Check that the response was created
        self.assertTrue(ReviewResponse.objects.filter(
            review=review,
            response_text='Thank you for your kind review! We appreciate your feedback.'
        ).exists())
        
        # 4. Another customer flags the review
        self.client.logout()
        
        # Create another customer
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )
        
        self.client.login(username='flagger@example.com', password='testpass123')
        
        flag_review_url = reverse('review_app:flag_review', args=[review.id])
        response = self.client.post(flag_review_url, {
            'reason': 'This review contains inappropriate content.'
        })
        
        # Check that the flag was created
        self.assertTrue(ReviewFlag.objects.filter(
            review=review,
            flagged_by=flagger,
            reason='This review contains inappropriate content.'
        ).exists())
        
        flag = ReviewFlag.objects.get(review=review, flagged_by=flagger)
        
        # Check that the review was flagged
        review.refresh_from_db()
        self.assertTrue(review.is_flagged)
        
        # 5. Admin approves the flag
        self.client.logout()
        self.client.login(username='admin@example.com', password='testpass123')
        
        approve_flag_url = reverse('review_app:admin_approve_flag', args=[flag.id])
        response = self.client.post(approve_flag_url)
        
        # Check that the flag was approved
        flag.refresh_from_db()
        self.assertEqual(flag.status, 'approved')
        
        # Check that the review was updated
        review.refresh_from_db()
        self.assertFalse(review.is_approved)
        
        # 6. Admin edits the review
        edit_review_url = reverse('review_app:admin_review_edit', args=[review.id])
        response = self.client.post(edit_review_url, {
            'rating': 4,
            'comment': 'Edited by admin: Appropriate content.',
            'is_approved': True,
            'is_flagged': False
        })
        
        # Check that the review was updated
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Edited by admin: Appropriate content.')
        self.assertTrue(review.is_approved)
        self.assertFalse(review.is_flagged)
        
        # 7. Admin deletes the review
        delete_review_url = reverse('review_app:admin_review_delete', args=[review.id])
        response = self.client.post(delete_review_url)
        
        # Check that the review was deleted
        self.assertFalse(Review.objects.filter(id=review.id).exists())
    
    def test_review_flagging_and_rejection(self):
        """Test the review flagging and rejection process"""
        # 1. Customer submits a review
        self.client.login(username='customer@example.com', password='testpass123')
        
        submit_review_url = reverse('review_app:submit_review', args=[self.venue.id])
        response = self.client.post(submit_review_url, {
            'rating': 2,
            'comment': 'Not a great experience.'
        })
        
        review = Review.objects.get(venue=self.venue, user=self.customer)
        
        # 2. Another customer flags the review
        self.client.logout()
        
        # Create another customer
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )
        
        self.client.login(username='flagger@example.com', password='testpass123')
        
        flag_review_url = reverse('review_app:flag_review', args=[review.id])
        response = self.client.post(flag_review_url, {
            'reason': 'This review is unfair.'
        })
        
        flag = ReviewFlag.objects.get(review=review, flagged_by=flagger)
        
        # 3. Admin rejects the flag
        self.client.logout()
        self.client.login(username='admin@example.com', password='testpass123')
        
        reject_flag_url = reverse('review_app:admin_reject_flag', args=[flag.id])
        response = self.client.post(reject_flag_url)
        
        # Check that the flag was rejected
        flag.refresh_from_db()
        self.assertEqual(flag.status, 'rejected')
        
        # Check that the review is still visible
        review.refresh_from_db()
        self.assertTrue(review.is_approved)
        self.assertFalse(review.is_flagged)
        
        # 4. Provider responds to the negative review
        self.client.logout()
        self.client.login(username='provider@example.com', password='testpass123')
        
        respond_to_review_url = reverse('review_app:provider_respond_to_review', args=[review.id])
        response = self.client.post(respond_to_review_url, {
            'response_text': 'We apologize for your experience. Please contact us directly so we can make it right.'
        })
        
        # Check that the response was created
        self.assertTrue(ReviewResponse.objects.filter(
            review=review,
            response_text='We apologize for your experience. Please contact us directly so we can make it right.'
        ).exists())
