import csv
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from datetime import datetime

from notifications_app.models import (
    NotificationCategory, Notification, UserNotification, NotificationPreference
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Imports dummy data for the notifications_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        clear_data = options['clear']
        
        # Get the path to the CSV files
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(base_dir, 'notifications_app_manual_test_dummy_data')
        
        # Check if the directory exists
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Data directory not found: {data_dir}'))
            return
        
        # Clear existing data if requested
        if clear_data:
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Cleared existing notification data'))
        
        # Load the data
        with transaction.atomic():
            self.import_categories(os.path.join(data_dir, 'notification_categories.csv'))
            self.import_notifications(os.path.join(data_dir, 'notifications.csv'))
            self.import_user_notifications(os.path.join(data_dir, 'user_notifications.csv'))
            self.import_preferences(os.path.join(data_dir, 'notification_preferences.csv'))
        
        self.stdout.write(self.style.SUCCESS('Successfully imported notification dummy data'))
    
    def clear_data(self):
        """Clear existing notification data"""
        UserNotification.objects.all().delete()
        NotificationPreference.objects.all().delete()
        Notification.objects.all().delete()
        NotificationCategory.objects.all().delete()
    
    def import_categories(self, file_path):
        """Import notification categories from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            categories_created = 0
            
            for row in reader:
                NotificationCategory.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'description': row['description'],
                        'icon': row['icon'],
                        'color': row['color']
                    }
                )
                categories_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {categories_created} notification categories'))
    
    def import_notifications(self, file_path):
        """Import notifications from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            notifications_created = 0
            
            for row in reader:
                # Parse dates
                created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                expires_at = None
                if row['expires_at'] and row['expires_at'] != 'NULL':
                    expires_at = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
                
                # Parse content type and object ID
                content_type = None
                object_id = None
                if row['content_type_id'] and row['content_type_id'] != 'NULL':
                    try:
                        content_type = ContentType.objects.get(id=row['content_type_id'])
                        object_id = int(row['object_id'])
                    except (ContentType.DoesNotExist, ValueError):
                        self.stdout.write(self.style.WARNING(
                            f"Content type {row['content_type_id']} not found or invalid object_id"
                        ))
                
                # Parse boolean fields
                is_system_wide = False
                if row['is_system_wide'] and row['is_system_wide'].lower() != 'null':
                    is_system_wide = row['is_system_wide'].lower() in ('true', '1', 't', 'y', 'yes')
                
                is_active = True
                if row['is_active'] and row['is_active'].lower() != 'null':
                    is_active = row['is_active'].lower() in ('true', '1', 't', 'y', 'yes')
                
                # Create notification
                try:
                    Notification.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'category_id': row['category_id'],
                            'title': row['title'],
                            'message': row['message'],
                            'priority': row['priority'],
                            'created_at': created_at,
                            'expires_at': expires_at,
                            'is_system_wide': is_system_wide,
                            'is_active': is_active,
                            'content_type': content_type,
                            'object_id': object_id
                        }
                    )
                    notifications_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating notification {row['id']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {notifications_created} notifications'))
    
    def import_user_notifications(self, file_path):
        """Import user notifications from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            user_notifications_created = 0
            
            for row in reader:
                # Parse dates
                read_at = None
                if row['read_at'] and row['read_at'] != 'NULL':
                    read_at = datetime.strptime(row['read_at'], '%Y-%m-%d %H:%M:%S')
                
                deleted_at = None
                if row['deleted_at'] and row['deleted_at'] != 'NULL':
                    deleted_at = datetime.strptime(row['deleted_at'], '%Y-%m-%d %H:%M:%S')
                
                # Parse boolean fields
                is_read = False
                if row['is_read'] and row['is_read'].lower() != 'null':
                    is_read = row['is_read'].lower() in ('true', '1', 't', 'y', 'yes')
                
                is_deleted = False
                if row['is_deleted'] and row['is_deleted'].lower() != 'null':
                    is_deleted = row['is_deleted'].lower() in ('true', '1', 't', 'y', 'yes')
                
                # Check if user and notification exist
                try:
                    user = User.objects.get(id=row['user_id'])
                    notification = Notification.objects.get(id=row['notification_id'])
                    
                    # Create user notification
                    UserNotification.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'user': user,
                            'notification': notification,
                            'is_read': is_read,
                            'read_at': read_at,
                            'is_deleted': is_deleted,
                            'deleted_at': deleted_at
                        }
                    )
                    user_notifications_created += 1
                except (User.DoesNotExist, Notification.DoesNotExist) as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping user notification {row['id']}: {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error creating user notification {row['id']}: {e}"
                    ))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {user_notifications_created} user notifications'))
    
    def import_preferences(self, file_path):
        """Import notification preferences from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            preferences_created = 0
            
            for row in reader:
                # Parse boolean fields
                is_enabled = False
                if row['is_enabled'] and row['is_enabled'].lower() != 'null':
                    is_enabled = row['is_enabled'].lower() in ('true', '1', 't', 'y', 'yes')
                
                # Check if user and category exist
                try:
                    user = User.objects.get(id=row['user_id'])
                    category = NotificationCategory.objects.get(id=row['category_id'])
                    
                    # Create preference
                    NotificationPreference.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'user': user,
                            'category': category,
                            'channel': row['channel'],
                            'is_enabled': is_enabled
                        }
                    )
                    preferences_created += 1
                except (User.DoesNotExist, NotificationCategory.DoesNotExist) as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping notification preference {row['id']}: {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error creating notification preference {row['id']}: {e}"
                    ))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {preferences_created} notification preferences'))
