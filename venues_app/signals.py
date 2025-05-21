from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Venue, Review

@receiver(post_save, sender=Venue)
def venue_status_changed(sender, instance, created, **kwargs):
    """Send email notifications when venue status changes"""
    if not created and instance.owner.email:
        # Send email based on the approval status
        if instance.approval_status == 'approved':
            subject = f"Your venue '{instance.name}' has been approved!"
            message = f"""
            Congratulations! Your venue '{instance.name}' has been approved by our team.

            Your venue is now visible to all users on our platform. You can start adding services
            and managing your venue from your dashboard.

            Thank you for choosing CozyWish!
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.owner.email],
                fail_silently=True,
            )

        elif instance.approval_status == 'rejected':
            subject = f"Your venue '{instance.name}' requires changes"
            message = f"""
            We've reviewed your venue '{instance.name}' and it requires some changes before it can be approved.

            Reason for rejection: {instance.rejection_reason}

            Please update your venue information and resubmit for approval.

            Thank you for your understanding.
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.owner.email],
                fail_silently=True,
            )

@receiver(post_save, sender=Review)
def review_submitted(sender, instance, created, **kwargs):
    """Send email notifications when a new review is submitted"""
    if created and instance.venue.owner.email:
        subject = f"New review for '{instance.venue.name}'"
        message = f"""
        A new review has been submitted for your venue '{instance.venue.name}'.

        Rating: {instance.rating}/5
        Comment: {instance.comment}

        You can view all reviews from your dashboard.

        Thank you for using CozyWish!
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.venue.owner.email],
            fail_silently=True,
        )
