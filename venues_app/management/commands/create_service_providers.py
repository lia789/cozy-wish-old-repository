import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts_app.models import ServiceProviderProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create service provider users for venues_app dummy data'

    def handle(self, *args, **options):
        # Service provider emails from venues.csv
        SERVICE_PROVIDER_EMAILS = [
            'provider1@example.com',
            'provider2@example.com',
            'provider3@example.com',
            'provider4@example.com',
            'provider5@example.com',
        ]
        
        created_count = 0
        existing_count = 0
        
        for email in SERVICE_PROVIDER_EMAILS:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"User already exists: {email}")
                existing_count += 1
                continue
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password='password123',
                is_service_provider=True,
            )
            
            # Update service provider profile
            profile = user.provider_profile
            profile.business_name = f"{email.split('@')[0].title()} Business"
            profile.phone_number = "+1234567890"
            profile.contact_person_name = f"{email.split('@')[0].title()} Contact"
            profile.save()
            
            self.stdout.write(self.style.SUCCESS(f"Created service provider: {email}"))
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} service providers, {existing_count} already existed."
            )
        )
