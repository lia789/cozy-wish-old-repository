import csv
import os
import decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import transaction
from decimal import Decimal
from venues_app.models import (
    Category, Tag, Venue, VenueImage, OpeningHours,
    FAQ, Service, Review, TeamMember, USCity
)
from accounts_app.models import ServiceProviderProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for venues_app manual testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            default='venues_app/venues_app_manual_test_dummy_data',
            help='Directory containing the CSV files'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        base_dir = options['dir']
        clear_data = options['clear']

        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {base_dir}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting import from {base_dir}'))

        # Use transaction to ensure data consistency
        with transaction.atomic():
            # Clear existing data if requested
            if clear_data:
                self.clear_existing_data()
                self.stdout.write(self.style.SUCCESS('Cleared existing data'))

            # Create service provider users needed for venues
            self.create_service_providers(os.path.join(base_dir, 'venues.csv'))

            # Create customer users needed for reviews
            self.create_customer_users(os.path.join(base_dir, 'reviews.csv'))

            # Import data in the correct order to maintain relationships
            self.import_categories(os.path.join(base_dir, 'categories.csv'))
            self.import_tags(os.path.join(base_dir, 'tags.csv'))
            self.import_us_cities(os.path.join(base_dir, 'us_cities.csv'))
            self.import_venues(os.path.join(base_dir, 'venues.csv'))
            self.import_services(os.path.join(base_dir, 'services.csv'))
            self.import_opening_hours(os.path.join(base_dir, 'opening_hours.csv'))
            self.import_team_members(os.path.join(base_dir, 'team_members.csv'))
            self.import_faqs(os.path.join(base_dir, 'faqs.csv'))
            self.import_reviews(os.path.join(base_dir, 'reviews.csv'))

        self.stdout.write(self.style.SUCCESS('Successfully imported venues dummy data'))

    def create_service_providers(self, venues_file_path):
        """Create service provider users needed for venues"""
        if not os.path.exists(venues_file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {venues_file_path}'))
            return

        # Get unique service provider emails from venues.csv
        service_provider_emails = set()
        with open(venues_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                service_provider_emails.add(row['owner_email'])

        created_count = 0
        existing_count = 0

        for email in service_provider_emails:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"User already exists: {email}")
                existing_count += 1
                continue

            # Create user
            user = User.objects.create_user(
                email=email,
                password='password123',
                is_service_provider=True,
            )

            # Update service provider profile
            profile = user.provider_profile
            profile.business_name = f"{email.split('@')[0].title()} Business"
            profile.phone_number = "+1234567890"
            profile.contact_person_name = f"{email.split('@')[0].title()} Contact"
            profile.save()

            self.stdout.write(self.style.SUCCESS(f"Created service provider: {email}"))
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} service providers, {existing_count} already existed."
            )
        )

    def create_customer_users(self, reviews_file_path):
        """Create customer users needed for reviews"""
        if not os.path.exists(reviews_file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {reviews_file_path}'))
            return

        # Get unique customer emails from reviews.csv
        customer_emails = set()
        with open(reviews_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_emails.add(row['user_email'])

        created_count = 0
        existing_count = 0

        for email in customer_emails:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"User already exists: {email}")
                existing_count += 1
                continue

            # Create user
            user = User.objects.create_user(
                email=email,
                password='password123',
                is_customer=True,
            )

            # Update customer profile
            profile = user.customer_profile
            first_name = email.split('@')[0].split('.')[0].title()
            last_name = email.split('@')[0].split('.')[1].title() if '.' in email.split('@')[0] else 'Customer'
            profile.first_name = first_name
            profile.last_name = last_name
            profile.phone_number = "+1234567890"
            profile.save()

            self.stdout.write(self.style.SUCCESS(f"Created customer: {email}"))
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} customers, {existing_count} already existed."
            )
        )

    def clear_existing_data(self):
        """Clear existing data from the database"""
        Review.objects.all().delete()
        FAQ.objects.all().delete()
        TeamMember.objects.all().delete()
        OpeningHours.objects.all().delete()
        Service.objects.all().delete()
        VenueImage.objects.all().delete()
        Venue.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        USCity.objects.all().delete()

    def import_categories(self, file_path):
        """Import categories from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Check if category already exists
                    category, created = Category.objects.get_or_create(
                        name=row['name'],
                        defaults={
                            'slug': row['slug'] or slugify(row['name']),
                            'description': row['description'],
                            'icon_class': row['icon_class'],
                            'is_active': row['is_active'] == 'True'
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created category: {category.name}')
                    else:
                        self.stdout.write(f'Category already exists: {category.name}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing category: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} categories'))

    def import_tags(self, file_path):
        """Import tags from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Check if tag already exists
                    tag, created = Tag.objects.get_or_create(
                        name=row['name'],
                        defaults={
                            'slug': row['slug'] or slugify(row['name'])
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created tag: {tag.name}')
                    else:
                        self.stdout.write(f'Tag already exists: {tag.name}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing tag: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} tags'))

    def import_us_cities(self, file_path):
        """Import US cities from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Check if city already exists
                    city, created = USCity.objects.get_or_create(
                        city_id=row['id'],
                        defaults={
                            'city': row['city'],
                            'state_id': row['state_id'],
                            'state_name': row['state_name'],
                            'county_name': row['county_name'],
                            'latitude': Decimal(row['lat']),
                            'longitude': Decimal(row['lng']),
                            'zip_codes': row['zips']
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created US city: {city.city}, {city.state_id}')
                    else:
                        self.stdout.write(f'US city already exists: {city.city}, {city.state_id}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing US city: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} US cities'))

    def import_venues(self, file_path):
        """Import venues from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the owner user
                    try:
                        owner = User.objects.get(email=row['owner_email'])
                    except User.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'User not found: {row["owner_email"]}. Skipping venue.'))
                        continue

                    # Get the category
                    try:
                        category = Category.objects.get(name=row['category_name'])
                    except Category.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Category not found: {row["category_name"]}. Skipping venue.'))
                        continue

                    # Get the US city
                    us_city = USCity.objects.filter(
                        city__iexact=row['city'],
                        state_name__iexact=row['state']
                    ).first()

                    # Create the venue
                    venue, created = Venue.objects.get_or_create(
                        name=row['name'],
                        owner=owner,
                        defaults={
                            'slug': slugify(row['name']),
                            'category': category,
                            'venue_type': row['venue_type'],
                            'state': row['state'],
                            'county': row['county'],
                            'city': row['city'],
                            'street_number': row['street_number'],
                            'street_name': row['street_name'],
                            'about': row['about'],
                            'approval_status': row['approval_status'],
                            'is_active': row['is_active'] == 'True',
                            'us_city': us_city
                        }
                    )

                    if created:
                        # Add tags
                        if row['tag_names']:
                            tag_names = row['tag_names'].split(',')
                            for tag_name in tag_names:
                                try:
                                    tag = Tag.objects.get(name=tag_name.strip())
                                    venue.tags.add(tag)
                                except Tag.DoesNotExist:
                                    self.stdout.write(self.style.WARNING(f'Tag not found: {tag_name}'))

                        counter += 1
                        self.stdout.write(f'Created venue: {venue.name}')
                    else:
                        self.stdout.write(f'Venue already exists: {venue.name}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing venue: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} venues'))

    def import_services(self, file_path):
        """Import services from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the venue
                    try:
                        venue = Venue.objects.get(name=row['venue_name'])
                    except Venue.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Venue not found: {row["venue_name"]}. Skipping service.'))
                        continue

                    # Create the service
                    try:
                        price = Decimal(row['price'].strip())
                    except (decimal.InvalidOperation, decimal.ConversionSyntax) as e:
                        self.stdout.write(self.style.ERROR(f'Invalid price format for {row["title"]}: {row["price"]}'))
                        continue

                    try:
                        discounted_price = Decimal(row['discounted_price'].strip()) if row['discounted_price'] else None
                    except (decimal.InvalidOperation, decimal.ConversionSyntax) as e:
                        self.stdout.write(self.style.ERROR(f'Invalid discounted price format for {row["title"]}: {row["discounted_price"]}'))
                        continue

                    service, created = Service.objects.get_or_create(
                        venue=venue,
                        title=row['title'],
                        defaults={
                            'slug': slugify(row['title']),
                            'short_description': row['short_description'],
                            'price': price,
                            'discounted_price': discounted_price,
                            'duration': int(row['duration']),
                            'is_active': row['is_active'] == 'True'
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created service: {service.title} for {venue.name}')
                    else:
                        self.stdout.write(f'Service already exists: {service.title} for {venue.name}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing service: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} services'))

    def import_opening_hours(self, file_path):
        """Import opening hours from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the venue
                    try:
                        venue = Venue.objects.get(name=row['venue_name'])
                    except Venue.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Venue not found: {row["venue_name"]}. Skipping opening hours.'))
                        continue

                    # Create the opening hours
                    hours, created = OpeningHours.objects.get_or_create(
                        venue=venue,
                        day=int(row['day']),
                        defaults={
                            'open_time': row['open_time'],
                            'close_time': row['close_time'],
                            'is_closed': row['is_closed'] == 'True'
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created opening hours for {venue.name} on day {hours.get_day_display()}')
                    else:
                        self.stdout.write(f'Opening hours already exist for {venue.name} on day {hours.get_day_display()}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing opening hours: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} opening hours'))

    def import_team_members(self, file_path):
        """Import team members from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the venue
                    try:
                        venue = Venue.objects.get(name=row['venue_name'])
                    except Venue.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Venue not found: {row["venue_name"]}. Skipping team member.'))
                        continue

                    # Create the team member
                    member, created = TeamMember.objects.get_or_create(
                        venue=venue,
                        name=row['name'],
                        defaults={
                            'title': row['title'],
                            'bio': row['bio'],
                            'is_active': row['is_active'] == 'True'
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created team member: {member.name} for {venue.name}')
                    else:
                        self.stdout.write(f'Team member already exists: {member.name} for {venue.name}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing team member: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} team members'))

    def import_faqs(self, file_path):
        """Import FAQs from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the venue
                    try:
                        venue = Venue.objects.get(name=row['venue_name'])
                    except Venue.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Venue not found: {row["venue_name"]}. Skipping FAQ.'))
                        continue

                    # Create the FAQ
                    faq, created = FAQ.objects.get_or_create(
                        venue=venue,
                        question=row['question'],
                        defaults={
                            'answer': row['answer'],
                            'order': int(row['order'])
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created FAQ for {venue.name}: {faq.question[:30]}...')
                    else:
                        self.stdout.write(f'FAQ already exists for {venue.name}: {faq.question[:30]}...')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing FAQ: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} FAQs'))

    def import_reviews(self, file_path):
        """Import reviews from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            counter = 0

            for row in reader:
                try:
                    # Get the venue
                    try:
                        venue = Venue.objects.get(name=row['venue_name'])
                    except Venue.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Venue not found: {row["venue_name"]}. Skipping review.'))
                        continue

                    # Get the user
                    try:
                        user = User.objects.get(email=row['user_email'])
                    except User.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'User not found: {row["user_email"]}. Skipping review.'))
                        continue

                    # Create the review
                    review, created = Review.objects.get_or_create(
                        venue=venue,
                        user=user,
                        defaults={
                            'rating': int(row['rating']),
                            'comment': row['comment'],
                            'is_approved': row['is_approved'] == 'True'
                        }
                    )

                    if created:
                        counter += 1
                        self.stdout.write(f'Created review for {venue.name} by {user.email}: {review.rating} stars')
                    else:
                        self.stdout.write(f'Review already exists for {venue.name} by {user.email}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing review: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Imported {counter} reviews'))
