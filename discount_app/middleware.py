from django.utils import timezone
from .utils import get_best_discount


class DiscountMiddleware:
    """
    Middleware to apply discounts to services
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        """
        Process template response to apply discounts to services
        """
        # Check if the response has a context
        if hasattr(response, 'context_data'):
            context = response.context_data

            # Apply discounts to single service
            if 'service' in context and hasattr(context['service'], 'price'):
                service = context['service']
                self._apply_discount_to_service(service, request.user)

            # Apply discounts to service list
            if 'services' in context and hasattr(context['services'], '__iter__'):
                for service in context['services']:
                    if hasattr(service, 'price'):
                        self._apply_discount_to_service(service, request.user)

            # Apply discounts to cart items
            if 'cart_items' in context and hasattr(context['cart_items'], '__iter__'):
                for item in context['cart_items']:
                    if hasattr(item, 'service') and hasattr(item.service, 'price'):
                        self._apply_discount_to_service(item.service, request.user)

            # Apply discounts to booking items
            if 'booking_items' in context and hasattr(context['booking_items'], '__iter__'):
                for item in context['booking_items']:
                    if hasattr(item, 'service') and hasattr(item.service, 'price'):
                        self._apply_discount_to_service(item.service, request.user)

        return response

    def _apply_discount_to_service(self, service, user=None):
        """
        Apply the best discount to a service
        """
        # Get the best discount for the service
        best_discount = get_best_discount(service, user)

        # Apply the discount if found
        if best_discount:
            discount, discount_amount, final_price = best_discount
            service.discounted_price = final_price
            service.discount_info = {
                'name': discount.name,
                'type': discount.discount_type,
                'value': discount.discount_value,
                'amount': discount_amount,
                'original_price': service.price,
                'final_price': final_price,
            }
        else:
            service.discounted_price = None
            service.discount_info = None
