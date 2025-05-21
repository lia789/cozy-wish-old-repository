import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from admin_app.models import (
    AdminPreference, AdminActivity, AdminTask,
    SystemConfig, AuditLog, SecurityEvent
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for admin_app manual testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting import of admin_app dummy data...'))
        
        # Define the path to the dummy data directory
        dummy_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'admin_app_manual_test_dummy_data'
        )
        
        # Import admin preferences
        self.import_admin_preferences(os.path.join(dummy_data_dir, 'admin_preferences.csv'))
        
        # Import admin activities
        self.import_admin_activities(os.path.join(dummy_data_dir, 'admin_activities.csv'))
        
        # Import admin tasks
        self.import_admin_tasks(os.path.join(dummy_data_dir, 'admin_tasks.csv'))
        
        # Import system configs
        self.import_system_configs(os.path.join(dummy_data_dir, 'system_configs.csv'))
        
        # Import audit logs
        self.import_audit_logs(os.path.join(dummy_data_dir, 'audit_logs.csv'))
        
        # Import security events
        self.import_security_events(os.path.join(dummy_data_dir, 'security_events.csv'))
        
        self.stdout.write(self.style.SUCCESS('Successfully imported all admin_app dummy data!'))
    
    def import_admin_preferences(self, csv_file):
        """Import admin preferences from CSV file"""
        self.stdout.write('Importing admin preferences...')
        
        # Clear existing preferences
        AdminPreference.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create user
                user, created = User.objects.get_or_create(
                    email=row['user_email'],
                    defaults={
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                # Create preference
                AdminPreference.objects.create(
                    user=user,
                    theme=row['theme'],
                    sidebar_collapsed=row['sidebar_collapsed'] == 'True',
                    show_quick_actions=row['show_quick_actions'] == 'True',
                    items_per_page=int(row['items_per_page'])
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {AdminPreference.objects.count()} admin preferences'))
    
    def import_admin_activities(self, csv_file):
        """Import admin activities from CSV file"""
        self.stdout.write('Importing admin activities...')
        
        # Clear existing activities
        AdminActivity.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create user
                user, created = User.objects.get_or_create(
                    email=row['user_email'],
                    defaults={
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                # Parse timestamp
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                timestamp = timezone.make_aware(timestamp)
                
                # Create activity
                AdminActivity.objects.create(
                    user=user,
                    action_type=row['action_type'],
                    target_model=row['target_model'],
                    target_id=row['target_id'],
                    description=row['description'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    timestamp=timestamp
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {AdminActivity.objects.count()} admin activities'))
    
    def import_admin_tasks(self, csv_file):
        """Import admin tasks from CSV file"""
        self.stdout.write('Importing admin tasks...')
        
        # Clear existing tasks
        AdminTask.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create users
                created_by, created = User.objects.get_or_create(
                    email=row['created_by_email'],
                    defaults={
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                assigned_to = None
                if row['assigned_to_email']:
                    assigned_to, created = User.objects.get_or_create(
                        email=row['assigned_to_email'],
                        defaults={
                            'is_staff': True,
                            'is_active': True
                        }
                    )
                
                # Parse dates
                due_date = None
                if row['due_date']:
                    due_date = datetime.strptime(row['due_date'], '%Y-%m-%d %H:%M:%S')
                    due_date = timezone.make_aware(due_date)
                
                completed_at = None
                if row['completed_at']:
                    completed_at = datetime.strptime(row['completed_at'], '%Y-%m-%d %H:%M:%S')
                    completed_at = timezone.make_aware(completed_at)
                
                # Create task
                AdminTask.objects.create(
                    title=row['title'],
                    description=row['description'],
                    created_by=created_by,
                    assigned_to=assigned_to,
                    due_date=due_date,
                    priority=row['priority'],
                    status=row['status'],
                    completed_at=completed_at
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {AdminTask.objects.count()} admin tasks'))
    
    def import_system_configs(self, csv_file):
        """Import system configs from CSV file"""
        self.stdout.write('Importing system configs...')
        
        # Clear existing configs
        SystemConfig.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create user
                last_updated_by, created = User.objects.get_or_create(
                    email=row['last_updated_by_email'],
                    defaults={
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                # Create config
                SystemConfig.objects.create(
                    maintenance_mode=row['maintenance_mode'] == 'True',
                    maintenance_message=row['maintenance_message'],
                    registration_enabled=row['registration_enabled'] == 'True',
                    max_login_attempts=int(row['max_login_attempts']),
                    login_lockout_duration=int(row['login_lockout_duration']),
                    password_expiry_days=int(row['password_expiry_days']),
                    session_timeout_minutes=int(row['session_timeout_minutes']),
                    enable_two_factor_auth=row['enable_two_factor_auth'] == 'True',
                    last_updated_by=last_updated_by
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {SystemConfig.objects.count()} system configs'))
    
    def import_audit_logs(self, csv_file):
        """Import audit logs from CSV file"""
        self.stdout.write('Importing audit logs...')
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create user
                user, created = User.objects.get_or_create(
                    email=row['user_email'],
                    defaults={
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                # Parse timestamp
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                timestamp = timezone.make_aware(timestamp)
                
                # Create audit log
                AuditLog.objects.create(
                    user=user,
                    action=row['action'],
                    resource_type=row['resource_type'],
                    resource_id=row['resource_id'],
                    details=row['details'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    timestamp=timestamp
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {AuditLog.objects.count()} audit logs'))
    
    def import_security_events(self, csv_file):
        """Import security events from CSV file"""
        self.stdout.write('Importing security events...')
        
        # Clear existing security events
        SecurityEvent.objects.all().delete()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get or create user
                user, created = User.objects.get_or_create(
                    email=row['user_email'],
                    defaults={
                        'is_active': True
                    }
                )
                
                # Get resolved_by user if applicable
                resolved_by = None
                if row['resolved_by_email']:
                    resolved_by, created = User.objects.get_or_create(
                        email=row['resolved_by_email'],
                        defaults={
                            'is_staff': True,
                            'is_active': True
                        }
                    )
                
                # Parse resolved_at if applicable
                resolved_at = None
                if row['resolved_at']:
                    resolved_at = datetime.strptime(row['resolved_at'], '%Y-%m-%d %H:%M:%S')
                    resolved_at = timezone.make_aware(resolved_at)
                
                # Create security event
                SecurityEvent.objects.create(
                    user=user,
                    event_type=row['event_type'],
                    severity=row['severity'],
                    description=row['description'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    is_resolved=row['is_resolved'] == 'True',
                    resolved_by=resolved_by,
                    resolved_at=resolved_at,
                    resolution_notes=row['resolution_notes']
                )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {SecurityEvent.objects.count()} security events'))
