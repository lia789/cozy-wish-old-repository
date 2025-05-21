# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView,
    PasswordResetConfirmView, LoginView,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

# Message constants
LOGIN_FAILED_MESSAGE = 'Multiple failed login attempts detected. Please try again later or reset your password.'
LOGOUT_SUCCESS_MESSAGE = 'You have been logged out successfully.'
PROFILE_UPDATE_SUCCESS = 'Your profile has been updated successfully.'
PASSWORD_CHANGE_SUCCESS = 'Your password has been changed successfully.'
SIGNUP_SUCCESS_MESSAGE = 'Your account has been created successfully. Welcome to CozyWish!'
SIGNUP_SUCCESS_NO_LOGIN = 'Your account has been created successfully. You can now log in.'
PROFILE_PICTURE_UPDATE_SUCCESS = 'Profile picture updated successfully.'
STAFF_ADDED_SUCCESS = 'Staff member added successfully.'
STAFF_UPDATED_SUCCESS = 'Staff member updated successfully.'
STAFF_DELETED_SUCCESS = 'Staff member deleted successfully.'
PASSWORD_RESET_SUCCESS = 'Your password has been reset successfully. You can now log in with your new password.'
ACCOUNT_DELETED_SUCCESS = 'Your account has been deleted successfully.'

# Local imports
from .models import (
    CustomUser, CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt, DeletedAccount,
)
from .forms import (
    CustomerSignUpForm, ServiceProviderSignUpForm, CustomLoginForm,
    CustomerProfileForm, ServiceProviderProfileForm, StaffMemberForm,
    CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm,
)

# Admin app imports
from admin_app.models import SystemConfig



# Helper functions
def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_activity(user, activity_type, request=None, details=''):
    """Log user activity with IP and user agent."""
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details
    )


def log_login_attempt(email, success, request=None):
    """Record login attempt with success status and request metadata."""
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    LoginAttempt.objects.create(
        email=email,
        was_successful=success,
        ip_address=ip_address,
        user_agent=user_agent
    )


def check_multiple_failed_logins(email, request):
    """
    Check for multiple failed login attempts from same IP within a time window.
    Returns True if attempts exceed threshold, False otherwise.
    """
    # Get max login attempts from system config
    system_config = SystemConfig.get_instance()
    max_attempts = system_config.max_login_attempts

    # Define a time window (e.g., last 30 minutes)
    time_window = timezone.now() - timezone.timedelta(minutes=system_config.login_lockout_duration)

    ip_address = get_client_ip(request)
    recent_failed_attempts = LoginAttempt.objects.filter(
        email=email,
        was_successful=False,
        ip_address=ip_address,
        timestamp__gte=time_window  # Only count attempts within the time window
    ).count()

    if recent_failed_attempts >= max_attempts:
        # Alert admin about multiple failed login attempts
        admin_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)
        if admin_emails:
            subject = 'Multiple Failed Login Attempts'
            message = f'Multiple failed login attempts detected for email: {email} from IP: {ip_address}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
        return True
    return False




# Business views
def for_business_view(request):
    """Service provider branding page"""
    return render(request, 'accounts_app/for_business.html')





# Authentication views
def custom_login(request):
    """
    Custom login view that handles authentication manually.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(username=email, password=password)

            if user is not None:
                # Log the user in
                login(request, user)

                # Handle "Remember me" functionality
                if not request.POST.get('remember', None):
                    # If "Remember me" is not checked, set session to expire when browser closes
                    request.session.set_expiry(0)
                else:
                    # If "Remember me" is checked, set session to expire according to SESSION_COOKIE_AGE
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)

                # Log successful login attempt
                log_login_attempt(email, True, request)

                # Log user activity
                log_user_activity(user, 'login', request)

                # Print debug information
                print(f"Login successful for user: {user.email}")
                print(f"is_staff: {user.is_staff}")
                print(f"is_authenticated: {user.is_authenticated}")
                print(f"next_url from POST: {request.POST.get('next')}")

                # Determine the redirect URL
                next_url = request.POST.get('next')

                # Validate the next URL to prevent open redirect vulnerabilities
                if next_url and not next_url.startswith('http'):
                    print(f"Redirecting to next URL: {next_url}")
                    return redirect(next_url)

                # Default role-based redirects
                if user.is_customer:
                    return redirect('booking_cart_app:booking_list')
                elif user.is_service_provider:
                    return redirect('dashboard_app:provider_dashboard')
                else:
                    return redirect('accounts_app:home')
            else:
                # Authentication failed
                form.add_error(None, "Invalid email or password.")

                # Log failed login attempt
                log_login_attempt(email, False, request)

                # Check for multiple failed login attempts
                if check_multiple_failed_logins(email, request):
                    messages.error(
                        request,
                        LOGIN_FAILED_MESSAGE
                    )
    else:
        form = CustomLoginForm()

    return render(request, 'accounts_app/login.html', {'form': form})


# Keep the class-based view for compatibility, but use the function-based view
class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's LoginView.
    This is kept for compatibility, but the function-based view is used instead.
    """
    form_class = CustomLoginForm
    template_name = 'accounts_app/login.html'





# Customer signup views
class CustomerSignUpView(CreateView):
    """
    Customer sign up view that handles registration, validation, and auto-login.
    Uses CustomerSignUpForm for data validation and user creation.
    """
    model = CustomUser
    form_class = CustomerSignUpForm
    template_name = 'accounts_app/customer_signup.html'
    success_url = reverse_lazy('booking_cart_app:booking_list')


    def form_valid(self, form):
        """
        Process valid form data, create user, and handle auto-login.
        Performs additional email uniqueness check.
        """
        # Check if email already exists
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            form.add_error('email', 'A user with this email already exists.')
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Auto-login the customer after signup
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, SIGNUP_SUCCESS_MESSAGE)
        else:
            messages.success(self.request, SIGNUP_SUCCESS_NO_LOGIN)

        # Log user activity
        log_user_activity(self.object, 'signup', self.request, 'Customer signup')

        return response





# Service provider signup views
class ServiceProviderSignUpView(CreateView):
    """
    Service provider sign up view that handles registration and auto-login.
    Uses ServiceProviderSignUpForm for validation and user creation.
    """
    model = CustomUser
    form_class = ServiceProviderSignUpForm
    template_name = 'accounts_app/service_provider_signup.html'
    success_url = reverse_lazy('dashboard_app:provider_dashboard')

    def form_valid(self, form):
        """
        Process valid form data, create user, and handle auto-login.
        Checks email uniqueness and logs signup activity.
        """
        # Check if email already exists
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            form.add_error('email', 'A user with this email already exists.')
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Auto-login the service provider after signup
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, SIGNUP_SUCCESS_MESSAGE)
        else:
            messages.success(self.request, SIGNUP_SUCCESS_NO_LOGIN)

        # Log user activity
        log_user_activity(self.object, 'signup', self.request, 'Service provider signup')

        return response




# Logout view
def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        # Log user activity
        log_user_activity(request.user, 'logout', request)
        logout(request)

    messages.success(request, LOGOUT_SUCCESS_MESSAGE)
    return redirect('accounts_app:home')





## Profile views
@login_required
def profile_view(request):
    """Redirect to appropriate profile view based on user type"""
    if request.user.is_customer:
        return redirect('accounts_app:customer_profile')
    elif request.user.is_service_provider:
        # Get the service provider profile and redirect to the slug URL
        try:
            profile = ServiceProviderProfile.objects.get(user=request.user)
            return redirect('accounts_app:service_provider_profile', slug=profile.slug)
        except ServiceProviderProfile.DoesNotExist:
            messages.error(request, "Service provider profile not found.")
            return redirect('accounts_app:home')
    else:
        return redirect('accounts_app:home')



# Customer profile views
@method_decorator(login_required, name='dispatch')
class CustomerProfileView(DetailView):
    """Customer profile view"""
    model = CustomerProfile
    template_name = 'accounts_app/customer_profile.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        profile = CustomerProfile.objects.get_or_create(user=self.request.user)[0]
        return profile


@method_decorator(login_required, name='dispatch')
class CustomerProfileEditView(UpdateView):
    """Customer profile update"""
    model = CustomerProfile
    form_class = CustomerProfileForm
    template_name = 'accounts_app/customer_profile_edit.html'
    success_url = reverse_lazy('accounts_app:customer_profile')

    def get_object(self, queryset=None):
        profile, created = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def post(self, request, *args, **kwargs):
        if 'profile_picture' in request.FILES and len(request.POST) == 1:
            profile = self.get_object()
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()

            # Log user activity
            log_user_activity(request.user, 'profile_picture_update', request, 'Customer profile picture update')

            messages.success(request, PROFILE_PICTURE_UPDATE_SUCCESS)
            return redirect('accounts_app:customer_profile')

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, PROFILE_UPDATE_SUCCESS)

        # Log user activity
        log_user_activity(self.request.user, 'profile_update', self.request, 'Customer profile update')

        return response



# Service provider profile views
@method_decorator(login_required, name='dispatch')
class ServiceProviderProfileView(DetailView):
    """Service provider profile view"""
    model = ServiceProviderProfile
    template_name = 'accounts_app/service_provider_profile.html'
    context_object_name = 'object'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        # Check if the profile belongs to the current user
        obj = super().get_object(queryset)
        if obj.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_members'] = StaffMember.objects.filter(
            service_provider=self.get_object()
        ).order_by('-is_active', 'name')[:10]  # Limit to 10 as per requirements
        return context


@method_decorator(login_required, name='dispatch')
class ServiceProviderProfileEditView(UpdateView):
    """Service provider profile update"""
    model = ServiceProviderProfile
    form_class = ServiceProviderProfileForm
    template_name = 'accounts_app/service_provider_profile_edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        # Check if the profile belongs to the current user
        obj = super().get_object(queryset)
        if obj.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse('accounts_app:service_provider_profile', kwargs={'slug': self.object.slug})

    def post(self, request, *args, **kwargs):
        # Check if this is a profile picture only update from the profile page
        if 'profile_picture' in request.FILES and len(request.POST) == 1:  # Only CSRF token in POST
            profile = self.get_object()
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()

            # Log user activity
            log_user_activity(request.user, 'profile_picture_update', request, 'Service provider profile picture update')

            messages.success(request, PROFILE_PICTURE_UPDATE_SUCCESS)
            return redirect('accounts_app:service_provider_profile', slug=profile.slug)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, PROFILE_UPDATE_SUCCESS)

        # Log user activity
        log_user_activity(self.request.user, 'profile_update', self.request, 'Service provider profile update')

        return response






## Password management views
@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view"""
    form_class = CustomPasswordChangeForm
    template_name = 'accounts_app/password_change.html'
    success_url = reverse_lazy('accounts_app:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Log user activity
        log_user_activity(self.request.user, 'password_change', self.request)

        return response


@login_required
def password_change_done_view(request):
    """Password change done view"""
    messages.success(request, PASSWORD_CHANGE_SUCCESS)
    return redirect('accounts_app:profile')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts_app/password_reset.html'
    email_template_name = 'accounts_app/password_reset_email.html'
    subject_template_name = 'accounts_app/password_reset_subject.txt'
    success_url = reverse_lazy('accounts_app:password_reset_done')


def password_reset_done_view(request):
    """Password reset done view"""
    return render(request, 'accounts_app/password_reset_done.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    form_class = CustomSetPasswordForm
    template_name = 'accounts_app/password_reset_confirm.html'
    success_url = reverse_lazy('accounts_app:password_reset_complete')


def password_reset_complete_view(request):
    """Password reset complete view"""
    messages.success(request, PASSWORD_RESET_SUCCESS)
    return redirect('accounts_app:login')







##  Staff management views
@login_required
def staff_list_view(request):
    """Staff list view for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts_app:home')

    service_provider = get_object_or_404(ServiceProviderProfile, user=request.user)
    staff_members = StaffMember.objects.filter(service_provider=service_provider).order_by('-is_active', 'name')

    return render(request, 'accounts_app/staff_list.html', {
        'staff_members': staff_members,
        'service_provider': service_provider
    })


@login_required
def staff_add_view(request):
    """Add staff member view"""
    if not request.user.is_service_provider:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts_app:home')

    service_provider = get_object_or_404(ServiceProviderProfile, user=request.user)

    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES)
        if form.is_valid():
            staff_member = form.save(commit=False)
            staff_member.service_provider = service_provider
            staff_member.save()

            # Log user activity
            log_user_activity(request.user, 'staff_add', request, f'Added staff member: {staff_member.name}')

            messages.success(request, STAFF_ADDED_SUCCESS)
            return redirect('accounts_app:staff_list')
    else:
        form = StaffMemberForm()

    return render(request, 'accounts_app/staff_form.html', {
        'form': form,
        'service_provider': service_provider,
        'action': 'Add'
    })


@login_required
def staff_edit_view(request, pk):
    """Edit staff member view"""
    if not request.user.is_service_provider:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts_app:home')

    service_provider = get_object_or_404(ServiceProviderProfile, user=request.user)
    staff_member = get_object_or_404(StaffMember, pk=pk, service_provider=service_provider)

    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()

            # Log user activity
            log_user_activity(request.user, 'staff_edit', request, f'Edited staff member: {staff_member.name}')

            messages.success(request, STAFF_UPDATED_SUCCESS)
            return redirect('accounts_app:staff_list')
    else:
        form = StaffMemberForm(instance=staff_member)

    return render(request, 'accounts_app/staff_form.html', {
        'form': form,
        'service_provider': service_provider,
        'staff_member': staff_member,
        'action': 'Edit'
    })


@login_required
def staff_toggle_active_view(request, pk):
    """Toggle staff member active status"""
    if not request.user.is_service_provider:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts_app:home')

    service_provider = get_object_or_404(ServiceProviderProfile, user=request.user)
    staff_member = get_object_or_404(StaffMember, pk=pk, service_provider=service_provider)

    staff_member.is_active = not staff_member.is_active
    staff_member.save()

    # Log user activity
    status = 'activated' if staff_member.is_active else 'deactivated'
    log_user_activity(request.user, 'staff_toggle_active', request, f'{status.capitalize()} staff member: {staff_member.name}')

    messages.success(request, f'Staff member {status} successfully.')
    return redirect('accounts_app:staff_list')


@login_required
def staff_delete_view(request, pk):
    """Delete staff member view"""
    if not request.user.is_service_provider:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts_app:home')

    service_provider = get_object_or_404(ServiceProviderProfile, user=request.user)
    staff_member = get_object_or_404(StaffMember, pk=pk, service_provider=service_provider)

    if request.method == 'POST':
        staff_name = staff_member.name
        staff_member.delete()

        # Log user activity
        log_user_activity(request.user, 'staff_delete', request, f'Deleted staff member: {staff_name}')

        messages.success(request, STAFF_DELETED_SUCCESS)
        return redirect('accounts_app:staff_list')

    return render(request, 'accounts_app/staff_confirm_delete.html', {
        'staff_member': staff_member,
        'service_provider': service_provider
    })






# Admin views have been removed as they are now implemented in admin_app


@login_required
def account_delete_view(request):
    """Delete own account view"""
    if request.method == 'POST':
        user = request.user
        email = user.email  # Store email for logging

        # Import needed models and functions
        from django.contrib.auth import get_user_model
        from django.db import transaction
        User = get_user_model()

        try:
            # Use a transaction to ensure atomicity - either all operations succeed or none do
            with transaction.atomic():
                # Log user activity before deleting
                log_user_activity(user, 'account_delete', request, 'Account deletion')

                # Check if user has dashboard preferences
                from django.db import connection
                with connection.cursor() as cursor:
                    # Check if dashboard_app_dashboardpreference table exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_app_dashboardpreference';"
                    )
                    if cursor.fetchone():
                        # If table exists, delete any preferences for this user
                        cursor.execute(
                            "DELETE FROM dashboard_app_dashboardpreference WHERE user_id = ?;",
                            [user.id]
                        )

                # Manually delete related objects that might cause issues
                if hasattr(user, 'customer_profile'):
                    user.customer_profile.delete()
                if hasattr(user, 'provider_profile'):
                    user.provider_profile.delete()

                # Delete any cart items
                try:
                    from booking_cart_app.models import CartItem
                    CartItem.objects.filter(user=user).delete()
                except ImportError:
                    # CartItem model might not exist in test environment
                    pass

                # Delete any user notifications
                try:
                    from django.apps import apps
                    if apps.is_installed('notifications_app'):
                        UserNotification = apps.get_model('notifications_app', 'UserNotification')
                        UserNotification.objects.filter(user=user).delete()
                except:
                    # Notifications app might not exist in test environment
                    pass

                # Get user ID before logout for deletion
                user_id = user.id

                # First verify the user exists
                if not User.objects.filter(id=user_id).exists():
                    raise ValueError(f"User with ID {user_id} does not exist")

                # Delete the user account BEFORE creating the DeletedAccount record
                # This ensures we don't have a situation where the DeletedAccount exists
                # but the user account still exists
                User.objects.filter(id=user_id).delete()

                # Verify the user was actually deleted
                if User.objects.filter(id=user_id).exists():
                    raise ValueError(f"Failed to delete user with ID {user_id}")

                # Now record the deleted account to prevent re-registration
                DeletedAccount.objects.create(
                    email=email,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

            # Logout the user - do this outside the transaction
            # since it's not critical to the deletion process
            logout(request)

            # Log the successful deletion
            print(f"User account deleted successfully: {email}")
            messages.success(request, ACCOUNT_DELETED_SUCCESS)

        except Exception as e:
            # Log the error but don't show technical details to the user
            print(f"Error deleting account: {str(e)}")
            messages.error(request, 'There was a problem deleting your account. Please contact support.')

        return redirect('accounts_app:home')

    return render(request, 'accounts_app/account_confirm_delete.html')
