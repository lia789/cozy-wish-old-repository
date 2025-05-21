from django.test import TestCase
from django.urls import reverse, resolve
from venues_app.views import (
    # Public views
    home_view, venue_list_view, venue_detail_view, service_detail_view, submit_review_view,

    # Provider views
    provider_venue_detail_view, create_venue_view, edit_venue_view,
    delete_venue_view, create_service_view, edit_service_view, delete_service_view,
    service_create_redirect,

    # Admin views
    admin_venue_list_view, admin_venue_detail_view, admin_venue_approval_view
)


class VenuesAppUrlsTest(TestCase):
    """Test the URLs for the venues_app."""

    def test_home_url(self):
        """Test the home URL."""
        url = reverse('venues_app:home')
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, home_view)

    def test_venue_list_url(self):
        """Test the venue list URL."""
        url = reverse('venues_app:venue_list')
        self.assertEqual(url, '/venues/')
        self.assertEqual(resolve(url).func, venue_list_view)

    def test_venue_search_url(self):
        """Test the venue search URL."""
        url = reverse('venues_app:venue_search')
        self.assertEqual(url, '/venues/search/')
        self.assertEqual(resolve(url).func, venue_list_view)

    def test_venue_detail_url(self):
        """Test the venue detail URL."""
        url = reverse('venues_app:venue_detail', args=['test-venue'])
        self.assertEqual(url, '/venues/test-venue/')
        self.assertEqual(resolve(url).func, venue_detail_view)

    def test_service_detail_url(self):
        """Test the service detail URL."""
        url = reverse('venues_app:service_detail', args=['test-venue', 'test-service'])
        self.assertEqual(url, '/venues/test-venue/services/test-service/')
        self.assertEqual(resolve(url).func, service_detail_view)

    def test_submit_review_url(self):
        """Test the submit review URL."""
        url = reverse('venues_app:submit_review', args=['test-venue'])
        self.assertEqual(url, '/venues/test-venue/review/')
        self.assertEqual(resolve(url).func, submit_review_view)


class ProviderUrlsTest(TestCase):
    """Test the provider URLs for the venues_app."""



    def test_provider_venue_detail_url(self):
        """Test the provider venue detail URL."""
        url = reverse('venues_app:provider_venue_detail', args=[1])
        self.assertEqual(url, '/provider/venues/1/')
        self.assertEqual(resolve(url).func, provider_venue_detail_view)

    def test_create_venue_url(self):
        """Test the create venue URL."""
        url = reverse('venues_app:create_venue')
        self.assertEqual(url, '/provider/venues/create/')
        self.assertEqual(resolve(url).func, create_venue_view)

    def test_edit_venue_url(self):
        """Test the edit venue URL."""
        url = reverse('venues_app:edit_venue', args=[1])
        self.assertEqual(url, '/provider/venues/1/edit/')
        self.assertEqual(resolve(url).func, edit_venue_view)

    def test_delete_venue_url(self):
        """Test the delete venue URL."""
        url = reverse('venues_app:delete_venue', args=[1])
        self.assertEqual(url, '/provider/venues/1/delete/')
        self.assertEqual(resolve(url).func, delete_venue_view)

    def test_create_service_url(self):
        """Test the create service URL."""
        url = reverse('venues_app:create_service', args=[1])
        self.assertEqual(url, '/provider/venues/1/services/create/')
        self.assertEqual(resolve(url).func, create_service_view)

    def test_edit_service_url(self):
        """Test the edit service URL."""
        url = reverse('venues_app:edit_service', args=[1, 1])
        self.assertEqual(url, '/provider/venues/1/services/1/edit/')
        self.assertEqual(resolve(url).func, edit_service_view)

    def test_delete_service_url(self):
        """Test the delete service URL."""
        url = reverse('venues_app:delete_service', args=[1, 1])
        self.assertEqual(url, '/provider/venues/1/services/1/delete/')
        self.assertEqual(resolve(url).func, delete_service_view)

    def test_service_create_redirect_url(self):
        """Test the service create redirect URL."""
        url = reverse('venues_app:service_create')
        self.assertEqual(url, '/provider/services/create/')
        self.assertEqual(resolve(url).func, service_create_redirect)


class AdminUrlsTest(TestCase):
    """Test the admin URLs for the venues_app."""

    def test_admin_venue_list_url(self):
        """Test the admin venue list URL."""
        url = reverse('venues_app:admin_venue_list')
        self.assertEqual(url, '/venue-admin/venues/')
        self.assertEqual(resolve(url).func, admin_venue_list_view)

    def test_admin_venue_detail_url(self):
        """Test the admin venue detail URL."""
        url = reverse('venues_app:admin_venue_detail', args=[1])
        self.assertEqual(url, '/venue-admin/venues/1/')
        self.assertEqual(resolve(url).func, admin_venue_detail_view)

    def test_admin_venue_approval_url(self):
        """Test the admin venue approval URL."""
        url = reverse('venues_app:admin_venue_approval', args=[1])
        self.assertEqual(url, '/venue-admin/venues/1/approval/')
        self.assertEqual(resolve(url).func, admin_venue_approval_view)
