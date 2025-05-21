from django.urls import path
from . import views

app_name = 'payments_app'

urlpatterns = [
    # Customer URLs
    path('process/<uuid:booking_id>/', views.payment_process, name='payment_process'),
    path('process/<uuid:booking_id>/<uuid:checkout_session_id>/', views.payment_process, name='payment_process_with_session'),
    path('confirmation/<uuid:transaction_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('history/', views.payment_history, name='payment_history'),
    path('detail/<uuid:transaction_id>/', views.payment_detail, name='payment_detail'),
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/add/', views.add_payment_method, name='add_payment_method'),
    path('methods/edit/<int:payment_method_id>/', views.edit_payment_method, name='edit_payment_method'),
    path('methods/delete/<int:payment_method_id>/', views.delete_payment_method, name='delete_payment_method'),

    # Service Provider URLs
    path('provider/history/', views.provider_payment_history, name='provider_payment_history'),
    path('provider/detail/<uuid:transaction_id>/', views.provider_payment_detail, name='provider_payment_detail'),

    # Admin URLs
    path('admin/payments/', views.admin_payment_list, name='admin_payment_list'),
    path('admin/payments/<uuid:transaction_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('admin/payments/<uuid:transaction_id>/refund/', views.admin_refund_payment, name='admin_refund_payment'),
    path('admin/invoices/', views.admin_invoice_list, name='admin_invoice_list'),
    path('admin/invoices/<uuid:invoice_number>/', views.admin_invoice_detail, name='admin_invoice_detail'),
]
