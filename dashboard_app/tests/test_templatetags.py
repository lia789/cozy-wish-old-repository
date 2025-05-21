from django.test import TestCase
from dashboard_app.templatetags.dashboard_tags import (
    get_item, filter_by_rating, filter_by_status, filter_with_response,
    percentage, format_currency, get_status_badge_class
)


class DashboardTagsTest(TestCase):
    """Test the dashboard template tags"""
    
    def test_get_item(self):
        """Test the get_item template tag"""
        # Test with dictionary
        dictionary = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(get_item(dictionary, 'key1'), 'value1')
        self.assertEqual(get_item(dictionary, 'key2'), 'value2')
        self.assertIsNone(get_item(dictionary, 'nonexistent_key'))
        
        # Test with list
        list_obj = ['item1', 'item2', 'item3']
        self.assertEqual(get_item(list_obj, 0), 'item1')
        self.assertEqual(get_item(list_obj, 1), 'item2')
        self.assertIsNone(get_item(list_obj, 10))  # Out of range
    
    def test_filter_by_rating(self):
        """Test the filter_by_rating template tag"""
        # Create mock reviews
        reviews = [
            {'rating': 5, 'comment': 'Excellent'},
            {'rating': 4, 'comment': 'Good'},
            {'rating': 3, 'comment': 'Average'},
            {'rating': 5, 'comment': 'Amazing'},
            {'rating': 2, 'comment': 'Poor'},
        ]
        
        # Filter by rating
        five_star_reviews = filter_by_rating(reviews, 5)
        four_star_reviews = filter_by_rating(reviews, 4)
        three_star_reviews = filter_by_rating(reviews, 3)
        two_star_reviews = filter_by_rating(reviews, 2)
        one_star_reviews = filter_by_rating(reviews, 1)
        
        # Check results
        self.assertEqual(len(five_star_reviews), 2)
        self.assertEqual(len(four_star_reviews), 1)
        self.assertEqual(len(three_star_reviews), 1)
        self.assertEqual(len(two_star_reviews), 1)
        self.assertEqual(len(one_star_reviews), 0)
        
        # Check content
        self.assertEqual(five_star_reviews[0]['comment'], 'Excellent')
        self.assertEqual(five_star_reviews[1]['comment'], 'Amazing')
        self.assertEqual(four_star_reviews[0]['comment'], 'Good')
    
    def test_filter_by_status(self):
        """Test the filter_by_status template tag"""
        # Create mock reviews
        reviews = [
            {'is_approved': True, 'is_flagged': False, 'comment': 'Approved'},
            {'is_approved': False, 'is_flagged': True, 'comment': 'Flagged'},
            {'is_approved': False, 'is_flagged': False, 'comment': 'Pending'},
            {'is_approved': True, 'is_flagged': False, 'comment': 'Approved 2'},
        ]
        
        # Filter by status
        approved_reviews = filter_by_status(reviews, 'approved')
        flagged_reviews = filter_by_status(reviews, 'flagged')
        pending_reviews = filter_by_status(reviews, 'pending')
        
        # Check results
        self.assertEqual(len(approved_reviews), 2)
        self.assertEqual(len(flagged_reviews), 1)
        self.assertEqual(len(pending_reviews), 1)
        
        # Check content
        self.assertEqual(approved_reviews[0]['comment'], 'Approved')
        self.assertEqual(approved_reviews[1]['comment'], 'Approved 2')
        self.assertEqual(flagged_reviews[0]['comment'], 'Flagged')
        self.assertEqual(pending_reviews[0]['comment'], 'Pending')
    
    def test_filter_with_response(self):
        """Test the filter_with_response template tag"""
        # Create mock reviews
        reviews = [
            {'response': {'text': 'Thank you'}, 'comment': 'With response'},
            {'response': None, 'comment': 'No response'},
            {'response': {'text': 'We appreciate your feedback'}, 'comment': 'With response 2'},
            {'comment': 'No response attribute'},
        ]
        
        # Filter reviews with response
        with_response = filter_with_response(reviews)
        
        # Check results
        self.assertEqual(len(with_response), 2)
        
        # Check content
        self.assertEqual(with_response[0]['comment'], 'With response')
        self.assertEqual(with_response[1]['comment'], 'With response 2')
    
    def test_percentage(self):
        """Test the percentage template tag"""
        # Test with various inputs
        self.assertEqual(percentage(50, 100), 50.0)
        self.assertEqual(percentage(25, 50), 50.0)
        self.assertEqual(percentage(0, 100), 0.0)
        self.assertEqual(percentage(100, 100), 100.0)
        
        # Test with zero denominator
        self.assertEqual(percentage(50, 0), 0.0)
    
    def test_format_currency(self):
        """Test the format_currency template tag"""
        # Test with various inputs
        self.assertEqual(format_currency(100), '$100.00')
        self.assertEqual(format_currency(99.99), '$99.99')
        self.assertEqual(format_currency(0), '$0.00')
        self.assertEqual(format_currency(1234.56), '$1234.56')
        
        # Test with None
        self.assertEqual(format_currency(None), '$0.00')
    
    def test_get_status_badge_class(self):
        """Test the get_status_badge_class template tag"""
        # Test with various statuses
        self.assertEqual(get_status_badge_class('pending'), 'bg-warning')
        self.assertEqual(get_status_badge_class('confirmed'), 'bg-success')
        self.assertEqual(get_status_badge_class('cancelled'), 'bg-danger')
        self.assertEqual(get_status_badge_class('completed'), 'bg-info')
        
        # Test with unknown status
        self.assertEqual(get_status_badge_class('unknown'), 'bg-secondary')
