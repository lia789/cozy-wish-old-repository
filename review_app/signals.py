from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review, ReviewFlag


@receiver(post_save, sender=Review)
def update_venue_rating(sender, instance, **kwargs):
    """Update venue average rating when a review is saved"""
    venue = instance.venue
    # Only count approved reviews
    avg_rating = Review.objects.filter(venue=venue, is_approved=True).aggregate(Avg('rating'))['rating__avg']
    
    # Update venue rating if it has a rating field
    if hasattr(venue, 'rating'):
        venue.rating = avg_rating or 0
        venue.save(update_fields=['rating'])


@receiver(post_delete, sender=Review)
def update_venue_rating_on_delete(sender, instance, **kwargs):
    """Update venue average rating when a review is deleted"""
    venue = instance.venue
    # Only count approved reviews
    avg_rating = Review.objects.filter(venue=venue, is_approved=True).aggregate(Avg('rating'))['rating__avg']
    
    # Update venue rating if it has a rating field
    if hasattr(venue, 'rating'):
        venue.rating = avg_rating or 0
        venue.save(update_fields=['rating'])


@receiver(post_save, sender=ReviewFlag)
def update_review_flag_status(sender, instance, created, **kwargs):
    """Update review flag status when a flag is saved"""
    if not created and instance.status in ['approved', 'rejected']:
        # If flag was approved, update the review
        if instance.status == 'approved':
            review = instance.review
            review.is_approved = False
            review.save(update_fields=['is_approved'])
        
        # If flag was rejected and there are no more pending flags, update the review
        elif instance.status == 'rejected':
            review = instance.review
            if not review.flags.filter(status='pending').exists():
                review.is_flagged = False
                review.save(update_fields=['is_flagged'])
