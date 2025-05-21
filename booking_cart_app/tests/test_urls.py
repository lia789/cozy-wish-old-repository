from django.test import SimpleTestCase
from django.urls import reverse, resolve
from booking_cart_app.views import (
    # Customer views
    add_to_cart, cart, update_cart_item, remove_from_cart, checkout, booking_confirmation,
    booking_list, booking_detail, cancel_booking,
    
    # Provider views
    provider_booking_list, provider_booking_detail, provider_update_booking_status,
    provider_service_availability, provider_bulk_availability, provider_update_availability,
    provider_delete_availability,
    
    # Admin views
    admin_booking_list, admin_booking_detail, admin_update_booking_status, admin_booking_analytics
)

class UrlsTest(SimpleTestCase):
    """Test the URLs in the booking_cart_app"""
    
    def test_add_to_cart_url(self):
        """Test the add_to_cart URL"""
        url = reverse('booking_cart_app:add_to_cart', args=[1])
        self.assertEqual(resolve(url).func, add_to_cart)
    
    def test_cart_url(self):
        """Test the cart URL"""
        url = reverse('booking_cart_app:cart')
        self.assertEqual(resolve(url).func, cart)
    
    def test_update_cart_item_url(self):
        """Test the update_cart_item URL"""
        url = reverse('booking_cart_app:update_cart_item', args=[1])
        self.assertEqual(resolve(url).func, update_cart_item)
    
    def test_remove_from_cart_url(self):
        """Test the remove_from_cart URL"""
        url = reverse('booking_cart_app:remove_from_cart', args=[1])
        self.assertEqual(resolve(url).func, remove_from_cart)
    
    def test_checkout_url(self):
        """Test the checkout URL"""
        url = reverse('booking_cart_app:checkout')
        self.assertEqual(resolve(url).func, checkout)
    
    def test_booking_confirmation_url(self):
        """Test the booking_confirmation URL"""
        url = reverse('booking_cart_app:booking_confirmation', args=['abc123'])
        self.assertEqual(resolve(url).func, booking_confirmation)
    
    def test_booking_list_url(self):
        """Test the booking_list URL"""
        url = reverse('booking_cart_app:booking_list')
        self.assertEqual(resolve(url).func, booking_list)
    
    def test_booking_detail_url(self):
        """Test the booking_detail URL"""
        url = reverse('booking_cart_app:booking_detail', args=['abc123'])
        self.assertEqual(resolve(url).func, booking_detail)
    
    def test_cancel_booking_url(self):
        """Test the cancel_booking URL"""
        url = reverse('booking_cart_app:cancel_booking', args=['abc123'])
        self.assertEqual(resolve(url).func, cancel_booking)
    
    def test_provider_booking_list_url(self):
        """Test the provider_booking_list URL"""
        url = reverse('booking_cart_app:provider_booking_list')
        self.assertEqual(resolve(url).func, provider_booking_list)
    
    def test_provider_booking_detail_url(self):
        """Test the provider_booking_detail URL"""
        url = reverse('booking_cart_app:provider_booking_detail', args=['abc123'])
        self.assertEqual(resolve(url).func, provider_booking_detail)
    
    def test_provider_update_booking_status_url(self):
        """Test the provider_update_booking_status URL"""
        url = reverse('booking_cart_app:provider_update_booking_status', args=['abc123'])
        self.assertEqual(resolve(url).func, provider_update_booking_status)
    
    def test_provider_service_availability_url(self):
        """Test the provider_service_availability URL"""
        url = reverse('booking_cart_app:provider_service_availability', args=[1])
        self.assertEqual(resolve(url).func, provider_service_availability)
    
    def test_provider_bulk_availability_url(self):
        """Test the provider_bulk_availability URL"""
        url = reverse('booking_cart_app:provider_bulk_availability', args=[1])
        self.assertEqual(resolve(url).func, provider_bulk_availability)
    
    def test_provider_update_availability_url(self):
        """Test the provider_update_availability URL"""
        url = reverse('booking_cart_app:provider_update_availability', args=[1])
        self.assertEqual(resolve(url).func, provider_update_availability)
    
    def test_provider_delete_availability_url(self):
        """Test the provider_delete_availability URL"""
        url = reverse('booking_cart_app:provider_delete_availability', args=[1])
        self.assertEqual(resolve(url).func, provider_delete_availability)
    
    def test_admin_booking_list_url(self):
        """Test the admin_booking_list URL"""
        url = reverse('booking_cart_app:admin_booking_list')
        self.assertEqual(resolve(url).func, admin_booking_list)
    
    def test_admin_booking_detail_url(self):
        """Test the admin_booking_detail URL"""
        url = reverse('booking_cart_app:admin_booking_detail', args=['abc123'])
        self.assertEqual(resolve(url).func, admin_booking_detail)
    
    def test_admin_update_booking_status_url(self):
        """Test the admin_update_booking_status URL"""
        url = reverse('booking_cart_app:admin_update_booking_status', args=['abc123'])
        self.assertEqual(resolve(url).func, admin_update_booking_status)
    
    def test_admin_booking_analytics_url(self):
        """Test the admin_booking_analytics URL"""
        url = reverse('booking_cart_app:admin_booking_analytics')
        self.assertEqual(resolve(url).func, admin_booking_analytics)
