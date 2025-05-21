from django.core.management.base import BaseCommand
from django.utils import timezone
from booking_cart_app.models import CartItem


class Command(BaseCommand):
    help = 'Removes expired cart items'

    def handle(self, *args, **options):
        # Get all expired cart items
        expired_items = CartItem.objects.filter(expires_at__lt=timezone.now())
        count = expired_items.count()

        # Delete expired items
        expired_items.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Deleted {count} expired cart items')
        )
