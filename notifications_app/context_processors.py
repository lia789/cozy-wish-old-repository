from .utils import get_unread_count, get_user_notifications


def notifications_context(request):
    """
    Context processor to add notification data to all templates
    """
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }
    
    if request.user.is_authenticated:
        context['unread_notifications_count'] = get_unread_count(request.user)
        context['recent_notifications'] = get_user_notifications(request.user)[:5]
    
    return context
