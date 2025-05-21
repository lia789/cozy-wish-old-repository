from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Tag, Venue, VenueImage, OpeningHours,
    FAQ, Service, Review, TeamMember, USCity
)


class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1
    fields = ('image', 'image_order', 'caption')


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 7  # One for each day of the week
    max_num = 7


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ('title', 'price', 'discounted_price', 'duration', 'is_active')


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'city', 'state', 'approval_status', 'is_active', 'created_at')
    list_filter = ('approval_status', 'is_active', 'category', 'state', 'city')
    search_fields = ('name', 'owner__email', 'city', 'state')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)

    inlines = [
        VenueImageInline,
        OpeningHoursInline,
        ServiceInline,
        FAQInline,
        TeamMemberInline,
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'slug', 'category', 'tags', 'venue_type', 'about')
        }),
        ('Location', {
            'fields': ('state', 'county', 'city', 'street_number', 'street_name', 'latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('approval_status', 'rejection_reason', 'is_active', 'created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.approval_status == 'rejected' and 'rejection_reason' not in readonly_fields:
            readonly_fields.append('rejection_reason')
        return readonly_fields


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'price', 'discounted_price', 'duration', 'is_active')
    list_filter = ('is_active', 'venue')
    search_fields = ('title', 'venue__name')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Basic Information', {
            'fields': ('venue', 'title', 'slug', 'short_description')
        }),
        ('Pricing and Duration', {
            'fields': ('price', 'discounted_price', 'duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__email', 'venue__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'venue', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved', 'created_at', 'updated_at')
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'title', 'is_active')
    list_filter = ('is_active', 'venue')
    search_fields = ('name', 'title', 'venue__name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('venue', 'name', 'title', 'profile_image', 'bio')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(USCity)
class USCityAdmin(admin.ModelAdmin):
    list_display = ('city', 'state_id', 'state_name', 'county_name')
    list_filter = ('state_name', 'state_id')
    search_fields = ('city', 'state_name', 'county_name', 'zip_codes')
    readonly_fields = ('city_id',)

    fieldsets = (
        ('Location Information', {
            'fields': ('city', 'state_id', 'state_name', 'county_name')
        }),
        ('Geographic Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Additional Information', {
            'fields': ('zip_codes', 'city_id')
        }),
    )
