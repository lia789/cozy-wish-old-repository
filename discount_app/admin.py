from django.contrib import admin
from .models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage


class DiscountBaseAdmin(admin.ModelAdmin):
    """Base admin class for all discount types"""
    list_display = ('name', 'discount_type', 'discount_value', 'start_date', 'end_date', 'get_status')
    list_filter = ('discount_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'

    def get_status(self, obj):
        return obj.get_status()
    get_status.short_description = 'Status'


@admin.register(VenueDiscount)
class VenueDiscountAdmin(DiscountBaseAdmin):
    """Admin for venue-wide discounts"""
    list_display = DiscountBaseAdmin.list_display + ('venue', 'is_approved')
    list_filter = DiscountBaseAdmin.list_filter + ('is_approved', 'venue')
    raw_id_fields = ('venue', 'created_by', 'approved_by')
    fieldsets = (
        ('Discount Information', {
            'fields': ('name', 'description', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date')
        }),
        ('Venue Information', {
            'fields': ('venue', 'min_booking_value', 'max_discount_amount')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceDiscount)
class ServiceDiscountAdmin(DiscountBaseAdmin):
    """Admin for service-specific discounts"""
    list_display = DiscountBaseAdmin.list_display + ('service', 'is_approved')
    list_filter = DiscountBaseAdmin.list_filter + ('is_approved', 'service__venue')
    raw_id_fields = ('service', 'created_by', 'approved_by')
    fieldsets = (
        ('Discount Information', {
            'fields': ('name', 'description', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date')
        }),
        ('Service Information', {
            'fields': ('service',)
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformDiscount)
class PlatformDiscountAdmin(DiscountBaseAdmin):
    """Admin for platform-wide discounts"""
    list_display = DiscountBaseAdmin.list_display + ('category', 'is_featured')
    list_filter = DiscountBaseAdmin.list_filter + ('is_featured', 'category')
    raw_id_fields = ('created_by',)
    fieldsets = (
        ('Discount Information', {
            'fields': ('name', 'description', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date')
        }),
        ('Targeting', {
            'fields': ('category', 'min_booking_value', 'max_discount_amount', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    """Admin for discount usage tracking"""
    list_display = ('user', 'discount_type', 'discount_id', 'booking', 'original_price', 'discount_amount', 'final_price', 'used_at')
    list_filter = ('discount_type', 'used_at')
    search_fields = ('user__email', 'booking__booking_id')
    readonly_fields = ('user', 'discount_type', 'discount_id', 'booking', 'original_price', 'discount_amount', 'final_price', 'used_at')
    date_hierarchy = 'used_at'

