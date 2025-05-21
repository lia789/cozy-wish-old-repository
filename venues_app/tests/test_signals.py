from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.conf import settings

from venues_app.models import (
    Category, Venue, Review
)

User = get_user_model()


class VenueSignalsTest(TestCase):
    """Test the signals in the venues_app."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa"
        )
        self.venue = Venue.objects.create(
            owner=self.user,
            name="Luxury Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city.",
            approval_status="pending"
        )

    def test_venue_approval_email(self):
        """Test that an email is sent when a venue is approved."""
        # Note: Signals are temporarily disabled in venues_app/apps.py
        # This test directly calls the signal handler

        # Clear the mail outbox
        mail.outbox = []

        # Import the signal handler function directly and call it
        from venues_app.signals import venue_status_changed

        # Update the venue to approved status (but don't save to avoid double signal)
        self.venue.approval_status = "approved"

        # Call the signal handler directly
        venue_status_changed(sender=Venue, instance=self.venue, created=False)

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"Your venue '{self.venue.name}' has been approved!")
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_venue_rejection_email(self):
        """Test that an email is sent when a venue is rejected."""
        # Note: Signals are temporarily disabled in venues_app/apps.py
        # This test directly calls the signal handler

        # Clear the mail outbox
        mail.outbox = []

        # Import the signal handler function directly and call it
        from venues_app.signals import venue_status_changed

        # Update the venue to rejected status with a reason (but don't save to avoid double signal)
        self.venue.approval_status = "rejected"
        self.venue.rejection_reason = "Incomplete information provided."

        # Call the signal handler directly
        venue_status_changed(sender=Venue, instance=self.venue, created=False)

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"Your venue '{self.venue.name}' requires changes")
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn("Incomplete information provided.", mail.outbox[0].body)


class ReviewSignalsTest(TestCase):
    """Test the signals for the Review model."""

    def setUp(self):
        """Set up test data."""
        self.provider = User.objects.create_user(
            email="provider@example.com",
            password="testpass123",
            is_service_provider=True
        )
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            is_customer=True
        )
        self.category = Category.objects.create(
            name="Spa",
            description="Relaxation and wellness services",
            icon_class="fa-spa"
        )
        self.venue = Venue.objects.create(
            owner=self.provider,
            name="Luxury Spa",
            category=self.category,
            venue_type="all",
            state="New York",
            county="New York County",
            city="New York",
            street_number="123",
            street_name="Main St",
            about="A luxury spa in the heart of the city.",
            approval_status="approved"
        )

    def test_review_submission_email(self):
        """Test that an email is sent when a review is submitted."""
        # Note: Signals are temporarily disabled in venues_app/apps.py
        # This test directly calls the signal handler

        # Clear the mail outbox
        mail.outbox = []

        # Create a review without saving to the database
        review = Review(
            venue=self.venue,
            user=self.customer,
            rating=4,
            comment="Great experience! The staff was very friendly and professional."
        )

        # Import the signal handler function directly and call it
        from venues_app.signals import review_submitted
        review_submitted(sender=Review, instance=review, created=True)

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"New review for '{self.venue.name}'")
        self.assertEqual(mail.outbox[0].to, [self.provider.email])
        self.assertIn("Rating: 4/5", mail.outbox[0].body)
        self.assertIn("Great experience!", mail.outbox[0].body)
