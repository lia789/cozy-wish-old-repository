import os
import csv
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from venues_app.models import Service, Venue
from booking_cart_app.models import CartItem, Booking, BookingItem, ServiceAvailability

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for booking_cart_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            default='booking_cart_app/booking_cart_app_manual_test_dummy_data',
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
                self.import_service_availability(os.path.join(directory, 'service_availability.csv'))
                self.import_cart_items(os.path.join(directory, 'cart_items.csv'))
                self.import_bookings(os.path.join(directory, 'bookings.csv'))
                self.import_booking_items(os.path.join(directory, 'booking_items.csv'))
            
            self.stdout.write(self.style.SUCCESS('Successfully imported dummy data for booking_cart_app'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))
    
    def clear_existing_data(self):
        """Clear existing data from the models"""
        self.stdout.write('Clearing existing data...')
        CartItem.objects.all().delete()
        BookingItem.objects.all().delete()
        Booking.objects.all().delete()
        ServiceAvailability.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))
    
    def import_service_availability(self, file_path):
        """Import service availability data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing service availability from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                service_title = row['service_title']
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                time_slot = datetime.strptime(row['time_slot'], '%H:%M:%S').time()
                max_bookings = int(row['max_bookings'])
                current_bookings = int(row['current_bookings'])
                is_available = row['is_available'].lower() == 'true'
                
                # Find the service
                service = Service.objects.filter(title=service_title).first()
                if not service:
                    self.stdout.write(self.style.WARNING(f'Service {service_title} not found, skipping'))
                    continue
                
                # Create or update service availability
                availability, created = ServiceAvailability.objects.update_or_create(
                    service=service,
                    date=date,
                    time_slot=time_slot,
                    defaults={
                        'max_bookings': max_bookings,
                        'current_bookings': current_bookings,
                        'is_available': is_available
                    }
                )
                
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} service availability records'))
    
    def import_cart_items(self, file_path):
        """Import cart items data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing cart items from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_email = row['user_email']
                service_title = row['service_title']
                quantity = int(row['quantity'])
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                time_slot = datetime.strptime(row['time_slot'], '%H:%M:%S').time()
                expires_at = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
                
                # Find the user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f'User {user_email} not found, skipping'))
                    continue
                
                # Find the service
                service = Service.objects.filter(title=service_title).first()
                if not service:
                    self.stdout.write(self.style.WARNING(f'Service {service_title} not found, skipping'))
                    continue
                
                # Create cart item
                try:
                    cart_item, created = CartItem.objects.update_or_create(
                        user=user,
                        service=service,
                        date=date,
                        time_slot=time_slot,
                        defaults={
                            'quantity': quantity,
                            'expires_at': timezone.make_aware(expires_at) if timezone.is_naive(expires_at) else expires_at
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating cart item: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} cart items'))
    
    def import_bookings(self, file_path):
        """Import bookings data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing bookings from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                booking_id = row['booking_id']
                user_email = row['user_email']
                venue_name = row['venue_name']
                status = row['status']
                total_price = Decimal(row['total_price'])
                booking_date = datetime.strptime(row['booking_date'], '%Y-%m-%d %H:%M:%S')
                notes = row['notes']
                cancellation_reason = row['cancellation_reason']
                dispute_reason = row['dispute_reason']
                
                # Find the user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f'User {user_email} not found, skipping'))
                    continue
                
                # Find the venue
                venue = Venue.objects.filter(name=venue_name).first()
                if not venue:
                    self.stdout.write(self.style.WARNING(f'Venue {venue_name} not found, skipping'))
                    continue
                
                # Create booking
                try:
                    booking, created = Booking.objects.update_or_create(
                        booking_id=uuid.UUID(booking_id),
                        defaults={
                            'user': user,
                            'venue': venue,
                            'status': status,
                            'total_price': total_price,
                            'booking_date': timezone.make_aware(booking_date) if timezone.is_naive(booking_date) else booking_date,
                            'notes': notes,
                            'cancellation_reason': cancellation_reason,
                            'dispute_reason': dispute_reason
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating booking: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} bookings'))
    
    def import_booking_items(self, file_path):
        """Import booking items data from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing booking items from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                booking_id = row['booking_id']
                service_title = row['service_title']
                service_price = Decimal(row['service_price'])
                quantity = int(row['quantity'])
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                time_slot = datetime.strptime(row['time_slot'], '%H:%M:%S').time()
                
                # Find the booking
                booking = Booking.objects.filter(booking_id=uuid.UUID(booking_id)).first()
                if not booking:
                    self.stdout.write(self.style.WARNING(f'Booking {booking_id} not found, skipping'))
                    continue
                
                # Find the service
                service = Service.objects.filter(title=service_title).first()
                if not service:
                    self.stdout.write(self.style.WARNING(f'Service {service_title} not found, creating booking item without service reference'))
                
                # Create booking item
                try:
                    booking_item = BookingItem.objects.create(
                        booking=booking,
                        service=service,
                        service_title=service_title,
                        service_price=service_price,
                        quantity=quantity,
                        date=date,
                        time_slot=time_slot
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating booking item: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} booking items'))
