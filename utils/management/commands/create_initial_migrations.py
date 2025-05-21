import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create initial migrations for all apps in the correct order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating migrations',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Define the order of apps for migrations to ensure dependencies are respected
        # Start with models that don't depend on other models, then move to dependent models
        apps_order = [
            'accounts_app',  # User model comes first
            'venues_app',    # Venues depend on users
            'review_app',    # Reviews depend on venues and users
            'booking_cart_app',  # Bookings depend on venues, services, and users
            'payments_app',  # Payments depend on bookings
            'dashboard_app',  # Dashboard depends on various models
            'discount_app',  # Discounts depend on venues and services
            'cms_app',       # CMS might depend on users
            'notifications_app',  # Notifications depend on users and possibly other models
            'admin_app',     # Admin app might depend on various models
            'utils',         # Utility models might depend on other models
        ]
        
        # Check if apps exist
        existing_apps = []
        for app in apps_order:
            app_path = os.path.join(settings.BASE_DIR, app)
            if os.path.exists(app_path) and os.path.isdir(app_path):
                existing_apps.append(app)
            else:
                self.stdout.write(self.style.WARNING(f"App '{app}' not found, skipping"))
        
        # Create migrations directory if it doesn't exist
        for app in existing_apps:
            migrations_dir = os.path.join(settings.BASE_DIR, app, 'migrations')
            if not os.path.exists(migrations_dir):
                if not dry_run:
                    os.makedirs(migrations_dir)
                    # Create __init__.py file
                    with open(os.path.join(migrations_dir, '__init__.py'), 'w') as f:
                        pass
                self.stdout.write(self.style.SUCCESS(f"Created migrations directory for '{app}'"))
        
        # Create initial migrations
        for app in existing_apps:
            self.stdout.write(f"Creating initial migration for '{app}'...")
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"[DRY RUN] Would create migration for '{app}'"))
                continue
            
            try:
                # Run makemigrations for the app
                result = subprocess.run(
                    ['python', 'manage.py', 'makemigrations', app],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.stdout.write(self.style.SUCCESS(f"Created migration for '{app}': {result.stdout}"))
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f"Error creating migration for '{app}': {e.stderr}"))
        
        # Final message
        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run completed. No migrations were actually created."))
        else:
            self.stdout.write(self.style.SUCCESS("Initial migrations created for all apps."))
            self.stdout.write("You can now run 'python manage.py migrate' to apply these migrations.")
