import uuid
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from booking_cart_app.models import Booking
from .models import PaymentMethod, Transaction, Invoice

def validate_credit_card(card_number):
    """
    Validate a credit card number using the Luhn algorithm.
    
    Args:
        card_number (str): The credit card number to validate
        
    Returns:
        bool: True if the card number is valid, False otherwise
    """
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Check if the card number contains only digits
    if not card_number.isdigit():
        return False
    
    # Check if the card number is of valid length (13-19 digits)
    if not 13 <= len(card_number) <= 19:
        return False
    
    # Luhn algorithm
    digits = [int(d) for d in card_number]
    checksum = 0
    
    # Double every second digit from right to left
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        if doubled > 9:
            doubled -= 9
        digits[i] = doubled
    
    # Sum all digits
    checksum = sum(digits)
    
    # If the sum is divisible by 10, the card number is valid
    return checksum % 10 == 0

def mask_card_number(card_number):
    """
    Mask a credit card number for display, showing only the last 4 digits.
    
    Args:
        card_number (str): The credit card number to mask
        
    Returns:
        str: The masked card number
    """
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Mask all but the last 4 digits
    masked = '*' * (len(card_number) - 4) + card_number[-4:]
    
    # Format the masked number for display
    formatted = ''
    for i in range(0, len(masked), 4):
        formatted += masked[i:i+4] + ' '
    
    return formatted.strip()

def get_last_four_digits(card_number):
    """
    Get the last four digits of a credit card number.
    
    Args:
        card_number (str): The credit card number
        
    Returns:
        str: The last four digits of the card number
    """
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Return the last 4 digits
    return card_number[-4:]

def process_payment(user, booking, payment_method_type, payment_method_details, amount):
    """
    Process a payment for a booking.
    
    Args:
        user (User): The user making the payment
        booking (Booking): The booking being paid for
        payment_method_type (str): The type of payment method
        payment_method_details (str): Details of the payment method
        amount (Decimal): The amount to charge
        
    Returns:
        Transaction: The created transaction
    """
    # In the MVP version, we'll just create a transaction with status 'completed'
    # In a real implementation, this would integrate with a payment gateway
    
    with transaction.atomic():
        # Create the transaction
        transaction_obj = Transaction.objects.create(
            user=user,
            booking=booking,
            amount=amount,
            status='completed',  # In MVP, all payments succeed
            payment_method=payment_method_type,
            payment_method_details=payment_method_details,
            notes='Payment processed successfully'
        )
    
    return transaction_obj

def get_transaction_history(user):
    """
    Get transaction history for a user.
    
    Args:
        user (User): The user to get transactions for
        
    Returns:
        QuerySet: A queryset of transactions for the user
    """
    return Transaction.objects.filter(user=user).order_by('-created_at')

def get_provider_transaction_history(user):
    """
    Get transaction history for a service provider.
    
    Args:
        user (User): The service provider to get transactions for
        
    Returns:
        QuerySet: A queryset of transactions for the provider's venues
    """
    # Get all venues owned by the provider
    venues = user.venues.all()
    
    # Get all bookings for those venues
    bookings = Booking.objects.filter(venue__in=venues)
    
    # Get all transactions for those bookings
    return Transaction.objects.filter(booking__in=bookings).order_by('-created_at')

def get_transaction_analytics(user=None, start_date=None, end_date=None):
    """
    Get transaction analytics.
    
    Args:
        user (User, optional): The user to get analytics for. If None, get analytics for all users.
        start_date (date, optional): The start date for the analytics period. If None, use all time.
        end_date (date, optional): The end date for the analytics period. If None, use today.
        
    Returns:
        dict: A dictionary of analytics data
    """
    # Base queryset
    transactions = Transaction.objects.all()
    
    # Filter by user if provided
    if user:
        if user.is_service_provider:
            # For service providers, get transactions for their venues
            venues = user.venues.all()
            bookings = Booking.objects.filter(venue__in=venues)
            transactions = transactions.filter(booking__in=bookings)
        else:
            # For customers, get their transactions
            transactions = transactions.filter(user=user)
    
    # Filter by date range if provided
    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
    
    # Calculate analytics
    total_transactions = transactions.count()
    total_amount = transactions.filter(status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    completed_transactions = transactions.filter(status='completed').count()
    failed_transactions = transactions.filter(status='failed').count()
    refunded_transactions = transactions.filter(status='refunded').count()
    
    # Calculate percentages
    completed_percentage = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
    failed_percentage = (failed_transactions / total_transactions * 100) if total_transactions > 0 else 0
    refunded_percentage = (refunded_transactions / total_transactions * 100) if total_transactions > 0 else 0
    
    # Group by day
    daily_transactions = transactions.filter(status='completed').extra(
        select={'day': "DATE(created_at)"}
    ).values('day').annotate(
        count=models.Count('id'),
        total=models.Sum('amount')
    ).order_by('day')
    
    return {
        'total_transactions': total_transactions,
        'total_amount': total_amount,
        'completed_transactions': completed_transactions,
        'failed_transactions': failed_transactions,
        'refunded_transactions': refunded_transactions,
        'completed_percentage': completed_percentage,
        'failed_percentage': failed_percentage,
        'refunded_percentage': refunded_percentage,
        'daily_transactions': list(daily_transactions)
    }

def generate_invoice(booking):
    """
    Generate an invoice for a booking.
    
    Args:
        booking (Booking): The booking to generate an invoice for
        
    Returns:
        Invoice: The created invoice
    """
    # Check if an invoice already exists for this booking
    existing_invoice = Invoice.objects.filter(booking=booking).first()
    if existing_invoice:
        return existing_invoice
    
    # Create a new invoice
    invoice = Invoice.objects.create(
        invoice_number=uuid.uuid4(),
        user=booking.user,
        booking=booking,
        amount=booking.total_price,
        status='pending',
        issue_date=timezone.now(),
        due_date=timezone.now() + timezone.timedelta(days=1),
        notes=f'Invoice for booking {booking.booking_id}'
    )
    
    return invoice

def generate_invoice_pdf(invoice):
    """
    Generate a PDF for an invoice.
    
    Args:
        invoice (Invoice): The invoice to generate a PDF for
        
    Returns:
        BytesIO: A BytesIO object containing the PDF
    """
    # In the MVP version, we'll just return a placeholder message
    # In a real implementation, this would generate a PDF using a library like ReportLab
    
    from io import BytesIO
    
    pdf_content = BytesIO()
    pdf_content.write(b'This is a placeholder for the invoice PDF')
    pdf_content.seek(0)
    
    return pdf_content

def get_invoice_history(user):
    """
    Get invoice history for a user.
    
    Args:
        user (User): The user to get invoices for
        
    Returns:
        QuerySet: A queryset of invoices for the user
    """
    return Invoice.objects.filter(user=user).order_by('-issue_date')

def get_provider_invoice_history(user):
    """
    Get invoice history for a service provider.
    
    Args:
        user (User): The service provider to get invoices for
        
    Returns:
        QuerySet: A queryset of invoices for the provider's venues
    """
    # Get all venues owned by the provider
    venues = user.venues.all()
    
    # Get all bookings for those venues
    bookings = Booking.objects.filter(venue__in=venues)
    
    # Get all invoices for those bookings
    return Invoice.objects.filter(booking__in=bookings).order_by('-issue_date')
