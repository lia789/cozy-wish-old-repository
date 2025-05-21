from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta

from accounts_app.models import CustomUser
from venues_app.models import Venue, Service, Review
from booking_cart_app.models import Booking, BookingItem
from payments_app.models import Transaction, Invoice

from .forms import DateRangeForm


@login_required
def dashboard_redirect(request):
    """Redirect to the appropriate dashboard based on user type"""
    if request.user.is_customer:
        return redirect('dashboard_app:customer_dashboard')
    elif request.user.is_service_provider:
        return redirect('dashboard_app:provider_dashboard')
    elif request.user.is_staff:
        return redirect('dashboard_app:admin_dashboard')
    else:
        messages.error(request, "You don't have access to a dashboard.")
        return redirect('venues_app:home')


@login_required
def customer_dashboard(request):
    """Main dashboard view for customers"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Dashboard preferences have been removed as per requirements

    # Get recent bookings
    recent_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:5]

    # Get upcoming bookings
    today = timezone.now().date()
    upcoming_bookings = []
    for booking in Booking.objects.filter(user=request.user, status='confirmed'):
        booking_items = booking.items.filter(date__gte=today).order_by('date', 'time_slot')
        if booking_items.exists():
            upcoming_bookings.append({
                'booking': booking,
                'next_item': booking_items.first()
            })

    # Sort upcoming bookings by date and time
    upcoming_bookings.sort(key=lambda x: timezone.make_aware(
        timezone.datetime.combine(x['next_item'].date, x['next_item'].time_slot)
    ))
    upcoming_bookings = upcoming_bookings[:5]

    # Get recent reviews
    recent_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'recent_bookings': recent_bookings,
        'upcoming_bookings': upcoming_bookings,
        'recent_reviews': recent_reviews,
    }

    return render(request, 'dashboard_app/customer/dashboard.html', context)


@login_required
def provider_dashboard(request):
    """Main dashboard view for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Dashboard preferences have been removed as per requirements

    # Get provider's venues
    venues = Venue.objects.filter(owner=request.user)

    # Get today's bookings
    today = timezone.now().date()
    todays_bookings = Booking.objects.filter(
        venue__in=venues,
        items__date=today
    ).distinct().order_by('booking_date')

    # Get recent bookings
    recent_bookings = Booking.objects.filter(venue__in=venues).order_by('-booking_date')[:5]

    # Get booking statistics
    total_bookings = Booking.objects.filter(venue__in=venues).count()
    pending_bookings = Booking.objects.filter(venue__in=venues, status='pending').count()
    confirmed_bookings = Booking.objects.filter(venue__in=venues, status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(venue__in=venues, status='cancelled').count()

    # Get revenue statistics
    total_revenue = Booking.objects.filter(
        venue__in=venues,
        status='confirmed'
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Get recent reviews
    recent_reviews = Review.objects.filter(venue__in=venues).order_by('-created_at')[:5]

    context = {
        'venues': venues,
        'todays_bookings': todays_bookings,
        'recent_bookings': recent_bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'recent_reviews': recent_reviews,
    }

    return render(request, 'dashboard_app/provider/dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Main dashboard view for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Dashboard preferences have been removed as per requirements

    # Get user statistics
    total_users = CustomUser.objects.count()
    customer_count = CustomUser.objects.filter(is_customer=True).count()
    provider_count = CustomUser.objects.filter(is_service_provider=True).count()
    staff_count = CustomUser.objects.filter(is_staff=True).count()

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
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_price'))['total'] or 0

    # Get recent bookings
    recent_bookings = Booking.objects.all().order_by('-booking_date')[:10]

    # Get recent reviews
    recent_reviews = Review.objects.all().order_by('-created_at')[:10]

    context = {
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
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
    }

    return render(request, 'dashboard_app/admin/dashboard.html', context)


@login_required
def customer_booking_history(request):
    """View booking history for customers"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Get date range form
    form = DateRangeForm(request.GET or None)

    # Default to last 30 days if no date range specified
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if form.is_valid():
        period = form.cleaned_data.get('period')
        custom_start = form.cleaned_data.get('start_date')
        custom_end = form.cleaned_data.get('end_date')

        if period == 'today':
            start_date = end_date
        elif period == 'yesterday':
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif period == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == 'last_week':
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif period == 'this_month':
            start_date = end_date.replace(day=1)
        elif period == 'last_month':
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
            end_date = start_date.replace(day=1) + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = end_date.replace(month=1, day=1)
        elif period == 'last_year':
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end

    # Get bookings for the date range
    bookings = Booking.objects.filter(
        user=request.user,
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    ).order_by('-booking_date')

    context = {
        'bookings': bookings,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'dashboard_app/customer/booking_history.html', context)


@login_required
def customer_active_bookings(request):
    """View active bookings for customers"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Get active bookings (confirmed and not completed)
    active_bookings = Booking.objects.filter(
        user=request.user,
        status='confirmed'
    ).order_by('booking_date')

    # Get upcoming booking items
    today = timezone.now().date()
    now = timezone.now()
    upcoming_booking_items = []

    for booking in active_bookings:
        items = booking.items.filter(date__gte=today).order_by('date', 'time_slot')
        if items.exists():
            for item in items:
                upcoming_booking_items.append({
                    'booking': booking,
                    'item': item,
                    'datetime': timezone.make_aware(timezone.datetime.combine(item.date, item.time_slot))
                })

    # Sort by date and time
    upcoming_booking_items.sort(key=lambda x: x['datetime'])

    context = {
        'active_bookings': active_bookings,
        'upcoming_booking_items': upcoming_booking_items,
        'now': now,
    }

    return render(request, 'dashboard_app/customer/active_bookings.html', context)


@login_required
def customer_favorite_venues(request):
    """View favorite venues for customers"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Get venues the customer has booked before
    booked_venues = Venue.objects.filter(
        bookings__user=request.user
    ).distinct()

    # Get venues the customer has reviewed
    reviewed_venues = Venue.objects.filter(
        reviews__user=request.user
    ).distinct()

    # Combine and remove duplicates
    favorite_venues = (booked_venues | reviewed_venues).distinct()

    # Get booking count for each venue
    venue_booking_counts = {}
    for venue in favorite_venues:
        venue_booking_counts[venue.id] = Booking.objects.filter(
            user=request.user,
            venue=venue
        ).count()

    # Get review for each venue
    venue_reviews = {}
    for venue in favorite_venues:
        review = Review.objects.filter(user=request.user, venue=venue).first()
        venue_reviews[venue.id] = review

    context = {
        'favorite_venues': favorite_venues,
        'venue_booking_counts': venue_booking_counts,
        'venue_reviews': venue_reviews,
    }

    return render(request, 'dashboard_app/customer/favorite_venues.html', context)


@login_required
def customer_profile_management(request):
    """View and edit customer profile"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Redirect to the accounts app profile view
    return redirect('accounts_app:customer_profile')


@login_required
def customer_review_history(request):
    """View review history for customers"""
    if not request.user.is_customer:
        messages.error(request, "You don't have access to the customer dashboard.")
        return redirect('venues_app:home')

    # Get all reviews by the customer
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'reviews': reviews,
    }

    return render(request, 'dashboard_app/customer/review_history.html', context)


@login_required
def provider_todays_bookings(request):
    """View today's bookings for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Get provider's venues
    venues = Venue.objects.filter(owner=request.user)

    # Get today's date
    today = timezone.now().date()

    # Get bookings for today
    todays_bookings = Booking.objects.filter(
        venue__in=venues,
        items__date=today
    ).distinct().order_by('booking_date')

    # Get booking items for today
    booking_items = []
    for booking in todays_bookings:
        items = booking.items.filter(date=today).order_by('time_slot')
        for item in items:
            booking_items.append({
                'booking': booking,
                'item': item,
                'datetime': timezone.make_aware(timezone.datetime.combine(item.date, item.time_slot))
            })

    # Sort by time
    booking_items.sort(key=lambda x: x['datetime'])

    context = {
        'today': today,
        'todays_bookings': todays_bookings,
        'booking_items': booking_items,
        'venues': venues,
    }

    return render(request, 'dashboard_app/provider/todays_bookings.html', context)


@login_required
def provider_revenue_reports(request):
    """View revenue reports for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Get date range form
    form = DateRangeForm(request.GET or None)

    # Default to last 30 days if no date range specified
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if form.is_valid():
        period = form.cleaned_data.get('period')
        custom_start = form.cleaned_data.get('start_date')
        custom_end = form.cleaned_data.get('end_date')

        if period == 'today':
            start_date = end_date
        elif period == 'yesterday':
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif period == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == 'last_week':
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif period == 'this_month':
            start_date = end_date.replace(day=1)
        elif period == 'last_month':
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
            end_date = start_date.replace(day=1) + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = end_date.replace(month=1, day=1)
        elif period == 'last_year':
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end

    # Get provider's venues
    venues = Venue.objects.filter(owner=request.user)

    # Get bookings for the date range
    bookings = Booking.objects.filter(
        venue__in=venues,
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date,
        status='confirmed'
    ).order_by('-booking_date')

    # Calculate total revenue
    total_revenue = bookings.aggregate(total=Sum('total_price'))['total'] or 0

    # Calculate revenue by venue
    revenue_by_venue = {}
    for venue in venues:
        venue_revenue = bookings.filter(venue=venue).aggregate(total=Sum('total_price'))['total'] or 0
        revenue_by_venue[venue.id] = venue_revenue

    # Calculate revenue by day
    revenue_by_day = {}
    current_date = start_date
    while current_date <= end_date:
        day_revenue = bookings.filter(
            booking_date__date=current_date
        ).aggregate(total=Sum('total_price'))['total'] or 0
        revenue_by_day[current_date.strftime('%Y-%m-%d')] = day_revenue
        current_date += timedelta(days=1)

    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'bookings': bookings,
        'venues': venues,
        'total_revenue': total_revenue,
        'revenue_by_venue': revenue_by_venue,
        'revenue_by_day': revenue_by_day,
    }

    return render(request, 'dashboard_app/provider/revenue_reports.html', context)


@login_required
def provider_service_performance(request):
    """View service performance metrics for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Get provider's venues
    venues = Venue.objects.filter(owner=request.user)

    # Get all services for the provider's venues
    services = Service.objects.filter(venue__in=venues, is_active=True)

    # Get booking items for each service
    service_metrics = {}
    for service in services:
        # Get booking items for this service
        booking_items = BookingItem.objects.filter(service=service)

        # Count total bookings
        total_bookings = booking_items.count()

        # Calculate total revenue
        total_revenue = booking_items.aggregate(total=Sum('service_price'))['total'] or 0

        # Store metrics
        service_metrics[service.id] = {
            'service': service,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'average_price': total_revenue / total_bookings if total_bookings > 0 else 0,
        }

    # Sort services by total revenue (descending)
    sorted_services = sorted(
        service_metrics.values(),
        key=lambda x: x['total_revenue'],
        reverse=True
    )

    context = {
        'venues': venues,
        'services': services,
        'service_metrics': service_metrics,
        'sorted_services': sorted_services,
    }

    return render(request, 'dashboard_app/provider/service_performance.html', context)


@login_required
def provider_discount_performance(request):
    """View discount campaign performance for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Get provider's venues
    venues = Venue.objects.filter(owner=request.user)

    # Get all services with discounts
    discounted_services = Service.objects.filter(
        venue__in=venues,
        is_active=True,
        discounted_price__isnull=False
    )

    # Get booking items for each discounted service
    discount_metrics = {}
    for service in discounted_services:
        # Get booking items for this service
        booking_items = BookingItem.objects.filter(service=service)

        # Count total bookings
        total_bookings = booking_items.count()

        # Calculate total revenue
        total_revenue = booking_items.aggregate(total=Sum('service_price'))['total'] or 0

        # Calculate discount percentage
        discount_percentage = service.get_discount_percentage()

        # Calculate savings for customers
        savings = (service.price - service.discounted_price) * total_bookings

        # Store metrics
        discount_metrics[service.id] = {
            'service': service,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'discount_percentage': discount_percentage,
            'savings': savings,
        }

    # Sort services by total bookings (descending)
    sorted_discounts = sorted(
        discount_metrics.values(),
        key=lambda x: x['total_bookings'],
        reverse=True
    )

    context = {
        'venues': venues,
        'discounted_services': discounted_services,
        'discount_metrics': discount_metrics,
        'sorted_discounts': sorted_discounts,
    }

    return render(request, 'dashboard_app/provider/discount_performance.html', context)


@login_required
def provider_team_management(request):
    """View and manage team members for service providers"""
    if not request.user.is_service_provider:
        messages.error(request, "You don't have access to the service provider dashboard.")
        return redirect('venues_app:home')

    # Redirect to the accounts app staff list view
    return redirect('accounts_app:staff_list')


@login_required
def admin_platform_overview(request):
    """View platform overview metrics for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Get date range form
    form = DateRangeForm(request.GET or None)

    # Default to last 30 days if no date range specified
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if form.is_valid():
        period = form.cleaned_data.get('period')
        custom_start = form.cleaned_data.get('start_date')
        custom_end = form.cleaned_data.get('end_date')

        if period == 'today':
            start_date = end_date
        elif period == 'yesterday':
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif period == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == 'last_week':
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif period == 'this_month':
            start_date = end_date.replace(day=1)
        elif period == 'last_month':
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
            end_date = start_date.replace(day=1) + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = end_date.replace(month=1, day=1)
        elif period == 'last_year':
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end

    # Get user statistics
    total_users = CustomUser.objects.count()
    new_users = CustomUser.objects.filter(
        date_joined__date__gte=start_date,
        date_joined__date__lte=end_date
    ).count()
    customer_count = CustomUser.objects.filter(is_customer=True).count()
    provider_count = CustomUser.objects.filter(is_service_provider=True).count()

    # Get venue statistics
    total_venues = Venue.objects.count()
    new_venues = Venue.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).count()
    pending_venues = Venue.objects.filter(approval_status='pending').count()
    approved_venues = Venue.objects.filter(approval_status='approved').count()

    # Get booking statistics
    total_bookings = Booking.objects.count()
    new_bookings = Booking.objects.filter(
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    ).count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()

    # Get revenue statistics
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_price'))['total'] or 0
    period_revenue = Booking.objects.filter(
        status='confirmed',
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Get daily statistics for the period
    daily_stats = {}
    current_date = start_date
    while current_date <= end_date:
        # Get new users for this day
        day_new_users = CustomUser.objects.filter(
            date_joined__date=current_date
        ).count()

        # Get new bookings for this day
        day_new_bookings = Booking.objects.filter(
            booking_date__date=current_date
        ).count()

        # Get revenue for this day
        day_revenue = Booking.objects.filter(
            status='confirmed',
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

    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': total_users,
        'new_users': new_users,
        'customer_count': customer_count,
        'provider_count': provider_count,
        'total_venues': total_venues,
        'new_venues': new_venues,
        'pending_venues': pending_venues,
        'approved_venues': approved_venues,
        'total_bookings': total_bookings,
        'new_bookings': new_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'period_revenue': period_revenue,
        'daily_stats': daily_stats,
    }

    return render(request, 'dashboard_app/admin/platform_overview.html', context)


@login_required
def admin_user_statistics(request):
    """View user statistics for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Get date range form
    form = DateRangeForm(request.GET or None)

    # Default to last 30 days if no date range specified
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if form.is_valid():
        period = form.cleaned_data.get('period')
        custom_start = form.cleaned_data.get('start_date')
        custom_end = form.cleaned_data.get('end_date')

        if period == 'today':
            start_date = end_date
        elif period == 'yesterday':
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif period == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == 'last_week':
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif period == 'this_month':
            start_date = end_date.replace(day=1)
        elif period == 'last_month':
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
            end_date = start_date.replace(day=1) + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = end_date.replace(month=1, day=1)
        elif period == 'last_year':
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end

    # Get all users
    all_users = CustomUser.objects.all()

    # Get user counts by type
    total_users = all_users.count()
    customer_count = all_users.filter(is_customer=True).count()
    provider_count = all_users.filter(is_service_provider=True).count()
    staff_count = all_users.filter(is_staff=True).count()

    # Get new users in the period
    new_users = all_users.filter(
        date_joined__date__gte=start_date,
        date_joined__date__lte=end_date
    )
    new_users_count = new_users.count()
    new_customers = new_users.filter(is_customer=True).count()
    new_providers = new_users.filter(is_service_provider=True).count()

    # Get active users (users with bookings in the period)
    active_users = CustomUser.objects.filter(
        bookings__booking_date__date__gte=start_date,
        bookings__booking_date__date__lte=end_date
    ).distinct()
    active_users_count = active_users.count()

    # Get user registration by day
    daily_registrations = {}
    current_date = start_date
    while current_date <= end_date:
        day_users = all_users.filter(date_joined__date=current_date)
        day_customers = day_users.filter(is_customer=True).count()
        day_providers = day_users.filter(is_service_provider=True).count()

        daily_registrations[current_date.strftime('%Y-%m-%d')] = {
            'date': current_date,
            'total': day_users.count(),
            'customers': day_customers,
            'providers': day_providers,
        }

        current_date += timedelta(days=1)

    # Get top 10 most active customers (by number of bookings)
    top_customers = CustomUser.objects.filter(is_customer=True).annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:10]

    # Get top 10 service providers (by number of bookings received)
    top_providers = CustomUser.objects.filter(is_service_provider=True).annotate(
        venue_count=Count('venues'),
        booking_count=Count('venues__bookings')
    ).order_by('-booking_count')[:10]

    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': total_users,
        'customer_count': customer_count,
        'provider_count': provider_count,
        'staff_count': staff_count,
        'new_users_count': new_users_count,
        'new_customers': new_customers,
        'new_providers': new_providers,
        'active_users_count': active_users_count,
        'daily_registrations': daily_registrations,
        'top_customers': top_customers,
        'top_providers': top_providers,
    }

    return render(request, 'dashboard_app/admin/user_statistics.html', context)


@login_required
def admin_booking_analytics(request):
    """View booking analytics for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Redirect to the booking_cart_app admin booking analytics view
    return redirect('booking_cart_app:admin_booking_analytics')


@login_required
def admin_revenue_tracking(request):
    """View revenue tracking for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Get date range form
    form = DateRangeForm(request.GET or None)

    # Default to last 30 days if no date range specified
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if form.is_valid():
        period = form.cleaned_data.get('period')
        custom_start = form.cleaned_data.get('start_date')
        custom_end = form.cleaned_data.get('end_date')

        if period == 'today':
            start_date = end_date
        elif period == 'yesterday':
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif period == 'this_week':
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == 'last_week':
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif period == 'this_month':
            start_date = end_date.replace(day=1)
        elif period == 'last_month':
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
            end_date = start_date.replace(day=1) + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = end_date.replace(month=1, day=1)
        elif period == 'last_year':
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end

    # Get confirmed bookings for the period
    bookings = Booking.objects.filter(
        status='confirmed',
        booking_date__date__gte=start_date,
        booking_date__date__lte=end_date
    )

    # Calculate total revenue
    total_revenue = bookings.aggregate(total=Sum('total_price'))['total'] or 0

    # Calculate revenue by day
    daily_revenue = {}
    current_date = start_date
    while current_date <= end_date:
        day_revenue = bookings.filter(
            booking_date__date=current_date
        ).aggregate(total=Sum('total_price'))['total'] or 0

        daily_revenue[current_date.strftime('%Y-%m-%d')] = {
            'date': current_date,
            'revenue': day_revenue,
        }

        current_date += timedelta(days=1)

    # Calculate revenue by venue category
    category_revenue = {}
    for booking in bookings:
        category = booking.venue.category.name if booking.venue.category else 'Uncategorized'
        if category not in category_revenue:
            category_revenue[category] = 0
        category_revenue[category] += booking.total_price

    # Sort categories by revenue (descending)
    sorted_categories = sorted(
        category_revenue.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Get top 10 venues by revenue
    top_venues = Venue.objects.filter(
        bookings__in=bookings
    ).annotate(
        revenue=Sum('bookings__total_price')
    ).order_by('-revenue')[:10]

    # Get top 10 services by revenue
    top_services = Service.objects.filter(
        booking_items__booking__in=bookings
    ).annotate(
        revenue=Sum('booking_items__service_price')
    ).order_by('-revenue')[:10]

    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'bookings': bookings,
        'total_revenue': total_revenue,
        'daily_revenue': daily_revenue,
        'category_revenue': category_revenue,
        'sorted_categories': sorted_categories,
        'top_venues': top_venues,
        'top_services': top_services,
    }

    return render(request, 'dashboard_app/admin/revenue_tracking.html', context)


@login_required
def admin_system_health(request):
    """View system health monitoring for admins"""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the admin dashboard.")
        return redirect('venues_app:home')

    # Get database statistics
    db_stats = {
        'users': CustomUser.objects.count(),
        'venues': Venue.objects.count(),
        'services': Service.objects.count(),
        'bookings': Booking.objects.count(),
        'booking_items': BookingItem.objects.count(),
        'reviews': Review.objects.count(),
        'transactions': Transaction.objects.count(),
        'invoices': Invoice.objects.count(),
    }

    # Get recent errors (would typically come from a logging system)
    # For demo purposes, we'll just show some placeholder data
    recent_errors = [
        {
            'timestamp': timezone.now() - timedelta(hours=2),
            'level': 'ERROR',
            'message': 'Example error message',
            'source': 'booking_cart_app.views',
        },
        {
            'timestamp': timezone.now() - timedelta(days=1),
            'level': 'WARNING',
            'message': 'Example warning message',
            'source': 'venues_app.models',
        },
    ]

    # Get system performance metrics (would typically come from monitoring tools)
    # For demo purposes, we'll just show some placeholder data
    performance_metrics = {
        'cpu_usage': 25,  # percentage
        'memory_usage': 40,  # percentage
        'disk_usage': 30,  # percentage
        'average_response_time': 120,  # milliseconds
        'requests_per_minute': 10,
    }

    # Get recent slow queries (would typically come from database monitoring)
    # For demo purposes, we'll just show some placeholder data
    slow_queries = [
        {
            'timestamp': timezone.now() - timedelta(hours=3),
            'duration': 2.5,  # seconds
            'query': 'SELECT * FROM venues_app_venue JOIN venues_app_service ON venue_id=venues_app_venue.id WHERE ...',
        },
        {
            'timestamp': timezone.now() - timedelta(hours=5),
            'duration': 1.8,  # seconds
            'query': 'SELECT * FROM booking_cart_app_booking JOIN booking_cart_app_bookingitem ON booking_id=booking_cart_app_booking.id WHERE ...',
        },
    ]

    context = {
        'db_stats': db_stats,
        'recent_errors': recent_errors,
        'performance_metrics': performance_metrics,
        'slow_queries': slow_queries,
    }

    return render(request, 'dashboard_app/admin/system_health.html', context)


# Dashboard preferences views have been removed as per requirements
