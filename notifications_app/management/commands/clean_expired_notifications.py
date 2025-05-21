from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications_app.models import Notification


class Command(BaseCommand):
    help = 'Deactivates expired notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deactivated without actually deactivating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all active notifications that have expired
        now = timezone.now()
        expired_notifications = Notification.objects.filter(
            is_active=True,
            expires_at__lt=now
        ).exclude(expires_at=None)
        
        count = expired_notifications.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would deactivate {count} expired notifications')
            )
            
            for notification in expired_notifications:
                self.stdout.write(f'- {notification.title} (expired: {notification.expires_at})')
            
            self.stdout.write(self.style.WARNING('Dry run - no changes made'))
        else:
            # Deactivate expired notifications
            expired_notifications.update(is_active=False)
            
            self.stdout.write(
                self.style.SUCCESS(f'Deactivated {count} expired notifications')
            )
