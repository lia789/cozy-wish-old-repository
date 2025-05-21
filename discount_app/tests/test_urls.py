from django.test import TestCase
from django.urls import reverse, resolve
from discount_app.views import (
    # Customer views
    FeaturedDiscountsView, VenueDiscountsView, SearchDiscountsView,
    
    # Service provider views
    ProviderDiscountListView, CreateVenueDiscountView, CreateServiceDiscountView,
    UpdateVenueDiscountView, UpdateServiceDiscountView,
    DeleteVenueDiscountView, DeleteServiceDiscountView,
    
    # Admin views
    AdminDiscountListView, AdminDiscountDetailView, AdminCreatePlatformDiscountView,
    AdminUpdatePlatformDiscountView, AdminDeletePlatformDiscountView,
    AdminDiscountApprovalView, AdminApproveDiscountView, AdminDiscountDashboardView
)

class DiscountURLsTest(TestCase):
    """Test the URLs for the discount app"""
    
    def test_customer_urls(self):
        """Test the customer-facing URLs"""
        # Featured discounts
        url = reverse('discount_app:featured_discounts')
        self.assertEqual(url, '/discounts/featured/')
        self.assertEqual(resolve(url).func.view_class, FeaturedDiscountsView)
        
        # Venue discounts
        url = reverse('discount_app:venue_discounts', args=['test-venue'])
        self.assertEqual(url, '/discounts/venue/test-venue/')
        self.assertEqual(resolve(url).func.view_class, VenueDiscountsView)
        
        # Search discounts
        url = reverse('discount_app:search_discounts')
        self.assertEqual(url, '/discounts/search/')
        self.assertEqual(resolve(url).func.view_class, SearchDiscountsView)
    
    def test_service_provider_urls(self):
        """Test the service provider URLs"""
        # Discount list
        url = reverse('discount_app:provider_discount_list')
        self.assertEqual(url, '/discounts/provider/list/')
        self.assertEqual(resolve(url).func.view_class, ProviderDiscountListView)
        
        # Create venue discount
        url = reverse('discount_app:create_venue_discount')
        self.assertEqual(url, '/discounts/provider/venue/create/')
        self.assertEqual(resolve(url).func.view_class, CreateVenueDiscountView)
        
        # Create service discount
        url = reverse('discount_app:create_service_discount')
        self.assertEqual(url, '/discounts/provider/service/create/')
        self.assertEqual(resolve(url).func.view_class, CreateServiceDiscountView)
        
        # Update venue discount
        url = reverse('discount_app:update_venue_discount', args=[1])
        self.assertEqual(url, '/discounts/provider/venue/update/1/')
        self.assertEqual(resolve(url).func.view_class, UpdateVenueDiscountView)
        
        # Update service discount
        url = reverse('discount_app:update_service_discount', args=[1])
        self.assertEqual(url, '/discounts/provider/service/update/1/')
        self.assertEqual(resolve(url).func.view_class, UpdateServiceDiscountView)
        
        # Delete venue discount
        url = reverse('discount_app:delete_venue_discount', args=[1])
        self.assertEqual(url, '/discounts/provider/venue/delete/1/')
        self.assertEqual(resolve(url).func.view_class, DeleteVenueDiscountView)
        
        # Delete service discount
        url = reverse('discount_app:delete_service_discount', args=[1])
        self.assertEqual(url, '/discounts/provider/service/delete/1/')
        self.assertEqual(resolve(url).func.view_class, DeleteServiceDiscountView)
    
    def test_admin_urls(self):
        """Test the admin URLs"""
        # Discount list
        url = reverse('discount_app:admin_discount_list')
        self.assertEqual(url, '/discounts/admin/list/')
        self.assertEqual(resolve(url).func.view_class, AdminDiscountListView)
        
        # Discount detail
        url = reverse('discount_app:admin_discount_detail', args=['venue', 1])
        self.assertEqual(url, '/discounts/admin/detail/venue/1/')
        self.assertEqual(resolve(url).func.view_class, AdminDiscountDetailView)
        
        # Create platform discount
        url = reverse('discount_app:admin_create_platform_discount')
        self.assertEqual(url, '/discounts/admin/platform/create/')
        self.assertEqual(resolve(url).func.view_class, AdminCreatePlatformDiscountView)
        
        # Update platform discount
        url = reverse('discount_app:admin_update_platform_discount', args=[1])
        self.assertEqual(url, '/discounts/admin/platform/update/1/')
        self.assertEqual(resolve(url).func.view_class, AdminUpdatePlatformDiscountView)
        
        # Delete platform discount
        url = reverse('discount_app:admin_delete_platform_discount', args=[1])
        self.assertEqual(url, '/discounts/admin/platform/delete/1/')
        self.assertEqual(resolve(url).func.view_class, AdminDeletePlatformDiscountView)
        
        # Discount approval
        url = reverse('discount_app:admin_discount_approval')
        self.assertEqual(url, '/discounts/admin/approval/')
        self.assertEqual(resolve(url).func.view_class, AdminDiscountApprovalView)
        
        # Approve discount
        url = reverse('discount_app:admin_approve_discount', args=['venue', 1])
        self.assertEqual(url, '/discounts/admin/approve/venue/1/')
        self.assertEqual(resolve(url).func.view_class, AdminApproveDiscountView)
        
        # Discount dashboard
        url = reverse('discount_app:admin_discount_dashboard')
        self.assertEqual(url, '/discounts/admin/dashboard/')
        self.assertEqual(resolve(url).func.view_class, AdminDiscountDashboardView)
