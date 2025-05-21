from django.contrib import admin
from .models import PaymentMethod, Transaction, Invoice


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'name', 'last_four', 'is_default', 'created_at')
    list_filter = ('payment_type', 'is_default', 'created_at')
    search_fields = ('user__email', 'name', 'last_four')
    date_hierarchy = 'created_at'


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'booking', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'booking__booking_id', 'payment_method_details')
    date_hierarchy = 'created_at'
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'booking', 'amount', 'status', 'issue_date', 'due_date', 'paid_date')
    list_filter = ('status', 'issue_date', 'due_date', 'paid_date')
    search_fields = ('invoice_number', 'user__email', 'booking__booking_id')
    date_hierarchy = 'issue_date'
    readonly_fields = ('invoice_number', 'issue_date')


admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Invoice, InvoiceAdmin)
