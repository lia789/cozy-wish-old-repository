from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import CartItem, Booking, ServiceAvailability

def clean_expired_cart_items():
    """
    Remove expired cart items
    Returns the number of items removed
    """
    expired_items = CartItem.objects.filter(expires_at__lt=timezone.now())
    count = expired_items.count()
    expired_items.delete()
    return count

def get_cart_items_for_user(user):
    """
    Get active cart items for a user
    """
    if not user.is_authenticated or not hasattr(user, 'is_customer') or not user.is_customer:
        return CartItem.objects.none()
    
    return CartItem.objects.filter(
        user=user,
        expires_at__gt=timezone.now()
    ).order_by('date', 'time_slot')

def get_cart_total(user):
    """
    Calculate the total price of items in a user's cart
    """
    cart_items = get_cart_items_for_user(user)
    return sum(item.get_total_price() for item in cart_items)

def get_bookings_for_customer(user, status=None):
    """
    Get bookings for a customer, optionally filtered by status
    """
    if not user.is_authenticated or not hasattr(user, 'is_customer') or not user.is_customer:
        return Booking.objects.none()
    
    bookings = Booking.objects.filter(user=user)
    
    if status:
        bookings = bookings.filter(status=status)
    
    return bookings.order_by('-booking_date')

def get_bookings_for_provider(user, status=None):
    """
    Get bookings for a service provider, optionally filtered by status
    """
    if not user.is_authenticated or not hasattr(user, 'is_service_provider') or not user.is_service_provider:
        return Booking.objects.none()
    
    # Get all venues owned by the service provider
    from venues_app.models import Venue
    venues = Venue.objects.filter(owner=user)
    
    bookings = Booking.objects.filter(venue__in=venues)
    
    if status:
        bookings = bookings.filter(status=status)
    
    return bookings.order_by('-booking_date')

def get_upcoming_bookings_for_provider(user, days=7):
    """
    Get upcoming bookings for a service provider within the specified number of days
    """
    bookings = get_bookings_for_provider(user, status='confirmed')
    
    # Filter for bookings with items in the next X days
    today = timezone.now().date()
    end_date = today + timedelta(days=days)
    
    return bookings.filter(
        items__date__gte=today,
        items__date__lte=end_date
    ).distinct()

def check_service_availability(service, date, time_slot, quantity=1):
    """
    Check if a service is available for the specified date, time, and quantity
    Returns (is_available, message, availability_object)
    """
    try:
        # Check if date is in the past
        if date < timezone.now().date():
            return False, "Cannot book services for past dates", None
        
        # Check if service is active
        if not service.is_active:
            return False, "This service is not currently available", None
        
        # Check if venue is active and approved
        if not service.venue.is_active or service.venue.approval_status != 'approved':
            return False, "This venue is not currently available", None
        
        # Get or create availability
        availability, created = ServiceAvailability.objects.get_or_create(
            service=service,
            date=date,
            time_slot=time_slot,
            defaults={
                'max_bookings': 10,
                'current_bookings': 0,
                'is_available': True
            }
        )
        
        # Check if available
        if not availability.is_available:
            return False, "This service is not available at the selected time", availability
        
        # Check if fully booked
        if availability.is_fully_booked():
            return False, "This service is fully booked for the selected time", availability
        
        # Check if enough slots available
        if availability.current_bookings + quantity > availability.max_bookings:
            return False, f"Only {availability.max_bookings - availability.current_bookings} slots available", availability
        
        return True, "Service is available", availability
    
    except Exception as e:
        return False, f"Error checking availability: {str(e)}", None

def get_booking_analytics():
    """
    Get booking analytics data
    Returns a dictionary with analytics data
    """
    today = timezone.now().date()
    
    # Get counts by status
    pending_count = Booking.objects.filter(status='pending').count()
    confirmed_count = Booking.objects.filter(status='confirmed').count()
    completed_count = Booking.objects.filter(status='completed').count()
    cancelled_count = Booking.objects.filter(status='cancelled').count()
    
    # Get counts by date range
    today_count = Booking.objects.filter(
        items__date=today
    ).distinct().count()
    
    this_week_count = Booking.objects.filter(
        items__date__gte=today,
        items__date__lte=today + timedelta(days=7)
    ).distinct().count()
    
    this_month_count = Booking.objects.filter(
        items__date__gte=today,
        items__date__lte=today + timedelta(days=30)
    ).distinct().count()
    
    # Get revenue data
    from django.db.models import Sum
    total_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Get top venues by booking count
    from venues_app.models import Venue
    from django.db.models import Count
    top_venues_by_count = Venue.objects.annotate(
        booking_count=Count('bookings', filter=Q(bookings__status__in=['confirmed', 'completed']))
    ).order_by('-booking_count')[:5]
    
    # Get top venues by revenue
    top_venues_by_revenue = Venue.objects.annotate(
        revenue=Sum('bookings__total_price', filter=Q(bookings__status__in=['confirmed', 'completed']))
    ).order_by('-revenue')[:5]
    
    return {
        'status_counts': {
            'pending': pending_count,
            'confirmed': confirmed_count,
            'completed': completed_count,
            'cancelled': cancelled_count,
            'total': pending_count + confirmed_count + completed_count + cancelled_count
        },
        'date_counts': {
            'today': today_count,
            'this_week': this_week_count,
            'this_month': this_month_count
        },
        'revenue': {
            'total': total_revenue
        },
        'top_venues_by_count': top_venues_by_count,
        'top_venues_by_revenue': top_venues_by_revenue
    }
