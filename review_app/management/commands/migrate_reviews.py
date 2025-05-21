from django.core.management.base import BaseCommand
from django.db import transaction
from venues_app.models import Review as VenuesReview
from review_app.models import Review as ReviewAppReview


class Command(BaseCommand):
    help = 'Migrates reviews from venues_app to review_app'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting review migration...'))
        
        # Count reviews in venues_app
        venues_reviews_count = VenuesReview.objects.count()
        self.stdout.write(f'Found {venues_reviews_count} reviews in venues_app')
        
        # Count existing reviews in review_app
        existing_reviews_count = ReviewAppReview.objects.count()
        self.stdout.write(f'Found {existing_reviews_count} existing reviews in review_app')
        
        migrated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for venues_review in VenuesReview.objects.all():
                # Check if review already exists in review_app
                existing_review = ReviewAppReview.objects.filter(
                    venue=venues_review.venue,
                    user=venues_review.user
                ).first()
                
                if existing_review:
                    self.stdout.write(f'Skipping review for {venues_review.venue.name} by {venues_review.user.email} - already exists')
                    skipped_count += 1
                    continue
                
                # Create new review in review_app
                new_review = ReviewAppReview(
                    venue=venues_review.venue,
                    user=venues_review.user,
                    rating=venues_review.rating,
                    comment=venues_review.comment,
                    created_at=venues_review.created_at,
                    updated_at=venues_review.updated_at,
                    is_approved=venues_review.is_approved
                )
                new_review.save()
                
                # Update created_at and updated_at manually since they are auto fields
                ReviewAppReview.objects.filter(id=new_review.id).update(
                    created_at=venues_review.created_at,
                    updated_at=venues_review.updated_at
                )
                
                migrated_count += 1
                self.stdout.write(f'Migrated review for {venues_review.venue.name} by {venues_review.user.email}')
        
        self.stdout.write(self.style.SUCCESS(f'Migration complete! Migrated {migrated_count} reviews, skipped {skipped_count} reviews'))
