from django.utils import timezone
from .models import AdminActivity, SecurityEvent, AdminPreference

def log_admin_activity(request, action_type, target_model=None, target_id=None, description=None):
    """
    Log admin activity
    
    Args:
        request: The HTTP request
        action_type: Type of action (create, update, delete, etc.)
        target_model: Model affected by the action
        target_id: ID of the object affected
        description: Description of the action
    """
    if not request.user.is_authenticated:
        return None
    
    return AdminActivity.objects.create(
        user=request.user,
        action_type=action_type,
        target_model=target_model,
        target_id=target_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

def log_security_event(request, event_type, severity='info', description=None, user=None):
    """
    Log security event
    
    Args:
        request: The HTTP request
        event_type: Type of security event
        severity: Severity level (info, warning, critical)
        description: Description of the event
        user: User associated with the event (defaults to request.user)
    """
    if user is None and request.user.is_authenticated:
        user = request.user
    
    return SecurityEvent.objects.create(
        user=user,
        event_type=event_type,
        severity=severity,
        description=description or f"{event_type} event",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

def get_client_ip(request):
    """
    Get client IP address from request
    
    Args:
        request: The HTTP request
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_admin_preference(user):
    """
    Get admin preferences for a user, creating default preferences if they don't exist
    
    Args:
        user: User object
    
    Returns:
        AdminPreference: User's admin preferences
    """
    if not user.is_authenticated:
        # Return default preferences for unauthenticated users
        return type('DefaultPreference', (), {
            'theme': 'light',
            'sidebar_collapsed': False,
            'show_quick_actions': True,
            'items_per_page': 10
        })
    
    preference, created = AdminPreference.objects.get_or_create(
        user=user,
        defaults={
            'theme': 'light',
            'sidebar_collapsed': False,
            'show_quick_actions': True,
            'items_per_page': 10
        }
    )
    return preference

def get_unresolved_security_events(limit=5):
    """
    Get unresolved security events
    
    Args:
        limit: Maximum number of events to return
    
    Returns:
        QuerySet: Unresolved security events
    """
    return SecurityEvent.objects.filter(is_resolved=False).order_by('-severity', '-timestamp')[:limit]

def get_unresolved_security_events_count():
    """
    Get count of unresolved security events
    
    Returns:
        int: Count of unresolved security events
    """
    return SecurityEvent.objects.filter(is_resolved=False).count()

def format_date_range(start_date, end_date):
    """
    Format date range for display
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        str: Formatted date range
    """
    if start_date == end_date:
        return start_date.strftime('%B %d, %Y')
    
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}"
    
    if start_date.year == end_date.year:
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    
    return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
