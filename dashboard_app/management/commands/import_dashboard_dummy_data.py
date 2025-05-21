import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from dashboard_app.models import DashboardPreference, DashboardWidget, UserWidget

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for dashboard_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            default='dashboard_app/dashboard_app_manual_test_dummy_data',
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
                self.import_dashboard_widgets(os.path.join(directory, 'dashboard_widgets.csv'))
                self.import_dashboard_preferences(os.path.join(directory, 'dashboard_preferences.csv'))
                self.import_user_widgets(os.path.join(directory, 'user_widgets.csv'))
            
            self.stdout.write(self.style.SUCCESS('Successfully imported dummy data for dashboard_app'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))
    
    def clear_existing_data(self):
        """Clear existing data from the database"""
        self.stdout.write('Clearing existing dashboard data...')
        UserWidget.objects.all().delete()
        DashboardPreference.objects.all().delete()
        DashboardWidget.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing dashboard data cleared'))
    
    def import_dashboard_widgets(self, file_path):
        """Import dashboard widgets from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing dashboard widgets from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                description = row['description']
                widget_type = row['widget_type']
                template_name = row['template_name']
                icon_class = row['icon_class']
                user_type = row['user_type']
                is_active = row['is_active'] == 'True'
                
                # Create or update widget
                try:
                    widget, created = DashboardWidget.objects.update_or_create(
                        name=name,
                        defaults={
                            'description': description,
                            'widget_type': widget_type,
                            'template_name': template_name,
                            'icon_class': icon_class,
                            'user_type': user_type,
                            'is_active': is_active
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(f'Created widget: {widget.name}')
                    else:
                        self.stdout.write(f'Updated widget: {widget.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating widget {name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} dashboard widgets'))
    
    def import_dashboard_preferences(self, file_path):
        """Import dashboard preferences from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing dashboard preferences from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_email = row['user_email']
                theme = row['theme']
                compact_view = row['compact_view'] == 'True'
                
                # Find the user
                try:
                    user = User.objects.get(email=user_email)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User {user_email} not found, skipping'))
                    continue
                
                # Create or update preference
                try:
                    preference, created = DashboardPreference.objects.update_or_create(
                        user=user,
                        defaults={
                            'theme': theme,
                            'compact_view': compact_view
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(f'Created preference for user: {user.email}')
                    else:
                        self.stdout.write(f'Updated preference for user: {user.email}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating preference for {user_email}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} dashboard preferences'))
    
    def import_user_widgets(self, file_path):
        """Import user widgets from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping'))
            return
        
        self.stdout.write(f'Importing user widgets from {file_path}...')
        count = 0
        
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_email = row['user_email']
                widget_name = row['widget_name']
                position = int(row['position'])
                is_visible = row['is_visible'] == 'True'
                
                # Find the user
                try:
                    user = User.objects.get(email=user_email)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User {user_email} not found, skipping'))
                    continue
                
                # Find the widget
                try:
                    widget = DashboardWidget.objects.get(name=widget_name)
                except DashboardWidget.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Widget {widget_name} not found, skipping'))
                    continue
                
                # Create or update user widget
                try:
                    user_widget, created = UserWidget.objects.update_or_create(
                        user=user,
                        widget=widget,
                        defaults={
                            'position': position,
                            'is_visible': is_visible
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(f'Created user widget: {user.email} - {widget.name}')
                    else:
                        self.stdout.write(f'Updated user widget: {user.email} - {widget.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating user widget for {user_email} - {widget_name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} user widgets'))
