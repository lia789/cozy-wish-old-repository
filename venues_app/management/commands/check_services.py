from django.core.management.base import BaseCommand
from venues_app.models import Venue, Service

class Command(BaseCommand):
    help = 'Check services and venues in the database'

    def handle(self, *args, **options):
        self.stdout.write(f"Total services in database: {Service.objects.count()}")
        self.stdout.write(f"Total venues in database: {Venue.objects.count()}")

        self.stdout.write("\nFirst 5 services:")
        for service in Service.objects.all()[:5]:
            self.stdout.write(f"Service: {service.title}, Venue: {service.venue.name if service.venue else 'None'}")

        self.stdout.write("\nAll venues and their services:")
        for venue in Venue.objects.all():
            services = Service.objects.filter(venue=venue)
            self.stdout.write(f"Venue: {venue.name}, Services count: {services.count()}")
            if services.count() > 0:
                for service in services:
                    self.stdout.write(f"  - {service.title}")
