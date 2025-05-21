from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from venues_app.models import Venue
from booking_cart_app.models import Booking
from .models import Review, ReviewResponse, ReviewFlag

User = get_user_model()


class ReviewModelTest(TestCase):
    """Test the Review model"""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            is_customer=True
        )
        
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpassword',
            is_service_provider=True
        )
        
        # Create test venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.provider,
            # Add other required fields
        )
        
        # Create test booking
        self.booking = Booking.objects.create(
            user=self.customer,
            venue=self.venue,
            status='completed',
            # Add other required fields
        )
        
        # Create test review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment='This is a test review.'
        )
    
    def test_review_creation(self):
        """Test review is created correctly"""
        self.assertEqual(self.review.venue, self.venue)
        self.assertEqual(self.review.user, self.customer)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'This is a test review.')
        self.assertTrue(self.review.is_approved)
        self.assertFalse(self.review.is_flagged)
    
    def test_review_str(self):
        """Test the string representation of review"""
        expected_str = f"{self.customer.email} - {self.venue.name} - 4 stars"
        self.assertEqual(str(self.review), expected_str)
    
    def test_get_response(self):
        """Test get_response method returns None when no response exists"""
        self.assertIsNone(self.review.get_response())
        
        # Create a response and test again
        response = ReviewResponse.objects.create(
            review=self.review,
            response_text='Thank you for your review.'
        )
        self.assertEqual(self.review.get_response(), response)
    
    def test_flag_review(self):
        """Test flagging a review"""
        # Create another user to flag the review
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpassword'
        )
        
        # Flag the review
        result = self.review.flag(flagger, 'This review is inappropriate.')
        
        # Check the result
        self.assertTrue(result)
        self.assertTrue(self.review.is_flagged)
        
        # Check that a flag was created
        flag = ReviewFlag.objects.get(review=self.review)
        self.assertEqual(flag.flagged_by, flagger)
        self.assertEqual(flag.reason, 'This review is inappropriate.')
        self.assertEqual(flag.status, 'pending')
    
    def test_cannot_flag_own_review(self):
        """Test that users cannot flag their own reviews"""
        # Try to flag own review
        result = self.review.flag(self.customer, 'This is my own review.')
        
        # Check the result
        self.assertFalse(result)
        self.assertFalse(self.review.is_flagged)
        
        # Check that no flag was created
        self.assertEqual(ReviewFlag.objects.count(), 0)


class ReviewResponseModelTest(TestCase):
    """Test the ReviewResponse model"""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            is_customer=True
        )
        
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpassword',
            is_service_provider=True
        )
        
        # Create test venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.provider,
            # Add other required fields
        )
        
        # Create test review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment='This is a test review.'
        )
        
        # Create test response
        self.response = ReviewResponse.objects.create(
            review=self.review,
            response_text='Thank you for your review.'
        )
    
    def test_response_creation(self):
        """Test response is created correctly"""
        self.assertEqual(self.response.review, self.review)
        self.assertEqual(self.response.response_text, 'Thank you for your review.')
    
    def test_response_str(self):
        """Test the string representation of response"""
        expected_str = f"Response to {self.review}"
        self.assertEqual(str(self.response), expected_str)


class ReviewFlagModelTest(TestCase):
    """Test the ReviewFlag model"""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            is_customer=True
        )
        
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='testpassword',
            is_service_provider=True
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpassword',
            is_staff=True
        )
        
        # Create test venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.provider,
            # Add other required fields
        )
        
        # Create test review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment='This is a test review.'
        )
        
        # Create test flag
        self.flag = ReviewFlag.objects.create(
            review=self.review,
            flagged_by=self.provider,
            reason='This review is inappropriate.'
        )
    
    def test_flag_creation(self):
        """Test flag is created correctly"""
        self.assertEqual(self.flag.review, self.review)
        self.assertEqual(self.flag.flagged_by, self.provider)
        self.assertEqual(self.flag.reason, 'This review is inappropriate.')
        self.assertEqual(self.flag.status, 'pending')
        self.assertIsNone(self.flag.reviewed_at)
        self.assertIsNone(self.flag.reviewed_by)
    
    def test_flag_str(self):
        """Test the string representation of flag"""
        expected_str = f"Flag on {self.review} by {self.provider.email}"
        self.assertEqual(str(self.flag), expected_str)
    
    def test_approve_flag(self):
        """Test approving a flag"""
        self.flag.approve(self.admin)
        
        # Check flag status
        self.assertEqual(self.flag.status, 'approved')
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)
        
        # Check review status
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_approved)
    
    def test_reject_flag(self):
        """Test rejecting a flag"""
        self.flag.reject(self.admin)
        
        # Check flag status
        self.assertEqual(self.flag.status, 'rejected')
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)
        
        # Check review status
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_approved)
        self.assertFalse(self.review.is_flagged)  # Flag should be removed
