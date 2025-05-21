from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from venues_app.models import Category, Venue
from review_app.models import Review, ReviewResponse, ReviewFlag

User = get_user_model()

class ReviewModelTest(TestCase):
    """Test the Review model"""
    
    def setUp(self):
        """Set up test data"""
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
        
        # Create review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )
    
    def test_review_creation(self):
        """Test creating a review is successful"""
        self.assertEqual(self.review.venue, self.venue)
        self.assertEqual(self.review.user, self.customer)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, "Great experience! The staff was very friendly and professional.")
        self.assertTrue(self.review.is_approved)
        self.assertFalse(self.review.is_flagged)
        
        # Test string representation
        expected_str = f"{self.customer.email} - {self.venue.name} - 4 stars"
        self.assertEqual(str(self.review), expected_str)
    
    def test_review_rating_validation(self):
        """Test review rating validation"""
        # Test rating too low
        with self.assertRaises(ValidationError):
            invalid_review = Review(
                venue=self.venue,
                user=self.customer,
                rating=0,
                comment="Invalid rating"
            )
            invalid_review.full_clean()
        
        # Test rating too high
        with self.assertRaises(ValidationError):
            invalid_review = Review(
                venue=self.venue,
                user=self.customer,
                rating=6,
                comment="Invalid rating"
            )
            invalid_review.full_clean()
    
    def test_review_unique_constraint(self):
        """Test that a user can only review a venue once"""
        # Try to create a duplicate review
        with self.assertRaises(Exception):
            duplicate_review = Review.objects.create(
                venue=self.venue,
                user=self.customer,
                rating=5,
                comment="This is a duplicate review"
            )
    
    def test_get_response_method(self):
        """Test the get_response method"""
        # Initially, there should be no response
        self.assertIsNone(self.review.get_response())
        
        # Create a response
        response = ReviewResponse.objects.create(
            review=self.review,
            response_text="Thank you for your review!"
        )
        
        # Now get_response should return the response
        self.assertEqual(self.review.get_response(), response)
    
    def test_flag_method(self):
        """Test the flag method"""
        # Create another customer to flag the review
        flagger = User.objects.create_user(
            email='flagger@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Flag the review
        result = self.review.flag(flagger, "This review contains inappropriate content")
        
        # Check that the flag was created
        self.assertTrue(result)
        self.assertTrue(self.review.is_flagged)
        
        # Check that the flag exists in the database
        flag = ReviewFlag.objects.get(review=self.review, flagged_by=flagger)
        self.assertEqual(flag.reason, "This review contains inappropriate content")
        self.assertEqual(flag.status, "pending")
        
        # Test that a user can't flag their own review
        result = self.review.flag(self.customer, "Trying to flag my own review")
        self.assertFalse(result)
        
        # Check that no new flag was created
        self.assertEqual(ReviewFlag.objects.filter(review=self.review).count(), 1)


class ReviewResponseModelTest(TestCase):
    """Test the ReviewResponse model"""
    
    def setUp(self):
        """Set up test data"""
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
        
        # Create review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )
        
        # Create response
        self.response = ReviewResponse.objects.create(
            review=self.review,
            response_text="Thank you for your kind review! We're glad you enjoyed your experience."
        )
    
    def test_response_creation(self):
        """Test creating a response is successful"""
        self.assertEqual(self.response.review, self.review)
        self.assertEqual(
            self.response.response_text,
            "Thank you for your kind review! We're glad you enjoyed your experience."
        )
        
        # Test string representation
        expected_str = f"Response to {self.review}"
        self.assertEqual(str(self.response), expected_str)
    
    def test_one_to_one_relationship(self):
        """Test that a review can only have one response"""
        # Try to create a second response for the same review
        with self.assertRaises(Exception):
            second_response = ReviewResponse.objects.create(
                review=self.review,
                response_text="This is a second response"
            )


class ReviewFlagModelTest(TestCase):
    """Test the ReviewFlag model"""
    
    def setUp(self):
        """Set up test data"""
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
        
        # Create review
        self.review = Review.objects.create(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )
        
        # Create flag
        self.flag = ReviewFlag.objects.create(
            review=self.review,
            flagged_by=self.flagger,
            reason="This review contains inappropriate content"
        )
    
    def test_flag_creation(self):
        """Test creating a flag is successful"""
        self.assertEqual(self.flag.review, self.review)
        self.assertEqual(self.flag.flagged_by, self.flagger)
        self.assertEqual(self.flag.reason, "This review contains inappropriate content")
        self.assertEqual(self.flag.status, "pending")
        self.assertIsNone(self.flag.reviewed_at)
        self.assertIsNone(self.flag.reviewed_by)
        
        # Test string representation
        expected_str = f"Flag on {self.review} by {self.flagger.email}"
        self.assertEqual(str(self.flag), expected_str)
    
    def test_approve_method(self):
        """Test the approve method"""
        # Approve the flag
        result = self.flag.approve(self.admin)
        
        # Check that the flag was approved
        self.assertTrue(result)
        self.assertEqual(self.flag.status, "approved")
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)
        
        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_approved)
    
    def test_reject_method(self):
        """Test the reject method"""
        # Reject the flag
        result = self.flag.reject(self.admin)
        
        # Check that the flag was rejected
        self.assertTrue(result)
        self.assertEqual(self.flag.status, "rejected")
        self.assertIsNotNone(self.flag.reviewed_at)
        self.assertEqual(self.flag.reviewed_by, self.admin)
        
        # Check that the review was updated
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_flagged)
    
    def test_multiple_flags(self):
        """Test handling multiple flags for the same review"""
        # Create a second flagger
        flagger2 = User.objects.create_user(
            email='flagger2@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create a second flag
        flag2 = ReviewFlag.objects.create(
            review=self.review,
            flagged_by=flagger2,
            reason="This review is offensive"
        )
        
        # Reject the first flag
        self.flag.reject(self.admin)
        
        # The review should still be flagged because of the second flag
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_flagged)
        
        # Reject the second flag
        flag2.reject(self.admin)
        
        # Now the review should not be flagged
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_flagged)
