import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime

from accounts_app.models import (
    CustomerProfile, ServiceProviderProfile,
    StaffMember, UserActivity, LoginAttempt
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for accounts_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            default='accounts_app/accounts_app_manual_test_dummy_data',
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
                self.import_users(os.path.join(directory, 'custom_users.csv'))
                self.import_customer_profiles(os.path.join(directory, 'customer_profiles.csv'))
                self.import_service_provider_profiles(os.path.join(directory, 'service_provider_profiles.csv'))
                self.import_staff_members(os.path.join(directory, 'staff_members.csv'))
                self.import_user_activities(os.path.join(directory, 'user_activities.csv'))
                self.import_login_attempts(os.path.join(directory, 'login_attempts.csv'))

            self.stdout.write(self.style.SUCCESS('Successfully imported accounts_app dummy data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))

    def clear_existing_data(self):
        """Clear existing data from the models"""
        self.stdout.write('Clearing existing accounts_app data...')
        LoginAttempt.objects.all().delete()
        UserActivity.objects.all().delete()
        StaffMember.objects.all().delete()
        ServiceProviderProfile.objects.all().delete()
        CustomerProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Keep superuser accounts
        self.stdout.write(self.style.SUCCESS('Existing accounts_app data cleared'))

    def import_users(self, file_path):
        """Import users from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing users from {file_path}...')
        count = 0

        # Temporarily disconnect the signal to prevent automatic profile creation
        from django.db.models.signals import post_save
        from accounts_app.signals import create_user_profile
        post_save.disconnect(create_user_profile, sender=User)

        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip if user already exists
                    if User.objects.filter(email=row['email']).exists():
                        self.stdout.write(f"User {row['email']} already exists, skipping")
                        continue

                    # Create user
                    user = User.objects.create_user(
                        email=row['email'],
                        password=row['password'],
                        is_customer=row['is_customer'] == 'True',
                        is_service_provider=row['is_service_provider'] == 'True',
                        is_staff=row['is_staff'] == 'True',
                        is_superuser=row['is_superuser'] == 'True',
                        is_active=row['is_active'] == 'True',
                        email_verified=row['email_verified'] == 'True'
                    )
                    count += 1
        finally:
            # Reconnect the signal
            post_save.connect(create_user_profile, sender=User)

        self.stdout.write(self.style.SUCCESS(f'Imported {count} users'))

    def import_customer_profiles(self, file_path):
        """Import customer profiles from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing customer profiles from {file_path}...')
        count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    user = User.objects.get(email=row['user_email'])

                    # Create or update profile
                    profile, created = CustomerProfile.objects.update_or_create(
                        user=user,
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'gender': row['gender'],
                            'birth_month': int(row['birth_month']),
                            'birth_year': int(row['birth_year']),
                            'phone_number': row['phone_number'],
                            'address': row['address'],
                            'city': row['city']
                        }
                    )
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found: {row['user_email']}"))

        self.stdout.write(self.style.SUCCESS(f'Imported {count} customer profiles'))

    def import_service_provider_profiles(self, file_path):
        """Import service provider profiles from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing service provider profiles from {file_path}...')
        count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    user = User.objects.get(email=row['user_email'])

                    # Use raw SQL to create or update the profile
                    # This is necessary because the model definition doesn't match the database schema
                    from django.db import connection
                    cursor = connection.cursor()

                    # Check if profile exists
                    cursor.execute(
                        "SELECT id FROM accounts_app_serviceproviderprofile WHERE user_id = %s",
                        [user.id]
                    )
                    profile_id = cursor.fetchone()

                    if profile_id:
                        # Update existing profile
                        slug = slugify(row['business_name'])

                        cursor.execute(
                            """
                            UPDATE accounts_app_serviceproviderprofile
                            SET business_name = %s,
                                venue_name = %s,
                                phone_number = %s,
                                contact_person_name = %s,
                                updated_at = %s,
                                slug = %s
                            WHERE user_id = %s
                            """,
                            [
                                row['business_name'],
                                row['venue_name'],
                                row['phone_number'],
                                row['contact_person_name'],
                                timezone.now(),
                                slug,
                                user.id
                            ]
                        )
                    else:
                        # Create new profile
                        slug = slugify(row['business_name'])

                        cursor.execute(
                            """
                            INSERT INTO accounts_app_serviceproviderprofile
                            (business_name, venue_name, phone_number, contact_person_name,
                             created_at, updated_at, user_id, slug)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            [
                                row['business_name'],
                                row['venue_name'],
                                row['phone_number'],
                                row['contact_person_name'],
                                timezone.now(),
                                timezone.now(),
                                user.id,
                                slug
                            ]
                        )
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found: {row['user_email']}"))

        self.stdout.write(self.style.SUCCESS(f'Imported {count} service provider profiles'))

    def import_staff_members(self, file_path):
        """Import staff members from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing staff members from {file_path}...')
        count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Get the service provider
                    user = User.objects.get(email=row['service_provider_email'])
                    service_provider = ServiceProviderProfile.objects.get(user=user)

                    # Create or update staff member
                    staff, created = StaffMember.objects.update_or_create(
                        service_provider=service_provider,
                        name=row['name'],
                        defaults={
                            'designation': row['designation'],
                            'is_active': row['is_active'] == 'True'
                        }
                    )
                    count += 1
                except (User.DoesNotExist, ServiceProviderProfile.DoesNotExist):
                    self.stdout.write(self.style.WARNING(f"Service provider not found: {row['service_provider_email']}"))

        self.stdout.write(self.style.SUCCESS(f'Imported {count} staff members'))

    def import_user_activities(self, file_path):
        """Import user activities from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing user activities from {file_path}...')
        count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    user = User.objects.get(email=row['user_email'])

                    # Parse timestamp
                    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                    timestamp = timezone.make_aware(timestamp)

                    # Create user activity
                    activity = UserActivity.objects.create(
                        user=user,
                        activity_type=row['activity_type'],
                        ip_address=row['ip_address'],
                        user_agent=row['user_agent'],
                        timestamp=timestamp,
                        details=row['details']
                    )
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found: {row['user_email']}"))

        self.stdout.write(self.style.SUCCESS(f'Imported {count} user activities'))

    def import_login_attempts(self, file_path):
        """Import login attempts from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return

        self.stdout.write(f'Importing login attempts from {file_path}...')
        count = 0

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse timestamp
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                timestamp = timezone.make_aware(timestamp)

                # Create login attempt
                attempt = LoginAttempt.objects.create(
                    email=row['email'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    timestamp=timestamp,
                    was_successful=row['was_successful'] == 'True'
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Imported {count} login attempts'))
