from django.core.management.base import BaseCommand
from cms_app.models import SiteConfiguration


class Command(BaseCommand):
    help = 'Resets site configuration to default values'

    def handle(self, *args, **options):
        # Delete existing configuration
        SiteConfiguration.objects.all().delete()
        
        # Create default configuration
        config = SiteConfiguration.objects.create(
            site_name='CozyWish',
            site_description='Find & Book Local Spa and Massage Services',
            contact_email='info@cozywish.com',
            contact_phone='(123) 456-7890',
            contact_address='123 Main St, New York, NY 10001',
            facebook_url='https://facebook.com/cozywish',
            twitter_url='https://twitter.com/cozywish',
            instagram_url='https://instagram.com/cozywish',
            linkedin_url='https://linkedin.com/company/cozywish',
            default_meta_description='CozyWish is a USA-based marketplace for discounted spa and wellness services during off-peak hours.',
            default_meta_keywords='spa, wellness, beauty, massage, discounts, off-peak, deals',
            maintenance_mode=False,
            maintenance_message='We are currently performing maintenance. Please check back soon.'
        )
        
        self.stdout.write(self.style.SUCCESS(f"Site configuration reset to default values"))
