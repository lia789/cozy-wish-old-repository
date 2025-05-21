import random
import csv
import os
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from venues_app.models import Venue, Service, Category
from discount_app.models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test data for the discount app'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating discount test data...'))
        
        # Create discount test data directory if it doesn't exist
        test_data_dir = 'discount_app_manual_test_dummy_data'
        if not os.path.exists(test_data_dir):
            os.makedirs(test_data_dir)
        
        # Get users
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            service_providers = User.objects.filter(is_service_provider=True)
            customers = User.objects.filter(is_customer=True)
            
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
                return
            
            if not service_providers:
                self.stdout.write(self.style.ERROR('No service providers found. Please create service providers first.'))
                return
            
            if not customers:
                self.stdout.write(self.style.ERROR('No customers found. Please create customers first.'))
                return
            
            # Get venues and services
            venues = Venue.objects.filter(approval_status='approved')
            services = Service.objects.filter(is_active=True)
            categories = Category.objects.all()
            
            if not venues:
                self.stdout.write(self.style.ERROR('No approved venues found. Please create venues first.'))
                return
            
            if not services:
                self.stdout.write(self.style.ERROR('No active services found. Please create services first.'))
                return
            
            if not categories:
                self.stdout.write(self.style.ERROR('No categories found. Please create categories first.'))
                return
            
            # Create venue discounts
            venue_discounts = []
            for i in range(20):
                venue = random.choice(venues)
                
                # Create discount with random values
                discount_type = random.choice(['percentage', 'fixed'])
                if discount_type == 'percentage':
                    discount_value = Decimal(str(random.randint(5, 50)))
                else:
                    discount_value = Decimal(str(random.randint(5, 30)))
                
                start_date = timezone.now() - timedelta(days=random.randint(0, 10))
                end_date = timezone.now() + timedelta(days=random.randint(10, 60))
                
                is_approved = random.choice([True, False])
                
                venue_discount = VenueDiscount.objects.create(
                    name=f"Venue Discount {i+1}",
                    description=f"Special discount for {venue.name}",
                    discount_type=discount_type,
                    discount_value=discount_value,
                    start_date=start_date,
                    end_date=end_date,
                    venue=venue,
                    min_booking_value=Decimal(str(random.randint(0, 50))),
                    max_discount_amount=Decimal(str(random.randint(0, 100))) if random.choice([True, False]) else None,
                    is_approved=is_approved,
                    created_by=venue.owner,
                    approved_by=admin_user if is_approved else None,
                    approved_at=timezone.now() if is_approved else None
                )
                
                venue_discounts.append(venue_discount)
                
                self.stdout.write(self.style.SUCCESS(f'Created venue discount: {venue_discount.name}'))
            
            # Create service discounts
            service_discounts = []
            for i in range(30):
                service = random.choice(services)
                
                # Create discount with random values
                discount_type = random.choice(['percentage', 'fixed'])
                if discount_type == 'percentage':
                    discount_value = Decimal(str(random.randint(5, 50)))
                else:
                    discount_value = Decimal(str(random.randint(5, 30)))
                
                start_date = timezone.now() - timedelta(days=random.randint(0, 10))
                end_date = timezone.now() + timedelta(days=random.randint(10, 60))
                
                is_approved = random.choice([True, False])
                
                service_discount = ServiceDiscount.objects.create(
                    name=f"Service Discount {i+1}",
                    description=f"Special discount for {service.title}",
                    discount_type=discount_type,
                    discount_value=discount_value,
                    start_date=start_date,
                    end_date=end_date,
                    service=service,
                    is_approved=is_approved,
                    created_by=service.venue.owner,
                    approved_by=admin_user if is_approved else None,
                    approved_at=timezone.now() if is_approved else None
                )
                
                service_discounts.append(service_discount)
                
                self.stdout.write(self.style.SUCCESS(f'Created service discount: {service_discount.name}'))
            
            # Create platform discounts
            platform_discounts = []
            for i in range(10):
                # Create discount with random values
                discount_type = random.choice(['percentage', 'fixed'])
                if discount_type == 'percentage':
                    discount_value = Decimal(str(random.randint(5, 30)))
                else:
                    discount_value = Decimal(str(random.randint(5, 20)))
                
                start_date = timezone.now() - timedelta(days=random.randint(0, 10))
                end_date = timezone.now() + timedelta(days=random.randint(10, 60))
                
                category = random.choice(categories) if random.choice([True, False]) else None
                
                platform_discount = PlatformDiscount.objects.create(
                    name=f"Platform Discount {i+1}",
                    description=f"Special platform-wide discount",
                    discount_type=discount_type,
                    discount_value=discount_value,
                    start_date=start_date,
                    end_date=end_date,
                    category=category,
                    min_booking_value=Decimal(str(random.randint(0, 50))),
                    max_discount_amount=Decimal(str(random.randint(0, 100))) if random.choice([True, False]) else None,
                    is_featured=random.choice([True, False]),
                    created_by=admin_user
                )
                
                platform_discounts.append(platform_discount)
                
                self.stdout.write(self.style.SUCCESS(f'Created platform discount: {platform_discount.name}'))
            
            # Create discount usages
            discount_usages = []
            for i in range(50):
                # Choose a random discount
                discount_type = random.choice(['VenueDiscount', 'ServiceDiscount', 'PlatformDiscount'])
                if discount_type == 'VenueDiscount':
                    discount = random.choice(venue_discounts)
                    discount_id = discount.id
                    original_price = Decimal(str(random.randint(50, 200)))
                elif discount_type == 'ServiceDiscount':
                    discount = random.choice(service_discounts)
                    discount_id = discount.id
                    original_price = discount.service.price
                else:
                    discount = random.choice(platform_discounts)
                    discount_id = discount.id
                    original_price = Decimal(str(random.randint(50, 200)))
                
                # Calculate discount amount and final price
                if discount.discount_type == 'percentage':
                    discount_amount = original_price * discount.discount_value / 100
                    if discount.max_discount_amount and discount_amount > discount.max_discount_amount:
                        discount_amount = discount.max_discount_amount
                else:
                    discount_amount = discount.discount_value
                
                final_price = original_price - discount_amount
                
                # Create usage record
                usage_date = timezone.now() - timedelta(days=random.randint(0, 30))
                
                discount_usage = DiscountUsage.objects.create(
                    discount_type=discount_type,
                    discount_id=discount_id,
                    user=random.choice(customers),
                    booking_id=random.randint(1, 100),  # Dummy booking ID
                    usage_date=usage_date,
                    original_price=original_price,
                    discount_amount=discount_amount,
                    final_price=final_price
                )
                
                discount_usages.append(discount_usage)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(discount_usages)} discount usage records'))
            
            # Export data to CSV files
            self._export_to_csv(venue_discounts, os.path.join(test_data_dir, 'venue_discounts.csv'))
            self._export_to_csv(service_discounts, os.path.join(test_data_dir, 'service_discounts.csv'))
            self._export_to_csv(platform_discounts, os.path.join(test_data_dir, 'platform_discounts.csv'))
            self._export_to_csv(discount_usages, os.path.join(test_data_dir, 'discount_usages.csv'))
            
            self.stdout.write(self.style.SUCCESS('Discount test data created successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating discount test data: {str(e)}'))
    
    def _export_to_csv(self, objects, filename):
        """Export objects to a CSV file"""
        if not objects:
            return
        
        # Get field names from the first object
        model = objects[0].__class__
        field_names = [field.name for field in model._meta.fields]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(field_names)
            
            # Write data
            for obj in objects:
                row = []
                for field in field_names:
                    value = getattr(obj, field)
                    row.append(str(value))
                writer.writerow(row)
        
        self.stdout.write(self.style.SUCCESS(f'Exported data to {filename}'))
