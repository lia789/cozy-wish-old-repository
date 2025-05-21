from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from venues_app.models import Category, Venue
from review_app.models import Review, ReviewResponse, ReviewFlag
from review_app.forms import (
    ReviewForm, StarRatingForm, ReviewResponseForm, 
    ReviewFlagForm, AdminReviewForm
)

User = get_user_model()

class ReviewFormTest(TestCase):
    """Test the ReviewForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.'
        }
    
    def test_review_form_valid(self):
        """Test that the form is valid with valid data"""
        form = ReviewForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_review_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Test missing rating
        invalid_data = self.form_data.copy()
        invalid_data.pop('rating')
        form = ReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
        # Test missing comment
        invalid_data = self.form_data.copy()
        invalid_data.pop('comment')
        form = ReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)
    
    def test_review_form_invalid_rating(self):
        """Test that the form is invalid when rating is out of range"""
        # Test with rating too low
        invalid_data = self.form_data.copy()
        invalid_data['rating'] = 0
        form = ReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
        # Test with rating too high
        invalid_data = self.form_data.copy()
        invalid_data['rating'] = 6
        form = ReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)


class StarRatingFormTest(TestCase):
    """Test the StarRatingForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.'
        }
    
    def test_star_rating_form_valid(self):
        """Test that the form is valid with valid data"""
        form = StarRatingForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_star_rating_form_widget(self):
        """Test that the form uses a hidden input for rating"""
        form = StarRatingForm()
        self.assertEqual(form.fields['rating'].widget.__class__.__name__, 'HiddenInput')
        self.assertEqual(form.fields['rating'].widget.attrs['id'], 'star-rating-input')


class ReviewResponseFormTest(TestCase):
    """Test the ReviewResponseForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'response_text': 'Thank you for your kind review! We appreciate your feedback.'
        }
    
    def test_review_response_form_valid(self):
        """Test that the form is valid with valid data"""
        form = ReviewResponseForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_review_response_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Test missing response_text
        invalid_data = {}
        form = ReviewResponseForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('response_text', form.errors)


class ReviewFlagFormTest(TestCase):
    """Test the ReviewFlagForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'reason': 'This review contains inappropriate content.'
        }
    
    def test_review_flag_form_valid(self):
        """Test that the form is valid with valid data"""
        form = ReviewFlagForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_review_flag_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Test missing reason
        invalid_data = {}
        form = ReviewFlagForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('reason', form.errors)


class AdminReviewFormTest(TestCase):
    """Test the AdminReviewForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'rating': 4,
            'comment': 'Great experience! The staff was very friendly and professional.',
            'is_approved': True,
            'is_flagged': False
        }
    
    def test_admin_review_form_valid(self):
        """Test that the form is valid with valid data"""
        form = AdminReviewForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_admin_review_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing"""
        # Test missing rating
        invalid_data = self.form_data.copy()
        invalid_data.pop('rating')
        form = AdminReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
        # Test missing comment
        invalid_data = self.form_data.copy()
        invalid_data.pop('comment')
        form = AdminReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)
    
    def test_admin_review_form_invalid_rating(self):
        """Test that the form is invalid when rating is out of range"""
        # Test with rating too low
        invalid_data = self.form_data.copy()
        invalid_data['rating'] = 0
        form = AdminReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
        # Test with rating too high
        invalid_data = self.form_data.copy()
        invalid_data['rating'] = 6
        form = AdminReviewForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
