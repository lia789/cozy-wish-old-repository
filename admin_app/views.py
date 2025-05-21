from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta, datetime
from functools import wraps
import csv
import json

from .utils import log_admin_activity, get_client_ip, get_admin_preference

from accounts_app.models import ServiceProviderProfile, CustomerProfile, StaffMember
from venues_app.models import Venue, Service, Category, Tag
from booking_cart_app.models import Booking, BookingItem
from review_app.models import Review, ReviewFlag

from .models import (
    AdminPreference, AdminActivity, AdminTask,
    SystemConfig, AuditLog, SecurityEvent
)
from .forms import (
    AdminUserCreationForm, AdminUserChangeForm, VenueApprovalForm,
    AdminTaskForm, SystemConfigForm, BulkUserActionForm,
    SecurityEventResolveForm, DateRangeForm
)

User = get_user_model()


# Helper functions
def is_admin(user):
    """Check if user is an admin (staff)"""
    return user.is_authenticated and user.is_staff


# Custom login URL for admin views
def admin_login_required(view_func):
    """Custom login_required decorator that redirects to admin login page"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('admin_app:admin_login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Error handlers
def admin_404_handler(request, exception=None):
    """Custom 404 handler for admin app"""
    return render(request, 'admin_app/404.html', status=404)


def admin_500_handler(request, exception=None):
    """Custom 500 handler for admin app"""
    return render(request, 'admin_app/500.html', status=500)


def admin_403_handler(request, exception=None):
    """Custom 403 handler for admin app"""
    return render(request, 'admin_app/403.html', status=403)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_admin_activity(request, action_type, target_model=None, target_id=None, description=None):
    """Log admin activity"""
    AdminActivity.objects.create(
        user=request.user,
        action_type=action_type,
        target_model=target_model,
        target_id=target_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


# Authentication views
def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and user.is_staff:
                login(request, user)

                # Log admin activity
                log_admin_activity(request, 'login', None, None, 'Admin login')

                # Redirect to the dashboard
                next_url = request.GET.get('next', 'admin_app:admin_dashboard')
                return redirect(next_url)
            else:
                if user is not None and not user.is_staff:
                    messages.error(request, 'Your account does not have admin privileges.')
                else:
                    messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'admin_app/login.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    """Admin logout view"""
    # Log admin activity before logging out
    log_admin_activity(request, 'logout', None, None, 'Admin logout')

    # Logout the user
    logout(request)

    # Redirect to login page
    messages.success(request, 'You have been successfully logged out.')
    return redirect('admin_app:admin_login')


# Dashboard views
@admin_login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get system configuration
    system_config = SystemConfig.get_instance()

    # Get user statistics
    total_users = User.objects.count()
    customer_count = User.objects.filter(is_customer=True).count()
    provider_count = User.objects.filter(is_service_provider=True).count()
    staff_count = User.objects.filter(is_staff=True).count()

    # Get venue statistics
    total_venues = Venue.objects.count()
    pending_venues = Venue.objects.filter(approval_status='pending').count()
    approved_venues = Venue.objects.filter(approval_status='approved').count()
    rejected_venues = Venue.objects.filter(approval_status='rejected').count()

    # Get booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    completed_bookings = Booking.objects.filter(status='completed').count()

    # Get revenue statistics
    total_revenue = Booking.objects.filter(status__in=['confirmed', 'completed']).aggregate(total=Sum('total_price'))['total'] or 0

    # Get recent activities
    recent_activities = AdminActivity.objects.all().order_by('-timestamp')[:10]

    # Get pending tasks
    pending_tasks = AdminTask.objects.filter(
        Q(assigned_to=request.user) | Q(created_by=request.user),
        status__in=['pending', 'in_progress']
    ).order_by('due_date')[:5]

    # Get security events
    unresolved_security_events = SecurityEvent.objects.filter(is_resolved=False).order_by('-timestamp')[:5]

    # Get pending venue approvals
    pending_venue_approvals = Venue.objects.filter(approval_status='pending').order_by('-created_at')[:5]

    # Get flagged reviews
    flagged_reviews = ReviewFlag.objects.filter(status='pending').order_by('-created_at')[:5]

    # Log admin dashboard view
    log_admin_activity(request, 'view', 'Dashboard', None, 'Viewed admin dashboard')

    context = {
        'preference': preference,
        'system_config': system_config,
        'total_users': total_users,
        'customer_count': customer_count,
        'provider_count': provider_count,
        'staff_count': staff_count,
        'total_venues': total_venues,
        'pending_venues': pending_venues,
        'approved_venues': approved_venues,
        'rejected_venues': rejected_venues,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities,
        'pending_tasks': pending_tasks,
        'unresolved_security_events': unresolved_security_events,
        'pending_venue_approvals': pending_venue_approvals,
        'flagged_reviews': flagged_reviews,
    }

    return render(request, 'admin_app/dashboard.html', context)


# User management views
@login_required
@user_passes_test(is_admin)
def user_list(request):
    """View all users"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get filter parameters
    user_type = request.GET.get('user_type', 'all')
    status = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')

    # Base queryset
    users = User.objects.all()

    # Apply filters
    if user_type == 'customer':
        users = users.filter(is_customer=True)
    elif user_type == 'provider':
        users = users.filter(is_service_provider=True)
    elif user_type == 'staff':
        users = users.filter(is_staff=True)

    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    # Apply search
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Order by
    users = users.order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, preference.items_per_page)
    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'User', None, 'Viewed user list')

    context = {
        'preference': preference,
        'users': users,
        'user_type': user_type,
        'status': status,
        'search_query': search_query,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/user_management/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)

    # Get related data
    if user.is_customer:
        try:
            profile = user.customer_profile
        except CustomerProfile.DoesNotExist:
            profile = None
    elif user.is_service_provider:
        try:
            profile = user.provider_profile
            venues = Venue.objects.filter(owner=user)
            staff = StaffMember.objects.filter(service_provider=profile)
        except ServiceProviderProfile.DoesNotExist:
            profile = None
            venues = []
            staff = []
    else:
        profile = None
        venues = []
        staff = []

    # Get user activities
    activities = AdminActivity.objects.filter(user=user).order_by('-timestamp')[:10]

    # Get security events
    security_events = SecurityEvent.objects.filter(user=user).order_by('-timestamp')[:10]

    # Get bookings
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')[:10]

    # Get reviews
    reviews = Review.objects.filter(user=user).order_by('-created_at')[:10]

    # Log admin activity
    log_admin_activity(request, 'view', 'User', str(user.id), f'Viewed user details for {user.email}')

    context = {
        'user_obj': user,
        'profile': profile,
        'venues': venues if user.is_service_provider else [],
        'staff': staff if user.is_service_provider else [],
        'activities': activities,
        'security_events': security_events,
        'bookings': bookings,
        'reviews': reviews,
    }

    return render(request, 'admin_app/user_management/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Add user to selected groups
            groups = form.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)

            # Log admin activity
            log_admin_activity(request, 'create', 'User', str(user.id), f'Created new user: {user.email}')

            messages.success(request, f'User {user.email} has been created successfully.')
            return redirect('admin_app:user_detail', user_id=user.id)
    else:
        form = AdminUserCreationForm()

    context = {
        'form': form,
        'title': 'Create New User',
    }

    return render(request, 'admin_app/user_management/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Edit an existing user"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()

            # Update user groups
            groups = form.cleaned_data.get('groups')
            user.groups.set(groups)

            # Log admin activity
            log_admin_activity(request, 'update', 'User', str(user.id), f'Updated user: {user.email}')

            messages.success(request, f'User {user.email} has been updated successfully.')
            return redirect('admin_app:user_detail', user_id=user.id)
    else:
        form = AdminUserChangeForm(instance=user)
        # Pre-select current groups
        form.initial['groups'] = user.groups.all()

    context = {
        'form': form,
        'user_obj': user,
        'title': f'Edit User: {user.email}',
    }

    return render(request, 'admin_app/user_management/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_app:user_detail', user_id=user.id)

    if request.method == 'POST':
        email = user.email
        user.delete()

        # Log admin activity
        log_admin_activity(request, 'delete', 'User', user_id, f'Deleted user: {email}')

        messages.success(request, f'User {email} has been deleted successfully.')
        return redirect('admin_app:user_list')

    context = {
        'user_obj': user,
    }

    return render(request, 'admin_app/user_management/user_delete.html', context)


@login_required
@user_passes_test(is_admin)
def user_bulk_actions(request):
    """Perform bulk actions on users"""
    if request.method == 'POST':
        form = BulkUserActionForm(request.POST)
        selected_users = request.POST.getlist('selected_users')

        if not selected_users:
            messages.error(request, 'No users selected.')
            return redirect('admin_app:user_list')

        if form.is_valid():
            action = form.cleaned_data.get('action')
            group = form.cleaned_data.get('group')

            users = User.objects.filter(id__in=selected_users)
            count = users.count()

            if action == 'activate':
                users.update(is_active=True)
                message = f'{count} users have been activated.'
            elif action == 'deactivate':
                # Prevent deactivating yourself
                if str(request.user.id) in selected_users:
                    users = users.exclude(id=request.user.id)
                    count = users.count()
                    messages.warning(request, 'You cannot deactivate your own account.')

                users.update(is_active=False)
                message = f'{count} users have been deactivated.'
            elif action == 'make_staff':
                users.update(is_staff=True)
                message = f'{count} users have been given staff status.'
            elif action == 'remove_staff':
                # Prevent removing staff status from yourself
                if str(request.user.id) in selected_users:
                    users = users.exclude(id=request.user.id)
                    count = users.count()
                    messages.warning(request, 'You cannot remove your own staff status.')

                users.update(is_staff=False)
                message = f'{count} users have had staff status removed.'
            elif action == 'add_to_group' and group:
                for user in users:
                    user.groups.add(group)
                message = f'{count} users have been added to the group "{group.name}".'
            elif action == 'remove_from_group' and group:
                for user in users:
                    user.groups.remove(group)
                message = f'{count} users have been removed from the group "{group.name}".'

            # Log admin activity
            log_admin_activity(
                request,
                'update',
                'User',
                ','.join(selected_users),
                f'Bulk action: {action} on {count} users'
            )

            messages.success(request, message)
            return redirect('admin_app:user_list')
    else:
        form = BulkUserActionForm()

    # Get all users for the selection
    users = User.objects.all().order_by('-date_joined')

    context = {
        'form': form,
        'users': users,
        'title': 'Bulk User Actions',
    }

    return render(request, 'admin_app/user_management/user_bulk_actions.html', context)


# Venue management views
@login_required
@user_passes_test(is_admin)
def venue_list(request):
    """View all venues"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get filter parameters
    status = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')

    # Base queryset
    venues = Venue.objects.all()

    # Apply filters
    if status == 'pending':
        venues = venues.filter(approval_status='pending')
    elif status == 'approved':
        venues = venues.filter(approval_status='approved')
    elif status == 'rejected':
        venues = venues.filter(approval_status='rejected')

    # Apply search
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(owner__email__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query)
        )

    # Order by
    venues = venues.order_by('-created_at')

    # Pagination
    paginator = Paginator(venues, preference.items_per_page)
    page = request.GET.get('page')

    try:
        venues = paginator.page(page)
    except PageNotAnInteger:
        venues = paginator.page(1)
    except EmptyPage:
        venues = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'Venue', None, 'Viewed venue list')

    context = {
        'preference': preference,
        'venues': venues,
        'status': status,
        'search_query': search_query,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/venue_management/venue_list.html', context)


@login_required
@user_passes_test(is_admin)
def venue_detail(request, venue_id):
    """View venue details"""
    venue = get_object_or_404(Venue, id=venue_id)

    # Get related data
    services = Service.objects.filter(venue=venue)
    bookings = Booking.objects.filter(venue=venue).order_by('-booking_date')[:10]
    reviews = Review.objects.filter(venue=venue).order_by('-created_at')[:10]

    # Log admin activity
    log_admin_activity(request, 'view', 'Venue', str(venue.id), f'Viewed venue details for {venue.name}')

    context = {
        'venue': venue,
        'services': services,
        'bookings': bookings,
        'reviews': reviews,
    }

    return render(request, 'admin_app/venue_management/venue_detail.html', context)


@login_required
@user_passes_test(is_admin)
def venue_approval(request, venue_id):
    """Approve or reject a venue"""
    venue = get_object_or_404(Venue, id=venue_id)

    # If venue is already approved or rejected, redirect to detail page
    if venue.approval_status != 'pending':
        messages.info(request, f'This venue has already been {venue.approval_status}.')
        return redirect('admin_app:venue_detail', venue_id=venue.id)

    if request.method == 'POST':
        form = VenueApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action')
            rejection_reason = form.cleaned_data.get('rejection_reason')

            if action == 'approve':
                venue.approval_status = 'approved'
                venue.save()

                # Log admin activity
                log_admin_activity(request, 'approve', 'Venue', str(venue.id), f'Approved venue: {venue.name}')

                messages.success(request, f'Venue {venue.name} has been approved successfully.')
            elif action == 'reject':
                venue.approval_status = 'rejected'
                venue.rejection_reason = rejection_reason
                venue.save()

                # Log admin activity
                log_admin_activity(request, 'reject', 'Venue', str(venue.id), f'Rejected venue: {venue.name}')

                messages.success(request, f'Venue {venue.name} has been rejected.')

            return redirect('admin_app:venue_detail', venue_id=venue.id)
    else:
        form = VenueApprovalForm()

    context = {
        'form': form,
        'venue': venue,
    }

    return render(request, 'admin_app/venue_management/venue_approval.html', context)


@login_required
@user_passes_test(is_admin)
def pending_venues(request):
    """View all pending venues"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get pending venues
    venues = Venue.objects.filter(approval_status='pending').order_by('-created_at')

    # Pagination
    paginator = Paginator(venues, preference.items_per_page)
    page = request.GET.get('page')

    try:
        venues = paginator.page(page)
    except PageNotAnInteger:
        venues = paginator.page(1)
    except EmptyPage:
        venues = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'Venue', None, 'Viewed pending venues')

    context = {
        'preference': preference,
        'venues': venues,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/venue_management/pending_venues.html', context)


# System configuration views
@login_required
@user_passes_test(is_admin)
def system_config(request):
    """Configure system settings"""
    # Get system configuration
    config = SystemConfig.get_instance()

    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.last_updated_by = request.user
            config.save()

            # Log admin activity
            log_admin_activity(request, 'update', 'SystemConfig', '1', 'Updated system configuration')

            messages.success(request, 'System configuration has been updated successfully.')
            return redirect('admin_app:system_config')
    else:
        form = SystemConfigForm(instance=config)

    context = {
        'form': form,
        'config': config,
    }

    return render(request, 'admin_app/system/system_config.html', context)


# Audit log views
@login_required
@user_passes_test(is_admin)
def audit_log_list(request):
    """View audit logs"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get filter parameters
    action = request.GET.get('action', 'all')
    model = request.GET.get('model', 'all')
    user_id = request.GET.get('user', 'all')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Base queryset
    logs = AuditLog.objects.all()

    # Apply filters
    if action != 'all':
        logs = logs.filter(action=action)

    if model != 'all':
        logs = logs.filter(model_name=model)

    if user_id != 'all':
        logs = logs.filter(user_id=user_id)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=end_date)
        except ValueError:
            pass

    # Order by
    logs = logs.order_by('-timestamp')

    # Get unique values for filters
    actions = AuditLog.objects.values_list('action', flat=True).distinct()
    models = AuditLog.objects.values_list('model_name', flat=True).distinct()
    users = User.objects.filter(id__in=AuditLog.objects.values_list('user_id', flat=True).distinct())

    # Pagination
    paginator = Paginator(logs, preference.items_per_page)
    page = request.GET.get('page')

    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'AuditLog', None, 'Viewed audit logs')

    context = {
        'preference': preference,
        'logs': logs,
        'actions': actions,
        'models': models,
        'users': users,
        'selected_action': action,
        'selected_model': model,
        'selected_user': user_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/audit/audit_log_list.html', context)


@login_required
@user_passes_test(is_admin)
def audit_log_detail(request, log_id):
    """View audit log details"""
    log = get_object_or_404(AuditLog, id=log_id)

    # Log admin activity
    log_admin_activity(request, 'view', 'AuditLog', str(log.id), f'Viewed audit log details for {log.id}')

    context = {
        'log': log,
    }

    return render(request, 'admin_app/audit/audit_log_detail.html', context)


@login_required
@user_passes_test(is_admin)
def export_audit_logs(request):
    """Export audit logs to CSV"""
    # Get filter parameters
    action = request.GET.get('action', 'all')
    model = request.GET.get('model', 'all')
    user_id = request.GET.get('user', 'all')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Base queryset
    logs = AuditLog.objects.all()

    # Apply filters
    if action != 'all':
        logs = logs.filter(action=action)

    if model != 'all':
        logs = logs.filter(model_name=model)

    if user_id != 'all':
        logs = logs.filter(user_id=user_id)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=end_date)
        except ValueError:
            pass

    # Order by
    logs = logs.order_by('-timestamp')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Action', 'Model', 'Object ID', 'Timestamp', 'IP Address', 'Changes'])

    for log in logs:
        writer.writerow([
            log.id,
            log.user.email if log.user else 'System',
            log.action,
            log.model_name,
            log.object_id,
            log.timestamp,
            log.ip_address or 'N/A',
            json.dumps(log.changes)
        ])

    # Log admin activity
    log_admin_activity(request, 'export', 'AuditLog', None, 'Exported audit logs to CSV')

    return response


# Security monitoring views
@login_required
@user_passes_test(is_admin)
def security_event_list(request):
    """View security events"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get filter parameters
    event_type = request.GET.get('event_type', 'all')
    severity = request.GET.get('severity', 'all')
    status = request.GET.get('status', 'all')
    user_id = request.GET.get('user', 'all')

    # Base queryset
    events = SecurityEvent.objects.all()

    # Apply filters
    if event_type != 'all':
        events = events.filter(event_type=event_type)

    if severity != 'all':
        events = events.filter(severity=severity)

    if status == 'resolved':
        events = events.filter(is_resolved=True)
    elif status == 'unresolved':
        events = events.filter(is_resolved=False)

    if user_id != 'all':
        events = events.filter(user_id=user_id)

    # Order by
    events = events.order_by('-timestamp')

    # Get unique values for filters
    event_types = SecurityEvent.objects.values_list('event_type', flat=True).distinct()
    severities = SecurityEvent.objects.values_list('severity', flat=True).distinct()
    users = User.objects.filter(id__in=SecurityEvent.objects.values_list('user_id', flat=True).distinct())

    # Pagination
    paginator = Paginator(events, preference.items_per_page)
    page = request.GET.get('page')

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'SecurityEvent', None, 'Viewed security events')

    context = {
        'preference': preference,
        'events': events,
        'event_types': event_types,
        'severities': severities,
        'users': users,
        'selected_event_type': event_type,
        'selected_severity': severity,
        'selected_status': status,
        'selected_user': user_id,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/security/security_event_list.html', context)


@login_required
@user_passes_test(is_admin)
def security_event_detail(request, event_id):
    """View security event details"""
    event = get_object_or_404(SecurityEvent, id=event_id)

    # Log admin activity
    log_admin_activity(request, 'view', 'SecurityEvent', str(event.id), f'Viewed security event details for {event.id}')

    context = {
        'event': event,
    }

    return render(request, 'admin_app/security/security_event_detail.html', context)


@login_required
@user_passes_test(is_admin)
def security_event_resolve(request, event_id):
    """Resolve a security event"""
    event = get_object_or_404(SecurityEvent, id=event_id)

    # If event is already resolved, redirect to detail page
    if event.is_resolved:
        messages.info(request, 'This security event has already been resolved.')
        return redirect('admin_app:security_event_detail', event_id=event.id)

    if request.method == 'POST':
        form = SecurityEventResolveForm(request.POST)
        if form.is_valid():
            resolution_notes = form.cleaned_data.get('resolution_notes')

            # Resolve the event
            event.resolve(request.user, resolution_notes)

            # Log admin activity
            log_admin_activity(request, 'update', 'SecurityEvent', str(event.id), f'Resolved security event: {event.id}')

            messages.success(request, 'Security event has been resolved successfully.')
            return redirect('admin_app:security_event_detail', event_id=event.id)
    else:
        form = SecurityEventResolveForm()

    context = {
        'form': form,
        'event': event,
    }

    return render(request, 'admin_app/security/security_event_resolve.html', context)


# Task management views
@login_required
@user_passes_test(is_admin)
def task_list(request):
    """View admin tasks"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get filter parameters
    status = request.GET.get('status', 'all')
    priority = request.GET.get('priority', 'all')
    assigned_to = request.GET.get('assigned_to', 'all')

    # Base queryset
    tasks = AdminTask.objects.all()

    # Apply filters
    if status != 'all':
        tasks = tasks.filter(status=status)

    if priority != 'all':
        tasks = tasks.filter(priority=priority)

    if assigned_to == 'me':
        tasks = tasks.filter(assigned_to=request.user)
    elif assigned_to == 'unassigned':
        tasks = tasks.filter(assigned_to=None)
    elif assigned_to != 'all':
        tasks = tasks.filter(assigned_to_id=assigned_to)

    # Order by
    tasks = tasks.order_by('-created_at')

    # Get unique values for filters
    priorities = AdminTask.PRIORITY_CHOICES
    statuses = AdminTask.STATUS_CHOICES
    admins = User.objects.filter(is_staff=True)

    # Pagination
    paginator = Paginator(tasks, preference.items_per_page)
    page = request.GET.get('page')

    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    # Log admin activity
    log_admin_activity(request, 'view', 'AdminTask', None, 'Viewed admin tasks')

    context = {
        'preference': preference,
        'tasks': tasks,
        'priorities': priorities,
        'statuses': statuses,
        'admins': admins,
        'selected_status': status,
        'selected_priority': priority,
        'selected_assigned_to': assigned_to,
        'total_count': paginator.count,
    }

    return render(request, 'admin_app/tasks/task_list.html', context)


@login_required
@user_passes_test(is_admin)
def task_detail(request, task_id):
    """View task details"""
    task = get_object_or_404(AdminTask, id=task_id)

    # Log admin activity
    log_admin_activity(request, 'view', 'AdminTask', str(task.id), f'Viewed task details for {task.title}')

    context = {
        'task': task,
    }

    return render(request, 'admin_app/tasks/task_detail.html', context)


@login_required
@user_passes_test(is_admin)
def task_create(request):
    """Create a new admin task"""
    if request.method == 'POST':
        form = AdminTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            # Log admin activity
            log_admin_activity(request, 'create', 'AdminTask', str(task.id), f'Created new task: {task.title}')

            messages.success(request, 'Task has been created successfully.')
            return redirect('admin_app:task_detail', task_id=task.id)
    else:
        form = AdminTaskForm()

    context = {
        'form': form,
        'title': 'Create New Task',
    }

    return render(request, 'admin_app/tasks/task_form.html', context)


@login_required
@user_passes_test(is_admin)
def task_edit(request, task_id):
    """Edit an existing admin task"""
    task = get_object_or_404(AdminTask, id=task_id)

    if request.method == 'POST':
        form = AdminTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            # Log admin activity
            log_admin_activity(request, 'update', 'AdminTask', str(task.id), f'Updated task: {task.title}')

            messages.success(request, 'Task has been updated successfully.')
            return redirect('admin_app:task_detail', task_id=task.id)
    else:
        form = AdminTaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'title': f'Edit Task: {task.title}',
    }

    return render(request, 'admin_app/tasks/task_form.html', context)


@login_required
@user_passes_test(is_admin)
def task_delete(request, task_id):
    """Delete an admin task"""
    task = get_object_or_404(AdminTask, id=task_id)

    if request.method == 'POST':
        title = task.title
        task.delete()

        # Log admin activity
        log_admin_activity(request, 'delete', 'AdminTask', task_id, f'Deleted task: {title}')

        messages.success(request, f'Task "{title}" has been deleted successfully.')
        return redirect('admin_app:task_list')

    context = {
        'task': task,
    }

    return render(request, 'admin_app/tasks/task_delete.html', context)


@login_required
@user_passes_test(is_admin)
def task_update_status(request, task_id):
    """Update task status"""
    task = get_object_or_404(AdminTask, id=task_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(AdminTask.STATUS_CHOICES):
            old_status = task.status
            task.status = status
            task.save()

            # Log admin activity
            log_admin_activity(
                request,
                'update',
                'AdminTask',
                str(task.id),
                f'Updated task status from {old_status} to {status}: {task.title}'
            )

            messages.success(request, f'Task status has been updated to {task.get_status_display()}.')

    return redirect('admin_app:task_detail', task_id=task.id)


@login_required
@user_passes_test(is_admin)
def task_mark_completed(request, task_id):
    """Mark task as completed"""
    task = get_object_or_404(AdminTask, id=task_id)

    if request.method == 'POST':
        old_status = task.status
        task.status = 'completed'
        task.save()

        # Log admin activity
        log_admin_activity(
            request,
            'update',
            'AdminTask',
            str(task.id),
            f'Marked task as completed: {task.title}'
        )

        messages.success(request, f'Task has been marked as completed.')

    return redirect('admin_app:task_detail', task_id=task.id)


@login_required
@user_passes_test(is_admin)
def task_mark_cancelled(request, task_id):
    """Mark task as cancelled"""
    task = get_object_or_404(AdminTask, id=task_id)

    if request.method == 'POST':
        old_status = task.status
        task.status = 'cancelled'
        task.save()

        # Log admin activity
        log_admin_activity(
            request,
            'update',
            'AdminTask',
            str(task.id),
            f'Marked task as cancelled: {task.title}'
        )

        messages.success(request, f'Task has been cancelled.')

    return redirect('admin_app:task_detail', task_id=task.id)


# Admin preferences views
@login_required
@user_passes_test(is_admin)
def admin_preferences(request):
    """Edit admin preferences"""
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get form data
        theme = request.POST.get('theme')
        sidebar_collapsed = request.POST.get('sidebar_collapsed') == 'on'
        show_quick_actions = request.POST.get('show_quick_actions') == 'on'
        items_per_page = int(request.POST.get('items_per_page', 20))

        # Update preference
        preference.theme = theme
        preference.sidebar_collapsed = sidebar_collapsed
        preference.show_quick_actions = show_quick_actions
        preference.items_per_page = items_per_page
        preference.save()

        # Log admin activity
        log_admin_activity(request, 'update', 'AdminPreference', str(preference.id), 'Updated admin preferences')

        messages.success(request, 'Preferences have been updated successfully.')
        return redirect('admin_app:admin_dashboard')

    context = {
        'preference': preference,
    }

    return render(request, 'admin_app/preferences.html', context)


# Analytics and reporting views
@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """View analytics dashboard"""
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})

    # Get user statistics
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__date__range=[start_date, end_date]).count()
    active_users = User.objects.filter(last_login__date__range=[start_date, end_date]).count()

    # Get venue statistics
    total_venues = Venue.objects.count()
    new_venues = Venue.objects.filter(created_at__date__range=[start_date, end_date]).count()
    approved_venues = Venue.objects.filter(approval_status='approved').count()

    # Get booking statistics
    total_bookings = Booking.objects.count()
    new_bookings = Booking.objects.filter(booking_date__date__range=[start_date, end_date]).count()
    completed_bookings = Booking.objects.filter(status='completed').count()

    # Get revenue statistics
    total_revenue = Booking.objects.filter(status__in=['confirmed', 'completed']).aggregate(total=Sum('total_price'))['total'] or 0
    period_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed'],
        booking_date__date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Get daily statistics
    daily_stats = {}
    current_date = start_date
    while current_date <= end_date:
        # Get new users for this day
        day_new_users = User.objects.filter(date_joined__date=current_date).count()

        # Get new bookings for this day
        day_new_bookings = Booking.objects.filter(booking_date__date=current_date).count()

        # Get revenue for this day
        day_revenue = Booking.objects.filter(
            status__in=['confirmed', 'completed'],
            booking_date__date=current_date
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Store daily stats
        daily_stats[current_date.strftime('%Y-%m-%d')] = {
            'date': current_date,
            'new_users': day_new_users,
            'new_bookings': day_new_bookings,
            'revenue': day_revenue,
        }

        current_date += timedelta(days=1)

    # Log admin activity
    log_admin_activity(request, 'view', 'Analytics', None, 'Viewed analytics dashboard')

    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': total_users,
        'new_users': new_users,
        'active_users': active_users,
        'total_venues': total_venues,
        'new_venues': new_venues,
        'approved_venues': approved_venues,
        'total_bookings': total_bookings,
        'new_bookings': new_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': total_revenue,
        'period_revenue': period_revenue,
        'daily_stats': daily_stats,
    }

    return render(request, 'admin_app/analytics/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def export_analytics(request):
    """Export analytics data to CSV"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)  # Default to last 30 days
    else:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)  # Default to last 30 days

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'New Users', 'New Bookings', 'Revenue'])

    # Get daily statistics
    current_date = start_date
    while current_date <= end_date:
        # Get new users for this day
        day_new_users = User.objects.filter(date_joined__date=current_date).count()

        # Get new bookings for this day
        day_new_bookings = Booking.objects.filter(booking_date__date=current_date).count()

        # Get revenue for this day
        day_revenue = Booking.objects.filter(
            status__in=['confirmed', 'completed'],
            booking_date__date=current_date
        ).aggregate(total=Sum('total_price'))['total'] or 0

        writer.writerow([
            current_date,
            day_new_users,
            day_new_bookings,
            day_revenue
        ])

        current_date += timedelta(days=1)

    # Log admin activity
    log_admin_activity(request, 'export', 'Analytics', None, 'Exported analytics data to CSV')

    return response


@login_required
@user_passes_test(is_admin)
def user_report(request):
    """Generate user report"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})

    # Get user statistics
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__date__range=[start_date, end_date])
    active_users = User.objects.filter(last_login__date__range=[start_date, end_date])

    # Get user types
    customer_count = User.objects.filter(is_customer=True).count()
    provider_count = User.objects.filter(is_service_provider=True).count()
    staff_count = User.objects.filter(is_staff=True).count()

    # Get user activity
    most_active_users = User.objects.annotate(
        login_count=Count('admin_activities', filter=Q(admin_activities__action_type='login'))
    ).order_by('-login_count')[:10]

    # Get new users by day
    new_users_by_day = {}
    current_date = start_date
    while current_date <= end_date:
        day_new_users = User.objects.filter(date_joined__date=current_date).count()
        new_users_by_day[current_date.strftime('%Y-%m-%d')] = day_new_users
        current_date += timedelta(days=1)

    # Log admin activity
    log_admin_activity(request, 'view', 'UserReport', None, 'Viewed user report')

    context = {
        'preference': preference,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': total_users,
        'new_users': new_users,
        'active_users': active_users,
        'customer_count': customer_count,
        'provider_count': provider_count,
        'staff_count': staff_count,
        'most_active_users': most_active_users,
        'new_users_by_day': new_users_by_day,
    }

    return render(request, 'admin_app/analytics/user_report.html', context)


@login_required
@user_passes_test(is_admin)
def booking_report(request):
    """Generate booking report"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})

    # Get booking statistics
    total_bookings = Booking.objects.count()
    period_bookings = Booking.objects.filter(booking_date__date__range=[start_date, end_date])

    # Get booking status counts
    pending_count = Booking.objects.filter(status='pending').count()
    confirmed_count = Booking.objects.filter(status='confirmed').count()
    completed_count = Booking.objects.filter(status='completed').count()
    cancelled_count = Booking.objects.filter(status='cancelled').count()

    # Get top venues by bookings
    top_venues = Venue.objects.annotate(
        booking_count=Count('booking_cart_app_bookings')
    ).order_by('-booking_count')[:10]

    # Get bookings by day
    bookings_by_day = {}
    current_date = start_date
    while current_date <= end_date:
        day_bookings = Booking.objects.filter(booking_date__date=current_date).count()
        bookings_by_day[current_date.strftime('%Y-%m-%d')] = day_bookings
        current_date += timedelta(days=1)

    # Log admin activity
    log_admin_activity(request, 'view', 'BookingReport', None, 'Viewed booking report')

    context = {
        'preference': preference,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_bookings': total_bookings,
        'period_bookings': period_bookings,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'top_venues': top_venues,
        'bookings_by_day': bookings_by_day,
    }

    return render(request, 'admin_app/analytics/booking_report.html', context)


@login_required
@user_passes_test(is_admin)
def revenue_report(request):
    """Generate revenue report"""
    # Get admin preferences
    preference, created = AdminPreference.objects.get_or_create(user=request.user)

    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})

    # Get revenue statistics
    total_revenue = Booking.objects.filter(status__in=['confirmed', 'completed']).aggregate(total=Sum('total_price'))['total'] or 0
    period_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed'],
        booking_date__date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Get top venues by revenue
    top_venues_by_revenue = Venue.objects.annotate(
        revenue=Sum('booking_cart_app_bookings__total_price', filter=Q(booking_cart_app_bookings__status__in=['confirmed', 'completed']))
    ).filter(revenue__isnull=False).order_by('-revenue')[:10]

    # Get revenue by day
    revenue_by_day = {}
    current_date = start_date
    while current_date <= end_date:
        day_revenue = Booking.objects.filter(
            status__in=['confirmed', 'completed'],
            booking_date__date=current_date
        ).aggregate(total=Sum('total_price'))['total'] or 0
        revenue_by_day[current_date.strftime('%Y-%m-%d')] = day_revenue
        current_date += timedelta(days=1)

    # Log admin activity
    log_admin_activity(request, 'view', 'RevenueReport', None, 'Viewed revenue report')

    context = {
        'preference': preference,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'period_revenue': period_revenue,
        'top_venues_by_revenue': top_venues_by_revenue,
        'revenue_by_day': revenue_by_day,
    }

    return render(request, 'admin_app/analytics/revenue_report.html', context)
