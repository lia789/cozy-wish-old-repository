from .utils import get_admin_preference, get_unresolved_security_events, get_unresolved_security_events_count

def admin_context(request):
    """
    Context processor for admin app
    
    Adds admin-related context variables to all templates
    """
    context = {}
    
    # Only add admin context if user is authenticated and is staff/superuser
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Add admin preferences
        context['preference'] = get_admin_preference(request.user)
        
        # Add unresolved security events
        context['unresolved_security_events'] = get_unresolved_security_events()
        context['unresolved_security_events_count'] = get_unresolved_security_events_count()
    
    return context
