from .utils import get_cart_items_for_user, get_cart_total, clean_expired_cart_items

def cart_context(request):
    """
    Context processor to add cart information to all templates
    """
    cart_count = 0
    cart_total = 0

    if request.user.is_authenticated and hasattr(request.user, 'is_customer') and request.user.is_customer:
        # Clean expired cart items (only do this occasionally to avoid performance issues)
        if request.path.startswith('/booking/cart') or request.path.startswith('/booking/checkout'):
            clean_expired_cart_items()

        # Get active cart items
        cart_items = get_cart_items_for_user(request.user)

        # Count items and calculate total
        cart_count = cart_items.count()
        cart_total = get_cart_total(request.user)

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
