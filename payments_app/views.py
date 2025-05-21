from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from django.http import Http404

from booking_cart_app.models import Booking
from .models import PaymentMethod, Transaction, Invoice, CheckoutSession, CheckoutSessionBooking
from .forms import PaymentMethodForm, PaymentForm, RefundForm


# Customer Views
@login_required
def payment_process(request, booking_id, checkout_session_id=None):
    """Process payment for a booking or a checkout session with multiple bookings"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can process payments.")
        return redirect('venues_app:home')

    # Get the booking
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    # Get checkout session if provided
    checkout_session = None
    related_bookings = []
    total_amount = booking.total_price

    if checkout_session_id:
        try:
            checkout_session = CheckoutSession.objects.get(session_id=checkout_session_id, user=request.user)

            # Check if checkout session is already paid
            if checkout_session.is_paid:
                messages.info(request, "This checkout session has already been paid.")
                return redirect('booking_cart_app:booking_detail', booking_id=booking.booking_id)

            # Get all bookings associated with this checkout session
            session_bookings = CheckoutSessionBooking.objects.filter(checkout_session=checkout_session)
            related_bookings = [sb.booking for sb in session_bookings]

            # Use the total amount from the checkout session
            total_amount = checkout_session.total_amount
        except CheckoutSession.DoesNotExist:
            # If checkout session doesn't exist, just process the single booking
            pass

    # Check if booking is already paid
    if hasattr(booking, 'invoice') and booking.invoice.status == 'paid':
        messages.info(request, "This booking has already been paid.")
        return redirect('booking_cart_app:booking_detail', booking_id=booking.booking_id)

    # Get or create invoice for the main booking
    invoice, created = Invoice.objects.get_or_create(
        booking=booking,
        defaults={
            'user': request.user,
            'amount': booking.total_price,
            'due_date': timezone.now() + timezone.timedelta(hours=24),
        }
    )

    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            # For MVP, we'll just simulate payment processing
            # In a real app, you would integrate with a payment processor like Stripe

            payment_method_choice = form.cleaned_data['payment_method_choice']
            transactions_created = []

            with transaction.atomic():
                # Process payment method
                if payment_method_choice == 'new':
                    # Process payment with new payment method
                    payment_type = form.cleaned_data['payment_type']
                    name = form.cleaned_data['name']
                    card_number = form.cleaned_data['card_number']

                    # Save payment method if requested
                    if form.cleaned_data['save_payment_method']:
                        payment_method = PaymentMethod.objects.create(
                            user=request.user,
                            payment_type=payment_type,
                            name=name,
                            last_four=card_number[-4:],
                            expiry_date=form.cleaned_data['expiry_date'],
                            is_default=not PaymentMethod.objects.filter(user=request.user).exists()
                        )

                    # Payment details for transactions
                    payment_method_type = payment_type
                    payment_method_details = f"{payment_type.title()} ending in {card_number[-4:]}"

                elif payment_method_choice == 'saved':
                    # Process payment with saved payment method
                    payment_method = form.cleaned_data['saved_payment_method']

                    # Payment details for transactions
                    payment_method_type = payment_method.payment_type
                    payment_method_details = f"{payment_method.get_payment_type_display()} ending in {payment_method.last_four}"

                # Process the main booking first
                main_transaction = Transaction.objects.create(
                    user=request.user,
                    booking=booking,
                    amount=booking.total_price,
                    status='completed',  # For MVP, all payments are successful
                    payment_method=payment_method_type,
                    payment_method_details=payment_method_details
                )
                transactions_created.append(main_transaction)

                # Update invoice for main booking
                invoice.mark_as_paid(transaction=main_transaction)

                # Update main booking status
                booking.status = 'confirmed'
                booking.save()

                # Process related bookings if this is a multi-venue checkout
                if checkout_session and related_bookings:
                    for related_booking in related_bookings:
                        # Skip the main booking as it's already processed
                        if related_booking.booking_id == booking.booking_id:
                            continue

                        # Create transaction for related booking
                        related_transaction = Transaction.objects.create(
                            user=request.user,
                            booking=related_booking,
                            amount=related_booking.total_price,
                            status='completed',  # For MVP, all payments are successful
                            payment_method=payment_method_type,
                            payment_method_details=payment_method_details
                        )
                        transactions_created.append(related_transaction)

                        # Create and mark invoice as paid
                        related_invoice, _ = Invoice.objects.get_or_create(
                            booking=related_booking,
                            defaults={
                                'user': request.user,
                                'amount': related_booking.total_price,
                                'due_date': timezone.now() + timezone.timedelta(hours=24),
                            }
                        )
                        related_invoice.mark_as_paid(transaction=related_transaction)

                        # Update related booking status
                        related_booking.status = 'confirmed'
                        related_booking.save()

                    # Mark checkout session as paid
                    if checkout_session:
                        checkout_session.mark_as_paid()

            # Success message based on number of bookings processed
            if len(transactions_created) > 1:
                messages.success(request, f"Payment processed successfully for {len(transactions_created)} bookings.")
            else:
                messages.success(request, "Payment processed successfully.")

            # Redirect to payment confirmation for the main transaction
            return redirect('payments_app:payment_confirmation', transaction_id=main_transaction.transaction_id)
    else:
        form = PaymentForm(user=request.user)

    context = {
        'form': form,
        'booking': booking,
        'invoice': invoice,
        'checkout_session': checkout_session,
        'related_bookings': related_bookings,
        'total_amount': total_amount,
        'is_multi_booking': len(related_bookings) > 1,
    }

    return render(request, 'payments_app/payment_process.html', context)


@login_required
def payment_confirmation(request, transaction_id):
    """Payment confirmation page"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view payment confirmations.")
        return redirect('venues_app:home')

    # Get the transaction
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    # Check if this transaction is part of a multi-booking checkout
    related_bookings = []
    checkout_session = None

    # Try to find if the booking is associated with a checkout session
    try:
        checkout_session_booking = CheckoutSessionBooking.objects.get(booking=transaction_obj.booking)
        checkout_session = checkout_session_booking.checkout_session

        # If checkout session exists and is paid, get all related bookings
        if checkout_session and checkout_session.is_paid:
            session_bookings = CheckoutSessionBooking.objects.filter(checkout_session=checkout_session)
            related_bookings = [sb.booking for sb in session_bookings]
    except CheckoutSessionBooking.DoesNotExist:
        # Not part of a checkout session, just show the single booking
        pass

    context = {
        'transaction': transaction_obj,
        'booking': transaction_obj.booking,
        'checkout_session': checkout_session,
        'related_bookings': related_bookings,
        'is_multi_booking': len(related_bookings) > 1,
    }

    return render(request, 'payments_app/payment_confirmation.html', context)


@login_required
def payment_history(request):
    """View payment history"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view payment history.")
        return redirect('venues_app:home')

    # Get all transactions for the user
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'transactions': transactions,
    }

    return render(request, 'payments_app/payment_history.html', context)


@login_required
def payment_detail(request, transaction_id):
    """View payment details"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can view payment details.")
        return redirect('venues_app:home')

    # Get the transaction
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    context = {
        'transaction': transaction_obj,
        'booking': transaction_obj.booking,
        'invoice': transaction_obj.invoices.first() if transaction_obj.invoices.exists() else None,
    }

    return render(request, 'payments_app/payment_detail.html', context)


@login_required
def payment_methods(request):
    """View and manage payment methods"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can manage payment methods.")
        return redirect('venues_app:home')

    # Get all payment methods for the user
    payment_methods = PaymentMethod.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    context = {
        'payment_methods': payment_methods,
    }

    return render(request, 'payments_app/payment_methods.html', context)


@login_required
def add_payment_method(request):
    """Add a new payment method"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can manage payment methods.")
        return redirect('venues_app:home')

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            payment_method.save()

            messages.success(request, "Payment method added successfully.")
            return redirect('payments_app:payment_methods')
    else:
        form = PaymentMethodForm()

    context = {
        'form': form,
    }

    return render(request, 'payments_app/add_payment_method.html', context)


@login_required
def edit_payment_method(request, payment_method_id):
    """Edit a payment method"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can manage payment methods.")
        return redirect('venues_app:home')

    # Get the payment method
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()

            messages.success(request, "Payment method updated successfully.")
            return redirect('payments_app:payment_methods')
    else:
        form = PaymentMethodForm(instance=payment_method)

    context = {
        'form': form,
        'payment_method': payment_method,
    }

    return render(request, 'payments_app/edit_payment_method.html', context)


@login_required
def delete_payment_method(request, payment_method_id):
    """Delete a payment method"""
    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can manage payment methods.")
        return redirect('venues_app:home')

    # Get the payment method
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)

    if request.method == 'POST':
        # Check if this is the only payment method
        if PaymentMethod.objects.filter(user=request.user).count() == 1 and payment_method.is_default:
            messages.error(request, "You cannot delete your only payment method.")
            return redirect('payments_app:payment_methods')

        # If this is the default payment method, set another one as default
        if payment_method.is_default:
            next_payment_method = PaymentMethod.objects.filter(user=request.user).exclude(id=payment_method.id).first()
            if next_payment_method:
                next_payment_method.is_default = True
                next_payment_method.save()

        # Delete the payment method
        payment_method.delete()

        messages.success(request, "Payment method deleted successfully.")
        return redirect('payments_app:payment_methods')

    context = {
        'payment_method': payment_method,
    }

    return render(request, 'payments_app/delete_payment_method.html', context)


# Service Provider Views
@login_required
def provider_payment_history(request):
    """View payment history for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get all bookings for venues owned by the service provider
    from venues_app.models import Venue
    venues = Venue.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(venue__in=venues)

    # Get all transactions for these bookings
    transactions = Transaction.objects.filter(booking__in=bookings).order_by('-created_at')

    context = {
        'transactions': transactions,
    }

    return render(request, 'payments_app/provider/payment_history.html', context)


@login_required
def provider_payment_detail(request, transaction_id):
    """View payment details for a service provider"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('venues_app:home')

    # Get all venues owned by the service provider
    from venues_app.models import Venue
    venues = Venue.objects.filter(owner=request.user)

    # Get the transaction
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id, booking__venue__in=venues)

    context = {
        'transaction': transaction_obj,
        'booking': transaction_obj.booking,
        'invoice': transaction_obj.invoices.first() if transaction_obj.invoices.exists() else None,
    }

    return render(request, 'payments_app/provider/payment_detail.html', context)


# Admin Views
@login_required
def admin_payment_list(request):
    """List all payments for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get all transactions
    transactions = Transaction.objects.all().order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)

    # Filter by payment method if provided
    payment_method_filter = request.GET.get('payment_method')
    if payment_method_filter:
        transactions = transactions.filter(payment_method=payment_method_filter)

    context = {
        'transactions': transactions,
        'status_filter': status_filter,
        'payment_method_filter': payment_method_filter,
        'status_choices': Transaction.STATUS_CHOICES,
        'payment_method_choices': Transaction.PAYMENT_METHOD_CHOICES,
    }

    return render(request, 'payments_app/admin/payment_list.html', context)


@login_required
def admin_payment_detail(request, transaction_id):
    """View payment details for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get the transaction
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id)

    context = {
        'transaction': transaction_obj,
        'booking': transaction_obj.booking,
        'invoice': transaction_obj.invoices.first() if transaction_obj.invoices.exists() else None,
    }

    return render(request, 'payments_app/admin/payment_detail.html', context)


@login_required
def admin_refund_payment(request, transaction_id):
    """Refund a payment for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get the transaction
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id)

    # Check if transaction can be refunded
    if transaction_obj.status != 'completed':
        messages.error(request, "Only completed transactions can be refunded.")
        return redirect('payments_app:admin_payment_detail', transaction_id=transaction_obj.transaction_id)

    if request.method == 'POST':
        form = RefundForm(request.POST, instance=transaction_obj)
        if form.is_valid():
            with transaction.atomic():
                # Update transaction status
                transaction_obj.status = 'refunded'
                transaction_obj.save()

                # Update invoice status
                invoice = transaction_obj.invoices.first()
                if invoice:
                    invoice.status = 'cancelled'
                    invoice.save()

                # Update booking status
                booking = transaction_obj.booking
                booking.status = 'cancelled'
                booking.cancellation_reason = form.cleaned_data['notes']
                booking.save()

            messages.success(request, "Payment refunded successfully.")
            return redirect('payments_app:admin_payment_detail', transaction_id=transaction_obj.transaction_id)
    else:
        form = RefundForm(instance=transaction_obj)

    context = {
        'form': form,
        'transaction': transaction_obj,
    }

    return render(request, 'payments_app/admin/refund_payment.html', context)


@login_required
def admin_invoice_list(request):
    """List all invoices for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get all invoices
    invoices = Invoice.objects.all().order_by('-issue_date')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)

    context = {
        'invoices': invoices,
        'status_filter': status_filter,
        'status_choices': Invoice.STATUS_CHOICES,
    }

    return render(request, 'payments_app/admin/invoice_list.html', context)


@login_required
def admin_invoice_detail(request, invoice_number):
    """View invoice details for admin"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('venues_app:home')

    # Get the invoice
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    context = {
        'invoice': invoice,
        'booking': invoice.booking,
        'transaction': invoice.transaction,
    }

    return render(request, 'payments_app/admin/invoice_detail.html', context)
