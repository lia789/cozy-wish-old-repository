import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from venues_app.models import USCity
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import US cities data from us_cities.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='venues_app/us_cities.csv',
            help='Path to the CSV file containing US cities data'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from {file_path}'))
        
        # Count total rows for progress reporting
        with open(file_path, 'r') as f:
            total_rows = sum(1 for _ in csv.reader(f)) - 1  # Subtract header row
        
        # Process the CSV file
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            
            # Use transaction to speed up bulk import
            with transaction.atomic():
                # Clear existing data if any
                USCity.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Cleared existing US cities data'))
                
                # Import new data
                counter = 0
                for row in reader:
                    try:
                        USCity.objects.create(
                            city=row['city'],
                            state_id=row['state_id'],
                            state_name=row['state_name'],
                            county_name=row['county_name'],
                            latitude=Decimal(row['lat']),
                            longitude=Decimal(row['lng']),
                            zip_codes=row['zips'],
                            city_id=row['id']
                        )
                        counter += 1
                        
                        # Report progress every 1000 rows
                        if counter % 1000 == 0:
                            self.stdout.write(self.style.SUCCESS(f'Imported {counter}/{total_rows} cities...'))
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error importing row {counter}: {e}'))
                        self.stdout.write(self.style.ERROR(f'Row data: {row}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {counter} US cities'))
