from django.core.management.base import BaseCommand
from django.db.models import Q
from venues_app.models import Venue, USCity


class Command(BaseCommand):
    help = 'Update existing venues with US city data'

    def handle(self, *args, **options):
        # Get all venues without us_city set
        venues = Venue.objects.filter(us_city__isnull=True)
        
        self.stdout.write(self.style.SUCCESS(f'Found {venues.count()} venues without US city data'))
        
        updated_count = 0
        not_found_count = 0
        
        for venue in venues:
            if venue.city and venue.state:
                # Try to find a matching city
                city_match = USCity.objects.filter(
                    Q(city__iexact=venue.city) & 
                    (Q(state_name__iexact=venue.state) | Q(state_id__iexact=venue.state))
                ).first()
                
                if city_match:
                    venue.us_city = city_match
                    
                    # Update coordinates if not set
                    if not venue.latitude or not venue.longitude:
                        venue.latitude = city_match.latitude
                        venue.longitude = city_match.longitude
                    
                    venue.save()
                    updated_count += 1
                    self.stdout.write(f'Updated venue: {venue.name} ({venue.city}, {venue.state})')
                else:
                    not_found_count += 1
                    self.stdout.write(self.style.WARNING(f'No matching city found for venue: {venue.name} ({venue.city}, {venue.state})'))
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} venues with US city data'))
        self.stdout.write(self.style.WARNING(f'Could not find matching cities for {not_found_count} venues'))
