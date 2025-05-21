import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from venues_app.models import Venue
from review_app.models import Review, ReviewResponse, ReviewFlag

User = get_user_model()


class Command(BaseCommand):
    help = 'Import dummy data for review_app from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            default='review_app/review_app_manual_test_dummy_data',
            help='Directory containing the CSV files'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        directory = options['dir']
        clear_data = options['clear']

        # Check if directory exists
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR(f'Directory {directory} does not exist'))
            return

        # Clear existing data if requested
        if clear_data:
            self.clear_existing_data()

        self.stdout.write(self.style.SUCCESS('Starting import of review_app dummy data...'))

        # Import data in a transaction to ensure consistency
        try:
            with transaction.atomic():
                # Import reviews
                self.import_reviews(os.path.join(directory, 'reviews.csv'))

                # Import review responses
                self.import_review_responses(os.path.join(directory, 'review_responses.csv'))

                # Import review flags
                self.import_review_flags(os.path.join(directory, 'review_flags.csv'))

            self.stdout.write(self.style.SUCCESS('Successfully imported review_app dummy data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing dummy data: {e}'))

    def clear_existing_data(self):
        """Clear existing data from the database"""
        self.stdout.write('Clearing existing review data...')
        ReviewFlag.objects.all().delete()
        ReviewResponse.objects.all().delete()
        Review.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing review data cleared'))

    def import_reviews(self, csv_file):
        """Import reviews from CSV file"""
        self.stdout.write('Importing reviews...')

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    venue = Venue.objects.filter(id=row['venue_id']).first()
                    user = User.objects.filter(id=row['user_id']).first()

                    if not venue or not user:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping review: Venue ID {row['venue_id']} or User ID {row['user_id']} not found"
                        ))
                        continue

                    # Check if review already exists
                    existing_review = Review.objects.filter(venue=venue, user=user).first()
                    if existing_review:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping review: Review for Venue ID {row['venue_id']} by User ID {row['user_id']} already exists"
                        ))
                        continue

                    # Create review
                    review = Review.objects.create(
                        venue=venue,
                        user=user,
                        rating=int(row['rating']),
                        comment=row['comment'],
                        is_approved=row['is_approved'].lower() == 'true',
                        is_flagged=row['is_flagged'].lower() == 'true'
                    )

                    count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Created review for {venue.name} by {user.email}"
                    ))

                self.stdout.write(self.style.SUCCESS(f"Imported {count} reviews"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing reviews: {str(e)}"))

    def import_review_responses(self, csv_file):
        """Import review responses from CSV file"""
        self.stdout.write('Importing review responses...')

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    review = Review.objects.filter(id=row['review_id']).first()

                    if not review:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping response: Review ID {row['review_id']} not found"
                        ))
                        continue

                    # Check if response already exists
                    try:
                        existing_response = review.response
                        self.stdout.write(self.style.WARNING(
                            f"Skipping response: Response for Review ID {row['review_id']} already exists"
                        ))
                        continue
                    except ReviewResponse.DoesNotExist:
                        pass

                    # Create response
                    response = ReviewResponse.objects.create(
                        review=review,
                        response_text=row['response_text']
                    )

                    count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Created response for review ID {review.id}"
                    ))

                self.stdout.write(self.style.SUCCESS(f"Imported {count} review responses"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing review responses: {str(e)}"))

    def import_review_flags(self, csv_file):
        """Import review flags from CSV file"""
        self.stdout.write('Importing review flags...')

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    review = Review.objects.filter(id=row['review_id']).first()
                    flagged_by = User.objects.filter(id=row['flagged_by_id']).first()

                    if not review or not flagged_by:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping flag: Review ID {row['review_id']} or User ID {row['flagged_by_id']} not found"
                        ))
                        continue

                    # Check if flag already exists
                    existing_flag = ReviewFlag.objects.filter(review=review, flagged_by=flagged_by).first()
                    if existing_flag:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping flag: Flag for Review ID {row['review_id']} by User ID {row['flagged_by_id']} already exists"
                        ))
                        continue

                    # Create flag
                    flag = ReviewFlag.objects.create(
                        review=review,
                        flagged_by=flagged_by,
                        reason=row['reason'],
                        status=row['status']
                    )

                    # Update review flag status
                    review.is_flagged = True
                    review.save()

                    count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Created flag for review ID {review.id} by {flagged_by.email}"
                    ))

                self.stdout.write(self.style.SUCCESS(f"Imported {count} review flags"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing review flags: {str(e)}"))
