import random
from django.utils import timezone
from .utils import clean_expired_cart_items

class CartCleanupMiddleware:
    """
    Middleware to clean expired cart items

    This middleware runs on each request to check and remove expired cart items.
    To avoid performance issues, it only runs the cleanup occasionally based on
    certain conditions:
    1. Always runs for cart and checkout pages
    2. Runs with a 5% probability for authenticated customers on other pages
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only run cleanup for authenticated users who are customers
        if request.user.is_authenticated and hasattr(request.user, 'is_customer') and request.user.is_customer:
            # Always clean expired items on cart and checkout pages
            if request.path.startswith('/booking/cart') or request.path.startswith('/booking/checkout'):
                clean_expired_cart_items()
            # Occasionally clean expired items on other pages (5% chance)
            elif random.random() < 0.05:
                clean_expired_cart_items()

        response = self.get_response(request)
        return response
