from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt, DeletedAccount
)



class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'




class ServiceProviderProfileInline(admin.StackedInline):
    model = ServiceProviderProfile
    can_delete = False
    verbose_name_plural = 'Service Provider Profile'




@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'is_service_provider',
                       'email_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_customer', 'is_service_provider')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [CustomerProfileInline, ServiceProviderProfileInline]




@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'city')
    search_fields = ('user__email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('city', 'gender')




@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone_number', 'created_at')
    search_fields = ('user__email', 'business_name', 'contact_person_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'business_name', 'phone_number', 'profile_picture')
        }),
        (_('Contact Person'), {
            'fields': ('contact_person_name',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )




@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_provider', 'designation', 'is_active')
    list_filter = ('is_active', 'designation')
    search_fields = ('name', 'service_provider__user__email')




@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__email', 'ip_address', 'details')
    readonly_fields = ('user', 'activity_type', 'ip_address', 'user_agent', 'timestamp', 'details')





@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'timestamp', 'was_successful')
    list_filter = ('was_successful', 'timestamp')
    search_fields = ('email', 'ip_address')
    readonly_fields = ('email', 'ip_address', 'user_agent', 'timestamp', 'was_successful')




@admin.register(DeletedAccount)
class DeletedAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'deleted_at', 'ip_address')
    list_filter = ('deleted_at',)
    search_fields = ('email', 'ip_address')
    readonly_fields = ('email', 'deleted_at', 'ip_address', 'user_agent')
