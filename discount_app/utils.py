from django.utils import timezone
from .models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage


def get_applicable_discounts(service, user=None):
    """
    Get all applicable discounts for a service
    Returns a list of tuples (discount_object, discount_amount, final_price)
    """
    now = timezone.now()
    applicable_discounts = []
    original_price = service.price
    
    # Check for service-specific discounts
    service_discounts = ServiceDiscount.objects.filter(
        service=service,
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now
    )
    
    for discount in service_discounts:
        discount_amount = discount.calculate_discount(original_price)
        final_price = discount.calculate_discounted_price(original_price)
        applicable_discounts.append((discount, discount_amount, final_price))
    
    # Check for venue-wide discounts
    venue_discounts = VenueDiscount.objects.filter(
        venue=service.venue,
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now,
        min_booking_value__lte=original_price
    )
    
    for discount in venue_discounts:
        discount_amount = discount.calculate_discount(original_price)
        
        # Apply max discount amount if set
        if discount.max_discount_amount and discount_amount > discount.max_discount_amount:
            discount_amount = discount.max_discount_amount
            
        final_price = original_price - discount_amount
        applicable_discounts.append((discount, discount_amount, final_price))
    
    # Check for platform-wide discounts
    platform_discounts = PlatformDiscount.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        min_booking_value__lte=original_price
    )
    
    # Filter by category if applicable
    if service.venue.category:
        platform_discounts = platform_discounts.filter(
            category__isnull=True
        ) | platform_discounts.filter(
            category=service.venue.category
        )
    
    for discount in platform_discounts:
        discount_amount = discount.calculate_discount(original_price)
        
        # Apply max discount amount if set
        if discount.max_discount_amount and discount_amount > discount.max_discount_amount:
            discount_amount = discount.max_discount_amount
            
        final_price = original_price - discount_amount
        applicable_discounts.append((discount, discount_amount, final_price))
    
    # Sort by final price (lowest first)
    applicable_discounts.sort(key=lambda x: x[2])
    
    return applicable_discounts


def get_best_discount(service, user=None):
    """
    Get the best discount for a service
    Returns a tuple (discount_object, discount_amount, final_price) or None if no discount applies
    """
    applicable_discounts = get_applicable_discounts(service, user)
    
    if applicable_discounts:
        return applicable_discounts[0]  # Return the discount with the lowest final price
    
    return None


def record_discount_usage(discount, user, booking, original_price, discount_amount, final_price):
    """
    Record the usage of a discount
    """
    if isinstance(discount, VenueDiscount):
        discount_type = 'VenueDiscount'
    elif isinstance(discount, ServiceDiscount):
        discount_type = 'ServiceDiscount'
    elif isinstance(discount, PlatformDiscount):
        discount_type = 'PlatformDiscount'
    else:
        raise ValueError("Invalid discount type")
    
    usage = DiscountUsage.objects.create(
        user=user,
        discount_type=discount_type,
        discount_id=discount.id,
        booking=booking,
        original_price=original_price,
        discount_amount=discount_amount,
        final_price=final_price
    )
    
    return usage
