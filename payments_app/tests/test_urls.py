from django.test import TestCase
from django.urls import reverse, resolve
import uuid

from payments_app.views import (
    payment_process, payment_confirmation, payment_history, payment_detail,
    payment_methods, add_payment_method, edit_payment_method, delete_payment_method,
    provider_payment_history, provider_payment_detail,
    admin_payment_list, admin_payment_detail, admin_refund_payment,
    admin_invoice_list, admin_invoice_detail
)

class UrlsTest(TestCase):
    """Test the URLs in the payments_app"""
    
    def test_payment_process_url(self):
        """Test the payment_process URL"""
        booking_id = uuid.uuid4()
        url = reverse('payments_app:payment_process', args=[booking_id])
        self.assertEqual(resolve(url).func, payment_process)
        self.assertEqual(url, f'/payments/process/{booking_id}/')
    
    def test_payment_confirmation_url(self):
        """Test the payment_confirmation URL"""
        transaction_id = uuid.uuid4()
        url = reverse('payments_app:payment_confirmation', args=[transaction_id])
        self.assertEqual(resolve(url).func, payment_confirmation)
        self.assertEqual(url, f'/payments/confirmation/{transaction_id}/')
    
    def test_payment_history_url(self):
        """Test the payment_history URL"""
        url = reverse('payments_app:payment_history')
        self.assertEqual(resolve(url).func, payment_history)
        self.assertEqual(url, '/payments/history/')
    
    def test_payment_detail_url(self):
        """Test the payment_detail URL"""
        transaction_id = uuid.uuid4()
        url = reverse('payments_app:payment_detail', args=[transaction_id])
        self.assertEqual(resolve(url).func, payment_detail)
        self.assertEqual(url, f'/payments/detail/{transaction_id}/')
    
    def test_payment_methods_url(self):
        """Test the payment_methods URL"""
        url = reverse('payments_app:payment_methods')
        self.assertEqual(resolve(url).func, payment_methods)
        self.assertEqual(url, '/payments/methods/')
    
    def test_add_payment_method_url(self):
        """Test the add_payment_method URL"""
        url = reverse('payments_app:add_payment_method')
        self.assertEqual(resolve(url).func, add_payment_method)
        self.assertEqual(url, '/payments/methods/add/')
    
    def test_edit_payment_method_url(self):
        """Test the edit_payment_method URL"""
        payment_method_id = 1
        url = reverse('payments_app:edit_payment_method', args=[payment_method_id])
        self.assertEqual(resolve(url).func, edit_payment_method)
        self.assertEqual(url, f'/payments/methods/edit/{payment_method_id}/')
    
    def test_delete_payment_method_url(self):
        """Test the delete_payment_method URL"""
        payment_method_id = 1
        url = reverse('payments_app:delete_payment_method', args=[payment_method_id])
        self.assertEqual(resolve(url).func, delete_payment_method)
        self.assertEqual(url, f'/payments/methods/delete/{payment_method_id}/')
    
    def test_provider_payment_history_url(self):
        """Test the provider_payment_history URL"""
        url = reverse('payments_app:provider_payment_history')
        self.assertEqual(resolve(url).func, provider_payment_history)
        self.assertEqual(url, '/payments/provider/history/')
    
    def test_provider_payment_detail_url(self):
        """Test the provider_payment_detail URL"""
        transaction_id = uuid.uuid4()
        url = reverse('payments_app:provider_payment_detail', args=[transaction_id])
        self.assertEqual(resolve(url).func, provider_payment_detail)
        self.assertEqual(url, f'/payments/provider/detail/{transaction_id}/')
    
    def test_admin_payment_list_url(self):
        """Test the admin_payment_list URL"""
        url = reverse('payments_app:admin_payment_list')
        self.assertEqual(resolve(url).func, admin_payment_list)
        self.assertEqual(url, '/payments/admin/payments/')
    
    def test_admin_payment_detail_url(self):
        """Test the admin_payment_detail URL"""
        transaction_id = uuid.uuid4()
        url = reverse('payments_app:admin_payment_detail', args=[transaction_id])
        self.assertEqual(resolve(url).func, admin_payment_detail)
        self.assertEqual(url, f'/payments/admin/payments/{transaction_id}/')
    
    def test_admin_refund_payment_url(self):
        """Test the admin_refund_payment URL"""
        transaction_id = uuid.uuid4()
        url = reverse('payments_app:admin_refund_payment', args=[transaction_id])
        self.assertEqual(resolve(url).func, admin_refund_payment)
        self.assertEqual(url, f'/payments/admin/payments/{transaction_id}/refund/')
    
    def test_admin_invoice_list_url(self):
        """Test the admin_invoice_list URL"""
        url = reverse('payments_app:admin_invoice_list')
        self.assertEqual(resolve(url).func, admin_invoice_list)
        self.assertEqual(url, '/payments/admin/invoices/')
    
    def test_admin_invoice_detail_url(self):
        """Test the admin_invoice_detail URL"""
        invoice_number = uuid.uuid4()
        url = reverse('payments_app:admin_invoice_detail', args=[invoice_number])
        self.assertEqual(resolve(url).func, admin_invoice_detail)
        self.assertEqual(url, f'/payments/admin/invoices/{invoice_number}/')
