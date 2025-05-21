from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Notification, UserNotification, NotificationCategory, NotificationPreference
from .forms import NotificationPreferenceForm, SystemAnnouncementForm, NotificationCategoryForm
from .utils import (
    create_notification, get_user_notifications, mark_all_as_read,
    create_system_announcement, get_unread_count
)


# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff


# Customer and Service Provider Views
@login_required
def notification_list(request):
    """View for users to see their notifications"""
    # Get filter parameters
    show_read = request.GET.get('show_read') == 'true'
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')

    # Get notifications
    notifications = get_user_notifications(request.user, include_read=show_read)

    # Apply category filter if provided
    if category_id:
        notifications = notifications.filter(notification__category_id=category_id)

    # Apply search filter if provided
    if search_query:
        notifications = notifications.filter(
            Q(notification__title__icontains=search_query) |
            Q(notification__message__icontains=search_query)
        )

    # Get categories for filter dropdown
    categories = NotificationCategory.objects.filter(
        notifications__user_notifications__user=request.user
    ).distinct()

    # Paginate results
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page = request.GET.get('page')

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    context = {
        'notifications': notifications_page,
        'categories': categories,
        'show_read': show_read,
        'selected_category': category_id,
        'search_query': search_query,
        'unread_count': get_unread_count(request.user),
    }

    return render(request, 'notifications_app/notification_list.html', context)


@login_required
def notification_detail(request, notification_id):
    """View for users to see a specific notification"""
    user_notification = get_object_or_404(
        UserNotification,
        notification_id=notification_id,
        user=request.user,
        is_deleted=False
    )

    # Mark as read if not already read
    if not user_notification.is_read:
        user_notification.mark_as_read()

    # Get related object if any
    related_object = None
    if user_notification.notification.content_object:
        related_object = user_notification.notification.content_object

    context = {
        'notification': user_notification,
        'related_object': related_object,
    }

    return render(request, 'notifications_app/notification_detail.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        user_notification = get_object_or_404(
            UserNotification,
            notification_id=notification_id,
            user=request.user
        )

        user_notification.mark_as_read()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'unread_count': get_unread_count(request.user)})

        return redirect('notifications_app:notification_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def mark_notification_unread(request, notification_id):
    """Mark a notification as unread"""
    if request.method == 'POST':
        user_notification = get_object_or_404(
            UserNotification,
            notification_id=notification_id,
            user=request.user
        )

        user_notification.mark_as_unread()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'unread_count': get_unread_count(request.user)})

        return redirect('notifications_app:notification_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    if request.method == 'POST':
        user_notification = get_object_or_404(
            UserNotification,
            notification_id=notification_id,
            user=request.user
        )

        user_notification.delete_notification()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, 'Notification deleted successfully.')
        return redirect('notifications_app:notification_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        count = mark_all_as_read(request.user)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'count': count, 'unread_count': 0})

        messages.success(request, f'{count} notifications marked as read.')
        return redirect('notifications_app:notification_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def notification_preferences(request):
    """View for users to manage their notification preferences"""
    # Get all categories
    categories = NotificationCategory.objects.all()

    # Get or create preferences for each category
    preferences = []
    for category in categories:
        preference, created = NotificationPreference.objects.get_or_create(
            user=request.user,
            category=category,
            defaults={'channel': 'both', 'is_enabled': True}
        )
        preferences.append({
            'category': category,
            'preference': preference,
            'form': NotificationPreferenceForm(instance=preference)
        })

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        if category_id:
            category = get_object_or_404(NotificationCategory, id=category_id)
            preference = get_object_or_404(NotificationPreference, user=request.user, category=category)
            form = NotificationPreferenceForm(request.POST, instance=preference)

            if form.is_valid():
                form.save()
                messages.success(request, f'Preferences for {category.name} updated successfully.')
                return redirect('notifications_app:notification_preferences')

    context = {
        'preferences': preferences,
    }

    return render(request, 'notifications_app/notification_preferences.html', context)


@login_required
def get_unread_notifications(request):
    """AJAX view to get unread notifications for the navbar dropdown"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        notifications = get_user_notifications(request.user)[:5]  # Get 5 most recent unread notifications
        unread_count = get_unread_count(request.user)

        notifications_data = [{
            'id': n.notification.id,
            'title': n.notification.title,
            'message': n.notification.message[:100] + '...' if len(n.notification.message) > 100 else n.notification.message,
            'created_at': n.notification.created_at.strftime('%b %d, %Y, %I:%M %p'),
            'category': n.notification.category.name,
            'priority': n.notification.priority,
        } for n in notifications]

        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count,
            'more_url': reverse('notifications_app:notification_list')
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_notification_dashboard(request):
    """Admin dashboard for notifications"""
    # Get counts
    total_notifications = Notification.objects.count()
    active_notifications = Notification.objects.filter(is_active=True).count()
    system_wide_notifications = Notification.objects.filter(is_system_wide=True).count()

    # Get active system-wide notifications
    active_announcements = Notification.objects.filter(
        is_system_wide=True,
        is_active=True,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')[:5]

    # Get notification categories
    categories = NotificationCategory.objects.all()

    # Get recent notifications
    recent_notifications = Notification.objects.all().order_by('-created_at')[:10]

    context = {
        'total_notifications': total_notifications,
        'active_notifications': active_notifications,
        'system_wide_notifications': system_wide_notifications,
        'active_announcements': active_announcements,
        'categories': categories,
        'recent_notifications': recent_notifications,
    }

    return render(request, 'notifications_app/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_announcement(request):
    """Admin view to create a system-wide announcement"""
    if request.method == 'POST':
        form = SystemAnnouncementForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            priority = form.cleaned_data['priority']
            expires_in_days = form.cleaned_data['expires_in_days']

            create_system_announcement(title, message, expires_in_days)

            messages.success(request, 'System announcement created successfully.')
            return redirect('notifications_app:admin_notification_dashboard')
    else:
        form = SystemAnnouncementForm()

    context = {
        'form': form,
        'title': 'Create System Announcement',
    }

    return render(request, 'notifications_app/admin/announcement_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_categories(request):
    """Admin view to manage notification categories"""
    categories = NotificationCategory.objects.all()

    context = {
        'categories': categories,
    }

    return render(request, 'notifications_app/admin/category_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_category(request):
    """Admin view to create a notification category"""
    if request.method == 'POST':
        form = NotificationCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification category created successfully.')
            return redirect('notifications_app:admin_manage_categories')
    else:
        form = NotificationCategoryForm()

    context = {
        'form': form,
        'title': 'Create Notification Category',
    }

    return render(request, 'notifications_app/admin/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_category(request, category_id):
    """Admin view to edit a notification category"""
    category = get_object_or_404(NotificationCategory, id=category_id)

    if request.method == 'POST':
        form = NotificationCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification category updated successfully.')
            return redirect('notifications_app:admin_manage_categories')
    else:
        form = NotificationCategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'title': 'Edit Notification Category',
    }

    return render(request, 'notifications_app/admin/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_category(request, category_id):
    """Admin view to delete a notification category"""
    category = get_object_or_404(NotificationCategory, id=category_id)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Notification category "{category_name}" deleted successfully.')
        return redirect('notifications_app:admin_manage_categories')

    context = {
        'category': category,
    }

    return render(request, 'notifications_app/admin/category_delete.html', context)


@login_required
@user_passes_test(is_admin)
def admin_notification_list(request):
    """Admin view to list all notifications"""
    # Get filter parameters
    category_id = request.GET.get('category')
    is_system_wide = request.GET.get('is_system_wide')
    is_active = request.GET.get('is_active')
    search_query = request.GET.get('search')

    # Start with all notifications
    notifications = Notification.objects.all()

    # Apply filters
    if category_id:
        notifications = notifications.filter(category_id=category_id)

    if is_system_wide == 'true':
        notifications = notifications.filter(is_system_wide=True)

    if is_active == 'true':
        notifications = notifications.filter(is_active=True)
    elif is_active == 'false':
        notifications = notifications.filter(is_active=False)

    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    # Get categories for filter dropdown
    categories = NotificationCategory.objects.all()

    # Paginate results
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page = request.GET.get('page')

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    context = {
        'notifications': notifications_page,
        'categories': categories,
        'selected_category': category_id,
        'is_system_wide': is_system_wide,
        'is_active': is_active,
        'search_query': search_query,
    }

    return render(request, 'notifications_app/admin/notification_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_notification_detail(request, notification_id):
    """Admin view to see notification details"""
    notification = get_object_or_404(Notification, id=notification_id)

    # Get users who received this notification
    user_notifications = UserNotification.objects.filter(notification=notification)

    # Get read/unread counts
    total_recipients = user_notifications.count()
    read_count = user_notifications.filter(is_read=True).count()
    unread_count = total_recipients - read_count

    context = {
        'notification': notification,
        'user_notifications': user_notifications,
        'total_recipients': total_recipients,
        'read_count': read_count,
        'unread_count': unread_count,
    }

    return render(request, 'notifications_app/admin/notification_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_deactivate_notification(request, notification_id):
    """Admin view to deactivate a notification"""
    notification = get_object_or_404(Notification, id=notification_id)

    if request.method == 'POST':
        notification.is_active = False
        notification.save()
        messages.success(request, 'Notification deactivated successfully.')
        return redirect('notifications_app:admin_notification_detail', notification_id=notification.id)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def test_view(request):
    """Simple test view to check if the app is working"""
    return render(request, 'notifications_app/test.html', {'message': 'Notifications app is working!'})
