from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from venues_app.models import Venue
from django.utils import timezone


class Review(models.Model):
    """Model for storing reviews of venues"""
    
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='review_app_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_app_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['venue', 'user']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
    
    def __str__(self):
        return f"{self.user.email} - {self.venue.name} - {self.rating} stars"
    
    def get_response(self):
        """Get the response to this review, if any"""
        try:
            return self.response
        except ReviewResponse.DoesNotExist:
            return None
    
    def flag(self, user, reason):
        """Flag this review as inappropriate"""
        if user != self.user:  # Users can't flag their own reviews
            ReviewFlag.objects.create(
                review=self,
                flagged_by=user,
                reason=reason
            )
            self.is_flagged = True
            self.save()
            return True
        return False


class ReviewResponse(models.Model):
    """Model for service provider responses to reviews"""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review Response"
        verbose_name_plural = "Review Responses"
    
    def __str__(self):
        return f"Response to {self.review}"


class ReviewFlag(models.Model):
    """Model for flagging inappropriate reviews"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Review Removed'),
        ('rejected', 'Rejected - Flag Dismissed'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flags')
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flagged_reviews')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_flags'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review Flag"
        verbose_name_plural = "Review Flags"
    
    def __str__(self):
        return f"Flag on {self.review} by {self.flagged_by.email}"
    
    def approve(self, admin_user):
        """Approve the flag and remove the review"""
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        
        # Update the review
        review = self.review
        review.is_approved = False
        review.save()
        
        return True
    
    def reject(self, admin_user):
        """Reject the flag and keep the review"""
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        
        # Update the review if it was the only pending flag
        review = self.review
        if not review.flags.filter(status='pending').exists():
            review.is_flagged = False
            review.save()
        
        return True
