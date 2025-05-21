import os
import csv
import uuid
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from booking_cart_app.models import Booking
from payments_app.models import PaymentMethod, Transaction, Invoice

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for payments_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            default='payments_app/payments_app_manual_test_dummy_data',
            help='Directory containing the CSV files'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        directory = options['directory']
        clear_data = options['clear']
        
        # Check if directory exists
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR(f'Directory {directory} does not exist'))
            return
        
        # Clear existing data if requested
        if clear_data:
            self.clear_existing_data()
        
        # Import data
        try:
            with transaction.atomic():
                self.import_payment_methods(os.path.join(directory, 'payment_methods.csv'))
                self.import_transactions(os.path.join(directory, 'transactions.csv'))
                self.import_invoices(os.path.join(directory, 'invoices.csv'))
            
            self.stdout.write(self.style.SUCCESS('Successfully imported dummy data for payments_app'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))
    
    def clear_existing_data(self):
        """Clear existing data from the models"""
        self.stdout.write('Clearing existing data...')
        Invoice.objects.all().delete()
        Transaction.objects.all().delete()
        PaymentMethod.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))
    
    def import_payment_methods(self, file_path):
        """Import payment methods data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing payment methods from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_email = row['user_email']
                payment_type = row['payment_type']
                name = row['name']
                last_four = row['last_four']
                expiry_date = row['expiry_date'] if row['expiry_date'] else None
                is_default = row['is_default'].lower() == 'true'
                
                # Find the user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f'User with email {user_email} not found, skipping'))
                    continue
                
                # Create payment method
                try:
                    payment_method, created = PaymentMethod.objects.update_or_create(
                        user=user,
                        payment_type=payment_type,
                        name=name,
                        defaults={
                            'last_four': last_four,
                            'expiry_date': expiry_date,
                            'is_default': is_default
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating payment method: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} payment methods'))
    
    def import_transactions(self, file_path):
        """Import transactions data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing transactions from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                transaction_id = row['transaction_id']
                user_email = row['user_email']
                booking_id = row['booking_id']
                amount = Decimal(row['amount'])
                status = row['status']
                payment_method = row['payment_method']
                payment_method_details = row['payment_method_details']
                created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                notes = row['notes']
                
                # Find the user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f'User with email {user_email} not found, skipping'))
                    continue
                
                # Find the booking
                booking = Booking.objects.filter(booking_id=uuid.UUID(booking_id)).first()
                if not booking:
                    self.stdout.write(self.style.WARNING(f'Booking with ID {booking_id} not found, skipping'))
                    continue
                
                # Create transaction
                try:
                    transaction, created = Transaction.objects.update_or_create(
                        id=uuid.UUID(transaction_id),
                        defaults={
                            'user': user,
                            'booking': booking,
                            'amount': amount,
                            'status': status,
                            'payment_method': payment_method,
                            'payment_method_details': payment_method_details,
                            'created_at': timezone.make_aware(created_at) if timezone.is_naive(created_at) else created_at,
                            'notes': notes
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating transaction: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} transactions'))
    
    def import_invoices(self, file_path):
        """Import invoices data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing invoices from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                invoice_number = row['invoice_number']
                user_email = row['user_email']
                booking_id = row['booking_id']
                transaction_id = row['transaction_id']
                amount = Decimal(row['amount'])
                status = row['status']
                issue_date = datetime.strptime(row['issue_date'], '%Y-%m-%d %H:%M:%S')
                due_date = datetime.strptime(row['due_date'], '%Y-%m-%d %H:%M:%S')
                paid_date = datetime.strptime(row['paid_date'], '%Y-%m-%d %H:%M:%S') if row['paid_date'] else None
                notes = row['notes']
                
                # Find the user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f'User with email {user_email} not found, skipping'))
                    continue
                
                # Find the booking
                booking = Booking.objects.filter(booking_id=uuid.UUID(booking_id)).first()
                if not booking:
                    self.stdout.write(self.style.WARNING(f'Booking with ID {booking_id} not found, skipping'))
                    continue
                
                # Find the transaction
                transaction = Transaction.objects.filter(id=uuid.UUID(transaction_id)).first()
                if not transaction:
                    self.stdout.write(self.style.WARNING(f'Transaction with ID {transaction_id} not found, skipping'))
                    continue
                
                # Create invoice
                try:
                    invoice, created = Invoice.objects.update_or_create(
                        invoice_number=uuid.UUID(invoice_number),
                        defaults={
                            'user': user,
                            'booking': booking,
                            'transaction': transaction,
                            'amount': amount,
                            'status': status,
                            'issue_date': timezone.make_aware(issue_date) if timezone.is_naive(issue_date) else issue_date,
                            'due_date': timezone.make_aware(due_date) if timezone.is_naive(due_date) else due_date,
                            'paid_date': timezone.make_aware(paid_date) if paid_date and timezone.is_naive(paid_date) else paid_date,
                            'notes': notes
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating invoice: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} invoices'))
