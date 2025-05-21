from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)

@register.filter
def filter_by_rating(reviews, rating):
    """Filter reviews by rating"""
    return [review for review in reviews if review.rating == rating]

@register.filter
def filter_by_status(reviews, status):
    """Filter reviews by status"""
    if status == 'approved':
        return [review for review in reviews if review.is_approved]
    elif status == 'flagged':
        return [review for review in reviews if review.is_flagged]
    elif status == 'pending':
        return [review for review in reviews if not review.is_approved and not review.is_flagged]
    return []

@register.filter
def filter_with_response(reviews):
    """Filter reviews that have responses"""
    return [review for review in reviews if hasattr(review, 'response') and review.response is not None]

@register.filter
def percentage(count, total):
    """Calculate percentage"""
    return (count / total * 100) if total > 0 else 0

@register.filter
def format_currency(value):
    """Format a value as currency"""
    if value is None:
        return "$0.00"
    return f"${value:.2f}"

@register.filter
def get_status_badge_class(status):
    """Get the appropriate Bootstrap badge class for a status"""
    if status == 'pending':
        return 'bg-warning'
    elif status == 'confirmed':
        return 'bg-success'
    elif status == 'cancelled':
        return 'bg-danger'
    elif status == 'completed':
        return 'bg-info'
    else:
        return 'bg-secondary'
