from django_cron import CronJobBase, Schedule
from .utils import clean_expired_cart_items

class CleanExpiredCartItemsCronJob(CronJobBase):
    """
    Cron job to clean expired cart items
    Runs every hour
    """
    RUN_EVERY_MINS = 60  # Run every hour
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'booking_cart_app.clean_expired_cart_items'  # Unique code
    
    def do(self):
        """
        Clean expired cart items
        """
        count = clean_expired_cart_items()
        return f"Removed {count} expired cart items"
