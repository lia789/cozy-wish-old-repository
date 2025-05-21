# Review App

The Review App provides a comprehensive review system for the CozyWish platform, allowing customers to rate and review venues, service providers to respond to reviews, and administrators to manage the review system.

## Features

### Customer Features
- Submit reviews for venues after completing a booking
- Rate venues on a scale of 1-5 stars
- Edit previously submitted reviews
- View personal review history
- Flag inappropriate reviews from other users

### Service Provider Features
- View all reviews for their venues
- Filter reviews by venue, rating, and status
- Respond to customer reviews
- Edit responses to reviews
- View review summary statistics and insights

### Admin Features
- View and manage all reviews in the system
- Edit or remove reviews that violate terms
- Investigate flagged reviews and decide outcomes
- View detailed review statistics
- Highlight "New on CozyWish" for venues with few reviews

## URLs

### Customer URLs
- `/reviews/submit/<int:venue_id>/` - Submit a new review for a venue
- `/reviews/edit/<int:review_id>/` - Edit an existing review
- `/reviews/flag/<int:review_id>/` - Flag an inappropriate review
- `/reviews/history/` - View personal review history

### Service Provider URLs
- `/reviews/provider/reviews/` - View all reviews for provider's venues
- `/reviews/provider/respond/<int:review_id>/` - Respond to a review
- `/reviews/provider/summary/` - View review summary statistics

### Admin URLs
- `/reviews/admin/reviews/` - View all reviews
- `/reviews/admin/reviews/<int:review_id>/` - View details of a review
- `/reviews/admin/reviews/<int:review_id>/edit/` - Edit a review
- `/reviews/admin/reviews/<int:review_id>/delete/` - Delete a review
- `/reviews/admin/flagged/` - View and manage flagged reviews
- `/reviews/admin/flags/<int:flag_id>/approve/` - Approve a flag
- `/reviews/admin/flags/<int:flag_id>/reject/` - Reject a flag

### Public URLs
- `/reviews/venue/<int:venue_id>/` - View all reviews for a venue

## Models

### Review
Stores reviews of venues.
- `venue`: Related to Venue model
- `user`: Related to User model
- `rating`: Integer from 1 to 5
- `comment`: Text content of the review
- `created_at`, `updated_at`: Timestamps
- `is_approved`: Whether the review is approved and visible
- `is_flagged`: Whether the review has been flagged

### ReviewResponse
Stores service provider responses to reviews.
- `review`: Related to Review model
- `response_text`: Text content of the response
- `created_at`, `updated_at`: Timestamps

### ReviewFlag
Stores flags for inappropriate reviews.
- `review`: Related to Review model
- `flagged_by`: User who flagged the review
- `reason`: Reason for flagging
- `created_at`: Timestamp
- `status`: Pending, Approved, or Rejected
- `reviewed_at`, `reviewed_by`: When and by whom the flag was reviewed

## Business Rules

1. **Review Eligibility**:
   - Customers can only review venues where they have completed a booking
   - Customers can only submit one review per venue (but can edit it)

2. **Review Visibility**:
   - Only approved reviews are visible to the public
   - Flagged reviews remain visible until admin action

3. **Review Flagging**:
   - Any user (except the review author) can flag a review
   - Flagged reviews are reviewed by admins
   - Admins can approve (remove review) or reject (keep review) flags

4. **Review Responses**:
   - Only the venue owner can respond to reviews
   - Each review can have only one response
   - Responses can be edited by the venue owner

## Templates

### Customer Templates
- `submit_review.html`: Form for submitting a new review
- `edit_review.html`: Form for editing an existing review
- `flag_review.html`: Form for flagging an inappropriate review
- `customer_review_history.html`: List of reviews submitted by the customer

### Service Provider Templates
- `provider/venue_reviews.html`: List of reviews for provider's venues
- `provider/respond_to_review.html`: Form for responding to a review
- `provider/review_summary.html`: Summary statistics for reviews

### Admin Templates
- `admin/review_list.html`: List of all reviews
- `admin/review_detail.html`: Detailed view of a review
- `admin/review_edit.html`: Form for editing a review
- `admin/review_delete.html`: Confirmation for deleting a review
- `admin/flagged_reviews.html`: List of flagged reviews
- `admin/approve_flag.html`: Confirmation for approving a flag
- `admin/reject_flag.html`: Confirmation for rejecting a flag

### Public Templates
- `venue_reviews.html`: List of reviews for a venue

## Forms

- `ReviewForm`: Form for submitting and editing reviews
- `StarRatingForm`: Form with star rating widget
- `ReviewResponseForm`: Form for responding to reviews
- `ReviewFlagForm`: Form for flagging inappropriate reviews
- `AdminReviewForm`: Form for admin to edit reviews

## Utility Functions

### Rating Calculation
The app automatically recalculates venue ratings when:
- A new review is added
- An existing review is edited
- A review is deleted
- A review's approval status changes

## Management Commands

### migrate_reviews
Migrates reviews from venues_app to review_app.

```bash
python manage.py migrate_reviews
```

### import_review_dummy_data
Imports dummy data for manual testing from CSV files in the `review_app_manual_test_dummy_data` directory.

```bash
python manage.py import_review_dummy_data
```

Options:
- `--dir`: Directory containing the CSV files (default: review_app/review_app_manual_test_dummy_data)
- `--clear`: Clear existing data before importing

Or use the Makefile target:

```bash
make import-review-data
```

## Test Data

Dummy data for manual testing is available in the `review_app_manual_test_dummy_data` directory. This includes:

- Reviews for various venues with different ratings (reviews.csv)
- Responses to reviews from service providers (review_responses.csv)
- Flags for inappropriate reviews (review_flags.csv)

This data can be used to test all aspects of the review system, including:
- Displaying reviews on venue pages
- Service provider responses to reviews
- Admin moderation of flagged reviews
- Review statistics and summaries

## Integration with Other Apps

### venues_app
- Reviews are displayed on venue detail pages
- Venue model has methods to get average rating and review count
- Venues are sorted by rating in search results

### dashboard_app
- Customer dashboard shows review history
- Service provider dashboard shows review statistics
- Admin dashboard shows review metrics

## Dependencies

- Django's built-in authentication system
- Bootstrap 5 for UI components
- Font Awesome for icons
