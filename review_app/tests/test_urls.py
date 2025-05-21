from django.test import SimpleTestCase
from django.urls import reverse, resolve
from review_app import views

class UrlsTest(SimpleTestCase):
    """Test the URLs for the review_app"""
    
    # Customer URLs
    def test_submit_review_url(self):
        """Test the submit review URL"""
        url = reverse('review_app:submit_review', args=[1])
        self.assertEqual(url, '/reviews/submit/1/')
        self.assertEqual(resolve(url).func, views.submit_review_view)
    
    def test_edit_review_url(self):
        """Test the edit review URL"""
        url = reverse('review_app:edit_review', args=[1])
        self.assertEqual(url, '/reviews/edit/1/')
        self.assertEqual(resolve(url).func, views.edit_review_view)
    
    def test_flag_review_url(self):
        """Test the flag review URL"""
        url = reverse('review_app:flag_review', args=[1])
        self.assertEqual(url, '/reviews/flag/1/')
        self.assertEqual(resolve(url).func, views.flag_review_view)
    
    def test_customer_review_history_url(self):
        """Test the customer review history URL"""
        url = reverse('review_app:customer_review_history')
        self.assertEqual(url, '/reviews/history/')
        self.assertEqual(resolve(url).func, views.customer_review_history_view)
    
    # Service Provider URLs
    def test_provider_venue_reviews_url(self):
        """Test the provider venue reviews URL"""
        url = reverse('review_app:provider_venue_reviews')
        self.assertEqual(url, '/reviews/provider/reviews/')
        self.assertEqual(resolve(url).func, views.provider_venue_reviews_view)
    
    def test_provider_respond_to_review_url(self):
        """Test the provider respond to review URL"""
        url = reverse('review_app:provider_respond_to_review', args=[1])
        self.assertEqual(url, '/reviews/provider/respond/1/')
        self.assertEqual(resolve(url).func, views.provider_respond_to_review_view)
    
    def test_provider_review_summary_url(self):
        """Test the provider review summary URL"""
        url = reverse('review_app:provider_review_summary')
        self.assertEqual(url, '/reviews/provider/summary/')
        self.assertEqual(resolve(url).func, views.provider_review_summary_view)
    
    # Admin URLs
    def test_admin_review_list_url(self):
        """Test the admin review list URL"""
        url = reverse('review_app:admin_review_list')
        self.assertEqual(url, '/reviews/admin/reviews/')
        self.assertEqual(resolve(url).func, views.admin_review_list_view)
    
    def test_admin_review_detail_url(self):
        """Test the admin review detail URL"""
        url = reverse('review_app:admin_review_detail', args=[1])
        self.assertEqual(url, '/reviews/admin/reviews/1/')
        self.assertEqual(resolve(url).func, views.admin_review_detail_view)
    
    def test_admin_review_edit_url(self):
        """Test the admin review edit URL"""
        url = reverse('review_app:admin_review_edit', args=[1])
        self.assertEqual(url, '/reviews/admin/reviews/1/edit/')
        self.assertEqual(resolve(url).func, views.admin_review_edit_view)
    
    def test_admin_review_delete_url(self):
        """Test the admin review delete URL"""
        url = reverse('review_app:admin_review_delete', args=[1])
        self.assertEqual(url, '/reviews/admin/reviews/1/delete/')
        self.assertEqual(resolve(url).func, views.admin_review_delete_view)
    
    def test_admin_flagged_reviews_url(self):
        """Test the admin flagged reviews URL"""
        url = reverse('review_app:admin_flagged_reviews')
        self.assertEqual(url, '/reviews/admin/flagged/')
        self.assertEqual(resolve(url).func, views.admin_flagged_reviews_view)
    
    def test_admin_approve_flag_url(self):
        """Test the admin approve flag URL"""
        url = reverse('review_app:admin_approve_flag', args=[1])
        self.assertEqual(url, '/reviews/admin/flags/1/approve/')
        self.assertEqual(resolve(url).func, views.admin_approve_flag_view)
    
    def test_admin_reject_flag_url(self):
        """Test the admin reject flag URL"""
        url = reverse('review_app:admin_reject_flag', args=[1])
        self.assertEqual(url, '/reviews/admin/flags/1/reject/')
        self.assertEqual(resolve(url).func, views.admin_reject_flag_view)
    
    # Public URLs
    def test_venue_reviews_url(self):
        """Test the venue reviews URL"""
        url = reverse('review_app:venue_reviews', args=[1])
        self.assertEqual(url, '/reviews/venue/1/')
        self.assertEqual(resolve(url).func, views.venue_reviews_view)
