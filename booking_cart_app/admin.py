from django.contrib import admin
from .models import CartItem, Booking, BookingItem, ServiceAvailability


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'time_slot', 'quantity', 'added_at', 'expires_at')
    list_filter = ('date', 'added_at', 'expires_at')
    search_fields = ('user__email', 'service__title')
    date_hierarchy = 'date'


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0
    readonly_fields = ('service_title', 'service_price', 'quantity', 'date', 'time_slot')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'venue', 'status', 'total_price', 'booking_date')
    list_filter = ('status', 'booking_date', 'venue')
    search_fields = ('booking_id', 'user__email', 'venue__name')
    readonly_fields = ('booking_id', 'booking_date')
    date_hierarchy = 'booking_date'
    inlines = [BookingItemInline]

    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'venue', 'status', 'total_price', 'booking_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'cancellation_reason')
        }),
    )


class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time_slot', 'max_bookings', 'current_bookings', 'is_available')
    list_filter = ('date', 'is_available', 'service__venue')
    search_fields = ('service__title', 'service__venue__name')
    date_hierarchy = 'date'
    list_editable = ('max_bookings', 'is_available')


admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ServiceAvailability, ServiceAvailabilityAdmin)
