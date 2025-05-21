import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from venues_app.models import Category, Tag, Venue, Service

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test venues and related data'

    def add_arguments(self, parser):
        parser.add_argument('--venues', type=int, default=3, help='Number of venues to create')
        parser.add_argument('--services', type=int, default=2, help='Number of services per venue')
        parser.add_argument('--approved', action='store_true', help='Create approved venues')

    def handle(self, *args, **options):
        num_venues = options['venues']
        num_services = options['services']
        approved = options['approved']

        # Get admin user
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting admin user: {e}'))
            return

        # Get categories and tags
        try:
            categories = list(Category.objects.all())
            tags = list(Tag.objects.all())

            if not categories:
                self.stdout.write(self.style.ERROR('No categories found. Please run migrations first.'))
                return

            if not tags:
                self.stdout.write(self.style.ERROR('No tags found. Please run migrations first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting categories and tags: {e}'))
            return

        # Create venues
        venues_created = 0
        try:
            for i in range(num_venues):
                category = random.choice(categories)
                venue_name = f"{category.name} {random.choice(['Paradise', 'Haven', 'Studio', 'Center', 'Place'])}"

                # Create venue
                venue = Venue.objects.create(
                    owner=admin_user,
                    name=venue_name,
                    slug=slugify(venue_name),
                    category=category,
                    venue_type=random.choice(['all', 'male', 'female']),
                    state="California",
                    county="Orange County",
                    city="Los Angeles",
                    street_number="123",
                    street_name="Main Street",
                    about=f"Welcome to {venue_name}! We offer the best {category.name.lower()} services in town.",
                    approval_status='approved' if approved else 'pending',
                    is_active=True
                )

                # Add tags (up to 3)
                selected_tags = random.sample(tags, min(3, len(tags)))
                venue.tags.add(*selected_tags)

                # Create services
                for j in range(num_services):
                    service_name = f"{random.choice(['Premium', 'Deluxe', 'Standard'])} {category.name} Service"
                    price = random.randint(50, 200)

                    Service.objects.create(
                        venue=venue,
                        title=service_name,
                        slug=slugify(service_name),
                        short_description=f"Enjoy our {service_name.lower()} designed to provide the ultimate relaxation experience.",
                        price=price,
                        duration=60,
                        is_active=True
                    )

                venues_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created venue: {venue.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating venues: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully created {venues_created} venues with {num_services} services each.'))
