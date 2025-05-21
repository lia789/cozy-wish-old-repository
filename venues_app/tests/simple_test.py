from django.test import TestCase
from django.apps import apps


class SimpleTestCase(TestCase):
    """Simple test case to verify that the test setup works correctly."""

    def test_app_installed(self):
        """Test that the venues_app is installed."""
        self.assertTrue(apps.is_installed('venues_app'))

    def test_models_exist(self):
        """Test that the models exist."""
        from venues_app.models import (
            Category, Tag, Venue, VenueImage, OpeningHours,
            FAQ, Service, Review, TeamMember, USCity
        )
        self.assertTrue(Category)
        self.assertTrue(Tag)
        self.assertTrue(Venue)
        self.assertTrue(VenueImage)
        self.assertTrue(OpeningHours)
        self.assertTrue(FAQ)
        self.assertTrue(Service)
        self.assertTrue(Review)
        self.assertTrue(TeamMember)
        self.assertTrue(USCity)
