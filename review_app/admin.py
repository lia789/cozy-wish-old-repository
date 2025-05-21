from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewResponse, ReviewFlag


class ReviewResponseInline(admin.StackedInline):
    model = ReviewResponse
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class ReviewFlagInline(admin.TabularInline):
    model = ReviewFlag
    extra = 0
    readonly_fields = ('flagged_by', 'created_at', 'reviewed_at', 'reviewed_by')
    fields = ('flagged_by', 'reason', 'status', 'created_at', 'reviewed_at', 'reviewed_by')
    can_delete = False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'rating_stars', 'created_at', 'is_approved', 'is_flagged', 'has_response')
    list_filter = ('rating', 'is_approved', 'is_flagged', 'created_at')
    search_fields = ('user__email', 'venue__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReviewResponseInline, ReviewFlagInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'venue', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_flagged', 'created_at', 'updated_at')
        }),
    )
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    def has_response(self, obj):
        """Check if review has a response"""
        return hasattr(obj, 'response')
    has_response.boolean = True
    has_response.short_description = 'Response'


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ('review', 'created_at', 'updated_at')
    search_fields = ('review__user__email', 'review__venue__name', 'response_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Response Information', {
            'fields': ('review', 'response_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ReviewFlag)
class ReviewFlagAdmin(admin.ModelAdmin):
    list_display = ('review', 'flagged_by', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('review__user__email', 'review__venue__name', 'flagged_by__email', 'reason')
    readonly_fields = ('created_at', 'reviewed_at')
    
    fieldsets = (
        ('Flag Information', {
            'fields': ('review', 'flagged_by', 'reason', 'status')
        }),
        ('Review Status', {
            'fields': ('reviewed_by', 'reviewed_at', 'created_at')
        }),
    )
    
    actions = ['approve_flags', 'reject_flags']
    
    def approve_flags(self, request, queryset):
        """Approve selected flags"""
        for flag in queryset.filter(status='pending'):
            flag.approve(request.user)
        self.message_user(request, f"{queryset.filter(status='pending').count()} flags were approved.")
    approve_flags.short_description = "Approve selected flags"
    
    def reject_flags(self, request, queryset):
        """Reject selected flags"""
        for flag in queryset.filter(status='pending'):
            flag.reject(request.user)
        self.message_user(request, f"{queryset.filter(status='pending').count()} flags were rejected.")
    reject_flags.short_description = "Reject selected flags"
