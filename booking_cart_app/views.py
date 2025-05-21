from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum, Count
from django.urls import reverse
from datetime import timedelta

from venues_app.models import Service, Venue
from .models import CartItem, Booking, BookingItem, ServiceAvailability
from payments_app.models import CheckoutSession, CheckoutSessionBooking
from .forms import (
    AddToCartForm, UpdateCartItemForm, CheckoutForm,
    BookingCancellationForm, ServiceAvailabilityForm, DateRangeAvailabilityForm
)
from .utils import (
    clean_expired_cart_items, get_cart_items_for_user, get_cart_total,
    get_bookings_for_customer, get_bookings_for_provider, get_upcoming_bookings_for_provider,
    check_service_availability, get_booking_analytics
)

# Try to import notification utilities if available
try:
    from notifications_app.utils import notify_new_booking, notify_booking_cancelled, notify_booking_status_changed
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False

    # Define dummy notification functions
    def notify_new_booking(booking):
        pass

    def notify_booking_cancelled(booking):
        pass

    def notify_booking_status_changed(booking, old_status):
        pass


# Customer Views
@login_required
def add_to_cart(request, service_id):
    """Add a service to the cart"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can add services to cart.")
        return redirect('venues_app:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id, is_active=True)

    # Check if venue is active and approved
    if not service.venue.is_active or service.venue.approval_status != 'approved':
        messages.error(request, "This service is not currently available.")
        return redirect('venues_app:venue_list')

    if request.method == 'POST':
        form = AddToCartForm(service=service, user=request.user, data=request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']
            quantity = form.cleaned_data['quantity']

            # Check service availability
            is_available, message, availability = check_service_availability(
                service, date, time_slot, quantity
            )

            if not is_available:
                messages.error(request, message)
                return render(request, 'booking_cart_app/add_to_cart.html', {
                    'form': form,
                    'service': service,
                })

            # Check if the service is already in the cart for the same date and time
            existing_item = CartItem.objects.filter(
                user=request.user,
                service=service,
                date=date,
                time_slot=time_slot,
                expires_at__gt=timezone.now()
            ).first()

            if existing_item:
                # Update the quantity
                existing_item.quantity = quantity
                existing_item.expires_at = timezone.now() + timedelta(hours=24)
                existing_item.save()
                messages.success(request, "Cart updated successfully.")
            else:
                # Create a new cart item
                cart_item = form.save(commit=False)
                cart_item.user = request.user
                cart_item.service = service
                cart_item.save()
                messages.success(request, "Service added to cart successfully.")

            # Redirect to cart
            return redirect('booking_cart_app:cart')
    else:
        # Clean expired cart items when viewing the add to cart page
        clean_expired_cart_items()
        form = AddToCartForm(service=service, user=request.user)

    context = {
        'form': form,
        'service': service,
    }

    return render(request, 'booking_cart_app/add_to_cart.html', context)


@login_required
def cart_view(request):
    """View the cart"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view cart.")
        return redirect('venues_app:home')

    # Clean expired cart items
    expired_count = clean_expired_cart_items()
    if expired_count > 0:
        messages.info(request, f"{expired_count} expired item(s) removed from your cart.")

    # Get active cart items
    cart_items = get_cart_items_for_user(request.user)

    # Calculate total price
    total_price = get_cart_total(request.user)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'booking_cart_app/cart.html', context)


@login_required
def update_cart_item(request, item_id):
    """Update a cart item"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can update cart.")
        return redirect('venues_app:home')

    # Get the cart item
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == 'POST':
        form = UpdateCartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            # Get the new quantity
            new_quantity = form.cleaned_data['quantity']

            # Check service availability for the new quantity
            is_available, message, availability = check_service_availability(
                cart_item.service, cart_item.date, cart_item.time_slot, new_quantity
            )

            if not is_available:
                messages.error(request, message)
                context = {
                    'form': form,
                    'cart_item': cart_item,
                }
                return render(request, 'booking_cart_app/update_cart_item.html', context)

            # Update the cart item
            cart_item.quantity = new_quantity
            cart_item.expires_at = timezone.now() + timedelta(hours=24)  # Reset expiration time
            cart_item.save()

            messages.success(request, "Cart updated successfully.")
            return redirect('booking_cart_app:cart')
    else:
        form = UpdateCartItemForm(instance=cart_item)

    context = {
        'form': form,
        'cart_item': cart_item,
    }

    return render(request, 'booking_cart_app/update_cart_item.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Remove a service from the cart"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can update cart.")
        return redirect('venues_app:home')

    # Get the cart item
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    # Delete the cart item
    cart_item.delete()

    messages.success(request, "Item removed from cart successfully.")
    return redirect('booking_cart_app:cart')


@login_required
def checkout(request):
    """Checkout process"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can checkout.")
        return redirect('venues_app:home')

    # Clean expired cart items
    clean_expired_cart_items()

    # Get active cart items
    cart_items = get_cart_items_for_user(request.user)

    # Check if cart is empty
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('booking_cart_app:cart')

    # Group cart items by venue
    venues_dict = {}
    for item in cart_items:
        # Verify service is still available
        is_available, message, _ = check_service_availability(
            item.service, item.date, item.time_slot, item.quantity
        )

        if not is_available:
            messages.error(request, f"Service '{item.service.title}' is no longer available: {message}")
            return redirect('booking_cart_app:cart')

        venue = item.service.venue
        if not venue:
            messages.error(request, f"Service '{item.service.title}' has no associated venue.")
            return redirect('booking_cart_app:cart')

        if venue.id not in venues_dict:
            venues_dict[venue.id] = {
                'venue': venue,
                'items': [],
                'total': 0,
            }

        venues_dict[venue.id]['items'].append(item)
        venues_dict[venue.id]['total'] += item.get_total_price()

    venues = list(venues_dict.values())

    # Calculate total price
    total_price = sum(venue['total'] for venue in venues)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            bookings_created = []

            try:
                with transaction.atomic():
                    # Create a checkout session to track all bookings from this checkout
                    checkout_session = CheckoutSession.objects.create(
                        user=request.user,
                        total_amount=total_price
                    )

                    # Create a booking for each venue
                    for venue_data in venues:
                        venue = venue_data['venue']
                        venue_items = venue_data['items']
                        venue_total = venue_data['total']

                        # Create the booking
                        booking = Booking.objects.create(
                            user=request.user,
                            venue=venue,
                            total_price=venue_total,
                            status='confirmed',  # For MVP, bookings are automatically confirmed
                            notes=form.cleaned_data['notes']
                        )

                        bookings_created.append(booking)

                        # Associate booking with checkout session
                        CheckoutSessionBooking.objects.create(
                            checkout_session=checkout_session,
                            booking=booking
                        )

                        # Create booking items
                        for cart_item in venue_items:
                            # Create booking item
                            # Get the service price (with discount if applicable)
                            service_price = cart_item.service.discounted_price or cart_item.service.price

                            # Create booking item
                            booking_item = BookingItem.objects.create(
                                booking=booking,
                                service=cart_item.service,
                                service_title=cart_item.service.title,
                                service_price=service_price,
                                quantity=cart_item.quantity,
                                date=cart_item.date,
                                time_slot=cart_item.time_slot
                            )

                            # Record discount usage if applicable
                            if cart_item.service.discounted_price and hasattr(cart_item.service, 'discount_info'):
                                from discount_app.utils import record_discount_usage
                                discount_info = cart_item.service.discount_info

                                # Get the discount object
                                if discount_info['type'] == 'percentage':
                                    from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount

                                    # Try to find the discount object based on the name
                                    discount = None
                                    for model in [ServiceDiscount, VenueDiscount, PlatformDiscount]:
                                        try:
                                            discount = model.objects.get(name=discount_info['name'])
                                            break
                                        except model.DoesNotExist:
                                            continue

                                    if discount:
                                        # Record the discount usage
                                        record_discount_usage(
                                            discount=discount,
                                            user=request.user,
                                            booking=booking,
                                            original_price=discount_info['original_price'],
                                            discount_amount=discount_info['amount'],
                                            final_price=discount_info['final_price']
                                        )

                            # Update service availability
                            availability, _ = ServiceAvailability.objects.get_or_create(
                                service=cart_item.service,
                                date=cart_item.date,
                                time_slot=cart_item.time_slot,
                                defaults={
                                    'max_bookings': 10,
                                    'current_bookings': 0,
                                    'is_available': True
                                }
                            )

                            availability.increment_bookings()

                            # Delete cart item
                            cart_item.delete()

                    # Send notifications for all bookings
                    if NOTIFICATIONS_ENABLED:
                        for booking in bookings_created:
                            notify_new_booking(booking)

                # Redirect to payment with the checkout session ID
                if bookings_created:
                    messages.success(request, "Booking created successfully. Please proceed to payment.")
                    # Pass the checkout session ID to the payment process
                    return redirect('payments_app:payment_process_with_session', booking_id=bookings_created[0].booking_id, checkout_session_id=checkout_session.session_id)
                else:
                    messages.error(request, "No bookings were created. Please try again.")
                    return redirect('booking_cart_app:cart')

            except Exception as e:
                messages.error(request, f"Error creating booking: {str(e)}")
                return redirect('booking_cart_app:cart')
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'venues': venues,
        'total_price': total_price,
    }

    return render(request, 'booking_cart_app/checkout.html', context)


@login_required
def booking_confirmation(request, booking_id):
    """Booking confirmation page"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view bookings.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    context = {
        'booking': booking,
        'booking_items': booking.items.all(),
    }

    return render(request, 'booking_cart_app/booking_confirmation.html', context)


def booking_list(request):
    """List all bookings for a customer"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("User is not authenticated, redirecting to login page")
        return redirect('accounts_app:login')

    # Print debug information
    print(f"User: {request.user.email}")
    print(f"is_customer: {getattr(request.user, 'is_customer', False)}")
    print(f"is_authenticated: {request.user.is_authenticated}")

    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view bookings.")
        return redirect('venues_app:home')

    # Get all bookings for the user
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    print(f"Bookings count: {bookings.count()}")

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }

    return render(request, 'booking_cart_app/booking_list.html', context)


def booking_detail(request, booking_id):
    """View booking details"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("User is not authenticated, redirecting to login page")
        return redirect('accounts_app:login')

    # Print debug information
    print(f"User: {request.user.email}")
    print(f"is_customer: {getattr(request.user, 'is_customer', False)}")
    print(f"is_authenticated: {request.user.is_authenticated}")

    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view bookings.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    print(f"Booking: {booking.booking_id}")

    context = {
        'booking': booking,
        'booking_items': booking.items.all(),
        'can_cancel': booking.can_cancel(),
    }

    return render(request, 'booking_cart_app/booking_detail.html', context)


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can cancel bookings.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    # Check if booking can be cancelled
    if not booking.can_cancel():
        messages.error(request, "This booking cannot be cancelled. Bookings must be cancelled at least 6 hours before the scheduled time.")
        return redirect('booking_cart_app:booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        form = BookingCancellationForm(request.POST)
        if form.is_valid():
            try:
                # Store old status for notification
                old_status = booking.status

                # Cancel the booking
                if booking.cancel(reason=form.cleaned_data['reason']):
                    # Send notification
                    if NOTIFICATIONS_ENABLED:
                        notify_booking_cancelled(booking)

                    messages.success(request, "Booking cancelled successfully.")
                else:
                    messages.error(request, "Unable to cancel booking. It may be too close to the scheduled time.")
            except Exception as e:
                messages.error(request, f"Error cancelling booking: {str(e)}")

            return redirect('booking_cart_app:booking_list')
    else:
        form = BookingCancellationForm()

    context = {
        'form': form,
        'booking': booking,
    }

    return render(request, 'booking_cart_app/cancel_booking.html', context)


# Service Provider Views
@login_required
def provider_booking_list(request):
    """List all bookings for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get all venues owned by the service provider
    venues = Venue.objects.filter(owner=request.user)

    # Get all bookings for the venues
    bookings = Booking.objects.filter(venue__in=venues).order_by('-booking_date')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }

    return render(request, 'booking_cart_app/provider/booking_list.html', context)


@login_required
def provider_booking_detail(request, booking_id):
    """View booking details for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get all venues owned by the service provider
    venues = Venue.objects.filter(owner=request.user)

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, venue__in=venues)

    context = {
        'booking': booking,
        'booking_items': booking.items.all(),
    }

    return render(request, 'booking_cart_app/provider/booking_detail.html', context)


@login_required
def provider_update_booking_status(request, booking_id):
    """Update booking status for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get all venues owned by the service provider
    venues = Venue.objects.filter(owner=request.user)

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, venue__in=venues)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [choice[0] for choice in Booking.STATUS_CHOICES]:
            # Store old status for notification
            old_status = booking.status

            # Update status
            booking.status = status
            booking.save()

            # Send notification if status changed
            if NOTIFICATIONS_ENABLED and old_status != status:
                notify_booking_status_changed(booking, old_status)

            messages.success(request, "Booking status updated successfully.")
        else:
            messages.error(request, "Invalid status.")

        return redirect('booking_cart_app:provider_booking_detail', booking_id=booking_id)

    context = {
        'booking': booking,
    }

    return render(request, 'booking_cart_app/provider/update_booking_status.html', context)


@login_required
def provider_service_availability(request, service_id):
    """Manage service availability for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id, venue__owner=request.user)

    # Get all availability records for the service
    availability_records = ServiceAvailability.objects.filter(
        service=service,
        date__gte=timezone.now().date()
    ).order_by('date', 'time_slot')

    if request.method == 'POST':
        form = ServiceAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.service = service

            # Check if a record already exists for this date and time
            existing = ServiceAvailability.objects.filter(
                service=service,
                date=availability.date,
                time_slot=availability.time_slot
            ).first()

            if existing:
                # Update existing record
                existing.max_bookings = availability.max_bookings
                existing.is_available = availability.is_available
                existing.save()
                messages.success(request, "Availability updated successfully.")
            else:
                # Create new record
                availability.save()
                messages.success(request, "Availability added successfully.")

            return redirect('booking_cart_app:provider_service_availability', service_id=service_id)
    else:
        form = ServiceAvailabilityForm()

    context = {
        'form': form,
        'service': service,
        'availability_records': availability_records,
    }

    return render(request, 'booking_cart_app/provider/service_availability.html', context)


@login_required
def provider_bulk_availability(request, service_id):
    """Set availability for a date range"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id, venue__owner=request.user)

    if request.method == 'POST':
        form = DateRangeAvailabilityForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            interval = form.cleaned_data['interval']
            max_bookings = form.cleaned_data['max_bookings']
            is_available = form.cleaned_data['is_available']

            # Generate time slots
            time_slots = []
            current_time = start_time
            while current_time < end_time:
                time_slots.append(current_time)
                # Add interval minutes to current time
                hours, minutes = divmod(current_time.hour * 60 + current_time.minute + interval, 60)
                current_time = timezone.datetime.time(hour=hours, minute=minutes)

            # Generate dates
            dates = []
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date)
                current_date += timedelta(days=1)

            # Create availability records
            created_count = 0
            updated_count = 0
            for date in dates:
                for time_slot in time_slots:
                    # Check if a record already exists
                    existing = ServiceAvailability.objects.filter(
                        service=service,
                        date=date,
                        time_slot=time_slot
                    ).first()

                    if existing:
                        # Update existing record
                        existing.max_bookings = max_bookings
                        existing.is_available = is_available
                        existing.save()
                        updated_count += 1
                    else:
                        # Create new record
                        ServiceAvailability.objects.create(
                            service=service,
                            date=date,
                            time_slot=time_slot,
                            max_bookings=max_bookings,
                            current_bookings=0,
                            is_available=is_available
                        )
                        created_count += 1

            messages.success(
                request,
                f"Availability set successfully. Created {created_count} new records and updated {updated_count} existing records."
            )
            return redirect('booking_cart_app:provider_service_availability', service_id=service_id)
    else:
        form = DateRangeAvailabilityForm()

    context = {
        'form': form,
        'service': service,
    }

    return render(request, 'booking_cart_app/provider/bulk_availability.html', context)


@login_required
def provider_delete_availability(request, availability_id):
    """Delete an availability record"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get the availability record
    availability = get_object_or_404(
        ServiceAvailability,
        id=availability_id,
        service__venue__owner=request.user
    )

    # Check if there are any bookings for this time slot
    if availability.current_bookings > 0:
        messages.error(request, "Cannot delete availability with existing bookings.")
        return redirect('booking_cart_app:provider_service_availability', service_id=availability.service.id)

    # Delete the availability record
    service_id = availability.service.id
    availability.delete()

    messages.success(request, "Availability deleted successfully.")
    return redirect('booking_cart_app:provider_service_availability', service_id=service_id)


# Simple test view to check authentication
def admin_booking_list(request):
    """List all bookings for admin"""
    # Create a simple response for testing
    if request.GET.get('test') == 'true':
        response_text = f"""
        <html>
        <head><title>Authentication Test</title></head>
        <body>
            <h1>Authentication Test</h1>
            <p>User: {request.user}</p>
            <p>Is Staff: {getattr(request.user, 'is_staff', False)}</p>
            <p>Is Authenticated: {request.user.is_authenticated}</p>
        </body>
        </html>
        """
        return HttpResponse(response_text)

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to access this page.")
        return redirect('accounts_app:login')

    # Print debug information
    print(f"User: {request.user.email}")
    print(f"is_staff: {request.user.is_staff}")
    print(f"is_authenticated: {request.user.is_authenticated}")

    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get all bookings
    bookings = Booking.objects.all().order_by('-booking_date')
    print(f"Bookings count: {bookings.count()}")

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Filter by venue if provided
    venue_filter = request.GET.get('venue')
    if venue_filter:
        bookings = bookings.filter(venue_id=venue_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'venue_filter': venue_filter,
        'venues': Venue.objects.all(),
    }

    return render(request, 'booking_cart_app/admin/booking_list.html', context)


@login_required
def admin_booking_detail(request, booking_id):
    """View booking details for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id)

    context = {
        'booking': booking,
        'booking_items': booking.items.all(),
    }

    return render(request, 'booking_cart_app/admin/booking_detail.html', context)


@login_required
def admin_update_booking_status(request, booking_id):
    """Update booking status for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [choice[0] for choice in Booking.STATUS_CHOICES]:
            # Store old status for notification
            old_status = booking.status

            # Update status
            booking.status = status
            booking.save()

            # Send notification if status changed
            if NOTIFICATIONS_ENABLED and old_status != status:
                notify_booking_status_changed(booking, old_status)

            messages.success(request, "Booking status updated successfully.")

            # Log admin activity
            try:
                from admin_app.utils import log_admin_activity
                log_admin_activity(
                    request,
                    action_type="update",
                    target_model="Booking",
                    target_id=str(booking.booking_id),
                    description=f"Updated booking status from {old_status} to {status}"
                )
            except ImportError:
                pass
        else:
            messages.error(request, "Invalid status.")

        return redirect('booking_cart_app:admin_booking_detail', booking_id=booking_id)

    context = {
        'booking': booking,
    }

    return render(request, 'booking_cart_app/admin/update_booking_status.html', context)


@login_required
def admin_booking_analytics(request):
    """View booking analytics for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get analytics data
    analytics = get_booking_analytics()

    # Get date range for filtering if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter by date range if provided
    if start_date and end_date:
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

            # Get bookings in date range
            bookings = Booking.objects.filter(
                items__date__gte=start_date,
                items__date__lte=end_date
            ).distinct()

            # Calculate total revenue in date range
            total_revenue = bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0

            # Calculate revenue by status in date range
            revenue_by_status = {}
            for status, _ in Booking.STATUS_CHOICES:
                revenue = bookings.filter(status=status).aggregate(Sum('total_price'))['total_price__sum'] or 0
                revenue_by_status[status] = revenue

            # Calculate booking counts by status in date range
            booking_counts = {}
            for status, _ in Booking.STATUS_CHOICES:
                count = bookings.filter(status=status).count()
                booking_counts[status] = count

            # Update analytics with filtered data
            analytics['revenue']['total_filtered'] = total_revenue
            analytics['revenue_by_status_filtered'] = revenue_by_status
            analytics['status_counts_filtered'] = booking_counts
            analytics['date_filter'] = {'start_date': start_date, 'end_date': end_date}
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

    context = analytics
    return render(request, 'booking_cart_app/admin/booking_analytics.html', context)
