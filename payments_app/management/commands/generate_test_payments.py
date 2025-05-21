import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal

from booking_cart_app.models import Booking
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test payments for development and testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of payments to create')
        parser.add_argument('--status', type=str, default=None, 
                            help='Payment status (pending, completed, failed, refunded)')
        parser.add_argument('--clear', action='store_true', help='Clear existing payments before generating new ones')
        parser.add_argument('--user_email', type=str, default=None, help='Generate payments for a specific user')

    def handle(self, *args, **options):
        count = options['count']
        status = options['status']
        clear = options['clear']
        user_email = options['user_email']
        
        # Clear existing payments if requested
        if clear:
            self.clear_existing_payments()
        
        # Get all bookings that don't have transactions
        bookings = Booking.objects.filter(transactions__isnull=True)
        
        # Filter by user if specified
        if user_email:
            user = User.objects.filter(email=user_email).first()
            if not user:
                self.stdout.write(self.style.ERROR(f'User with email {user_email} not found'))
                return
            bookings = bookings.filter(user=user)
        
        # Check if we have enough bookings
        if bookings.count() < count:
            self.stdout.write(
                self.style.WARNING(
                    f'Only {bookings.count()} bookings without transactions available. '
                    f'Generating payments for all available bookings.'
                )
            )
            count = bookings.count()
        
        if count == 0:
            self.stdout.write(self.style.ERROR('No bookings available for generating payments'))
            return
        
        # Get a sample of bookings
        bookings = bookings.order_by('?')[:count]
        
        # Generate payments
        with transaction.atomic():
            payments_created = self.generate_payments(bookings, status)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {payments_created} test payments')
        )
    
    def clear_existing_payments(self):
        """Clear existing payments"""
        transaction_count = Transaction.objects.count()
        invoice_count = Invoice.objects.count()
        
        Transaction.objects.all().delete()
        Invoice.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleared {transaction_count} transactions and {invoice_count} invoices')
        )
    
    def generate_payments(self, bookings, status=None):
        """Generate payments for the given bookings"""
        payments_created = 0
        
        for booking in bookings:
            # Get or create a payment method for the user
            payment_method = self.get_or_create_payment_method(booking.user)
            
            # Determine payment status
            if status:
                payment_status = status
            else:
                # Randomly select a status with weighted probabilities
                statuses = ['completed', 'completed', 'completed', 'refunded', 'failed']
                payment_status = random.choice(statuses)
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=booking.user,
                booking=booking,
                amount=booking.total_price,
                status=payment_status,
                payment_method=payment_method.payment_type,
                payment_method_details=f"{payment_method.get_payment_type_display()} ending in {payment_method.last_four}",
                created_at=self.generate_random_date(booking.booking_date),
                notes=f"Test payment for booking {booking.booking_id}"
            )
            
            # Create or update invoice
            invoice, created = Invoice.objects.get_or_create(
                booking=booking,
                defaults={
                    'user': booking.user,
                    'amount': booking.total_price,
                    'status': 'pending',
                    'issue_date': booking.booking_date,
                    'due_date': booking.booking_date + timedelta(days=1),
                }
            )
            
            # Update invoice status based on transaction status
            if payment_status == 'completed':
                invoice.status = 'paid'
                invoice.transaction = transaction
                invoice.paid_date = transaction.created_at
                booking.status = 'confirmed'
            elif payment_status == 'refunded':
                invoice.status = 'cancelled'
                invoice.transaction = transaction
                booking.status = 'cancelled'
                booking.cancellation_reason = 'Payment refunded'
            else:
                invoice.status = 'pending'
            
            invoice.save()
            booking.save()
            
            payments_created += 1
        
        return payments_created
    
    def get_or_create_payment_method(self, user):
        """Get or create a payment method for the user"""
        # Check if user already has a payment method
        payment_method = PaymentMethod.objects.filter(user=user).first()
        
        if not payment_method:
            # Create a new payment method
            payment_types = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay']
            card_names = ['Visa', 'Mastercard', 'American Express', 'Discover']
            
            payment_method = PaymentMethod.objects.create(
                user=user,
                payment_type=random.choice(payment_types),
                name=f"{user.first_name or 'User'} {user.last_name or user.email.split('@')[0]}",
                last_four=str(random.randint(1000, 9999)),
                expiry_date=timezone.now().date() + timedelta(days=365 * random.randint(1, 5)),
                is_default=True
            )
        
        return payment_method
    
    def generate_random_date(self, base_date):
        """Generate a random date within 7 days after the base date"""
        days = random.randint(0, 7)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        
        return base_date + timedelta(days=days, hours=hours, minutes=minutes)
