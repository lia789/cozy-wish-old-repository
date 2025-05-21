import csv
import os
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from venues_app.models import Venue, Service, Category
from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage, DiscountType

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for discount_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            default='discount_app/discount_app_manual_test_dummy_data',
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
                self.import_venue_discounts(os.path.join(directory, 'venue_discounts.csv'))
                self.import_service_discounts(os.path.join(directory, 'service_discounts.csv'))
                self.import_platform_discounts(os.path.join(directory, 'platform_discounts.csv'))
                self.import_discount_usages(os.path.join(directory, 'discount_usages.csv'))
            
            self.stdout.write(self.style.SUCCESS('Successfully imported dummy data for discount_app'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))
    
    def clear_existing_data(self):
        """Clear existing discount data"""
        self.stdout.write('Clearing existing discount data...')
        DiscountUsage.objects.all().delete()
        VenueDiscount.objects.all().delete()
        ServiceDiscount.objects.all().delete()
        PlatformDiscount.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing discount data cleared'))
    
    def import_venue_discounts(self, csv_file):
        """Import venue discounts from CSV file"""
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'File {csv_file} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing venue discounts from {csv_file}...')
        count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get related objects
                    venue = Venue.objects.get(name=row['venue_name'])
                    created_by = User.objects.get(email=row['created_by_email'])
                    
                    # Handle approved_by (may be None)
                    approved_by = None
                    if row['is_approved'] == 'True' and row['approved_by_email']:
                        approved_by = User.objects.get(email=row['approved_by_email'])
                    
                    # Parse dates
                    start_date = datetime.strptime(row['start_date'], '%Y-%m-%d %H:%M:%S')
                    end_date = datetime.strptime(row['end_date'], '%Y-%m-%d %H:%M:%S')
                    approved_at = None
                    if row['approved_at']:
                        approved_at = datetime.strptime(row['approved_at'], '%Y-%m-%d %H:%M:%S')
                    
                    # Handle optional decimal fields
                    min_booking_value = Decimal(row['min_booking_value']) if row['min_booking_value'] else None
                    max_discount_amount = Decimal(row['max_discount_amount']) if row['max_discount_amount'] else None
                    
                    # Create venue discount
                    venue_discount = VenueDiscount.objects.create(
                        name=row['name'],
                        description=row['description'],
                        discount_type=row['discount_type'],
                        discount_value=Decimal(row['discount_value']),
                        start_date=start_date,
                        end_date=end_date,
                        min_booking_value=min_booking_value,
                        max_discount_amount=max_discount_amount,
                        venue=venue,
                        created_by=created_by,
                        is_approved=row['is_approved'] == 'True',
                        approved_by=approved_by,
                        approved_at=approved_at,
                        approval_comments=row['approval_comments']
                    )
                    
                    count += 1
                    self.stdout.write(f'  Imported venue discount: {venue_discount.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error importing venue discount: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} venue discounts'))
    
    def import_service_discounts(self, csv_file):
        """Import service discounts from CSV file"""
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'File {csv_file} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing service discounts from {csv_file}...')
        count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get related objects
                    venue = Venue.objects.get(name=row['venue_name'])
                    service = Service.objects.get(title=row['service_title'], venue=venue)
                    created_by = User.objects.get(email=row['created_by_email'])
                    
                    # Handle approved_by (may be None)
                    approved_by = None
                    if row['is_approved'] == 'True' and row['approved_by_email']:
                        approved_by = User.objects.get(email=row['approved_by_email'])
                    
                    # Parse dates
                    start_date = datetime.strptime(row['start_date'], '%Y-%m-%d %H:%M:%S')
                    end_date = datetime.strptime(row['end_date'], '%Y-%m-%d %H:%M:%S')
                    approved_at = None
                    if row['approved_at']:
                        approved_at = datetime.strptime(row['approved_at'], '%Y-%m-%d %H:%M:%S')
                    
                    # Handle optional decimal fields
                    min_booking_value = Decimal(row['min_booking_value']) if row['min_booking_value'] else None
                    max_discount_amount = Decimal(row['max_discount_amount']) if row['max_discount_amount'] else None
                    
                    # Create service discount
                    service_discount = ServiceDiscount.objects.create(
                        name=row['name'],
                        description=row['description'],
                        discount_type=row['discount_type'],
                        discount_value=Decimal(row['discount_value']),
                        start_date=start_date,
                        end_date=end_date,
                        min_booking_value=min_booking_value,
                        max_discount_amount=max_discount_amount,
                        service=service,
                        created_by=created_by,
                        is_approved=row['is_approved'] == 'True',
                        approved_by=approved_by,
                        approved_at=approved_at,
                        approval_comments=row['approval_comments']
                    )
                    
                    count += 1
                    self.stdout.write(f'  Imported service discount: {service_discount.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error importing service discount: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} service discounts'))
    
    def import_platform_discounts(self, csv_file):
        """Import platform discounts from CSV file"""
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'File {csv_file} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing platform discounts from {csv_file}...')
        count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get related objects
                    created_by = User.objects.get(email=row['created_by_email'])
                    approved_by = User.objects.get(email=row['approved_by_email']) if row['approved_by_email'] else None
                    
                    # Get category (may be None)
                    category = None
                    if row['category_name']:
                        category = Category.objects.get(name=row['category_name'])
                    
                    # Parse dates
                    start_date = datetime.strptime(row['start_date'], '%Y-%m-%d %H:%M:%S')
                    end_date = datetime.strptime(row['end_date'], '%Y-%m-%d %H:%M:%S')
                    approved_at = None
                    if row['approved_at']:
                        approved_at = datetime.strptime(row['approved_at'], '%Y-%m-%d %H:%M:%S')
                    
                    # Handle optional decimal fields
                    min_booking_value = Decimal(row['min_booking_value']) if row['min_booking_value'] else None
                    max_discount_amount = Decimal(row['max_discount_amount']) if row['max_discount_amount'] else None
                    
                    # Create platform discount
                    platform_discount = PlatformDiscount.objects.create(
                        name=row['name'],
                        description=row['description'],
                        discount_type=row['discount_type'],
                        discount_value=Decimal(row['discount_value']),
                        start_date=start_date,
                        end_date=end_date,
                        min_booking_value=min_booking_value,
                        max_discount_amount=max_discount_amount,
                        category=category,
                        is_featured=row['is_featured'] == 'True',
                        created_by=created_by,
                        is_approved=row['is_approved'] == 'True',
                        approved_by=approved_by,
                        approved_at=approved_at
                    )
                    
                    count += 1
                    self.stdout.write(f'  Imported platform discount: {platform_discount.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error importing platform discount: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} platform discounts'))
    
    def import_discount_usages(self, csv_file):
        """Import discount usages from CSV file"""
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'File {csv_file} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing discount usages from {csv_file}...')
        count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get user
                    user = User.objects.get(email=row['user_email'])
                    
                    # Parse date
                    used_at = datetime.strptime(row['used_at'], '%Y-%m-%d %H:%M:%S')
                    
                    # Create a mock booking object since we can't create real bookings without the booking_cart_app
                    # In a real scenario, this would be a foreign key to a Booking object
                    booking_id = int(row['booking_id'])
                    
                    # Create discount usage
                    discount_usage = DiscountUsage(
                        user=user,
                        discount_type=row['discount_type'],
                        discount_id=int(row['discount_id']),
                        booking_id=booking_id,
                        original_price=Decimal(row['original_price']),
                        discount_amount=Decimal(row['discount_amount']),
                        final_price=Decimal(row['final_price'])
                    )
                    
                    # Set used_at manually since it's auto_now_add
                    discount_usage.used_at = used_at
                    
                    # We don't save this to the database to avoid foreign key constraints
                    # In a real scenario with the booking_cart_app installed, we would save it
                    
                    count += 1
                    self.stdout.write(f'  Prepared discount usage for user: {user.email} (not saved due to booking FK constraint)')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error importing discount usage: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Prepared {count} discount usages (not saved due to booking FK constraint)'))
