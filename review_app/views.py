from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count, Q
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse

from venues_app.models import Venue
from booking_cart_app.models import Booking
from .models import Review, ReviewResponse, ReviewFlag
from .forms import ReviewForm, StarRatingForm, ReviewResponseForm, ReviewFlagForm, AdminReviewForm


# Helper functions
def is_service_provider(user):
    """Check if user is a service provider"""
    return user.is_authenticated and user.is_service_provider


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_staff


def has_completed_booking(user, venue):
    """Check if user has a completed booking for the venue"""
    # Check if the Booking model has a 'status' field
    if hasattr(Booking, 'status'):
        return Booking.objects.filter(
            user=user,
            venue=venue,
            status='completed'
        ).exists()
    else:
        # Fallback if the Booking model doesn't have a status field
        # For now, we'll allow any customer to review any venue
        return user.is_authenticated and hasattr(user, 'is_customer') and user.is_customer


# Customer views
@login_required
def submit_review_view(request, venue_id):
    """Submit a new review for a venue"""
    venue = get_object_or_404(Venue, id=venue_id)

    # Check if user has a completed booking for this venue
    if not has_completed_booking(request.user, venue):
        messages.error(request, "You can only review venues where you've completed a booking.")
        return redirect('venues_app:venue_detail', venue_id=venue_id)

    # Check if user already has a review for this venue
    existing_review = Review.objects.filter(user=request.user, venue=venue).first()
    if existing_review:
        messages.info(request, "You've already reviewed this venue. You can edit your review.")
        return redirect('review_app:edit_review', review_id=existing_review.id)

    if request.method == 'POST':
        form = StarRatingForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('venues_app:venue_detail', venue_id=venue_id)
    else:
        form = StarRatingForm()

    return render(request, 'review_app/submit_review.html', {
        'form': form,
        'venue': venue,
    })


@login_required
def edit_review_view(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = StarRatingForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated successfully!")
            return redirect('venues_app:venue_detail', venue_id=review.venue.id)
    else:
        form = StarRatingForm(instance=review)

    return render(request, 'review_app/edit_review.html', {
        'form': form,
        'review': review,
        'venue': review.venue,
    })


@login_required
def flag_review_view(request, review_id):
    """Flag a review as inappropriate"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)

    # Users can't flag their own reviews
    if review.user == request.user:
        messages.error(request, "You cannot flag your own review.")
        return redirect('venues_app:venue_detail', venue_id=review.venue.id)

    # Check if user has already flagged this review
    if ReviewFlag.objects.filter(review=review, flagged_by=request.user).exists():
        messages.info(request, "You have already flagged this review.")
        return redirect('venues_app:venue_detail', venue_id=review.venue.id)

    if request.method == 'POST':
        form = ReviewFlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.review = review
            flag.flagged_by = request.user
            flag.save()

            # Update review flag status
            review.is_flagged = True
            review.save()

            messages.success(request, "Thank you for reporting this review. Our team will review it shortly.")
            return redirect('venues_app:venue_detail', venue_id=review.venue.id)
    else:
        form = ReviewFlagForm()

    return render(request, 'review_app/flag_review.html', {
        'form': form,
        'review': review,
    })


@login_required
def customer_review_history_view(request):
    """View all reviews submitted by the customer"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')

    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'review_app/customer_review_history.html', {
        'reviews': reviews,
    })


# Service Provider views
@login_required
@user_passes_test(is_service_provider)
def provider_venue_reviews_view(request):
    """View all reviews for a provider's venues"""
    # Get all venues owned by the provider
    venues = Venue.objects.filter(owner=request.user)

    # Get reviews for these venues
    reviews = Review.objects.filter(venue__in=venues).order_by('-created_at')

    # Filter by venue if specified
    venue_id = request.GET.get('venue')
    if venue_id:
        reviews = reviews.filter(venue_id=venue_id)

    # Filter by rating if specified
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)

    # Filter by status if specified
    status = request.GET.get('status')
    if status == 'flagged':
        reviews = reviews.filter(is_flagged=True)
    elif status == 'unanswered':
        reviews = reviews.exclude(response__isnull=False)

    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')

    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'review_app/provider/venue_reviews.html', {
        'reviews': reviews,
        'venues': venues,
        'selected_venue': venue_id,
        'selected_rating': rating,
        'selected_status': status,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_respond_to_review_view(request, review_id):
    """Respond to a review"""
    # Get the review and check if it belongs to one of the provider's venues
    review = get_object_or_404(Review, id=review_id, venue__owner=request.user, is_approved=True)

    # Check if there's already a response
    try:
        response = review.response
        is_edit = True
    except ReviewResponse.DoesNotExist:
        response = None
        is_edit = False

    if request.method == 'POST':
        form = ReviewResponseForm(request.POST, instance=response)
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.save()

            action = "updated" if is_edit else "added"
            messages.success(request, f"Your response has been {action} successfully!")
            return redirect('review_app:provider_venue_reviews')
    else:
        form = ReviewResponseForm(instance=response)

    return render(request, 'review_app/provider/respond_to_review.html', {
        'form': form,
        'review': review,
        'is_edit': is_edit,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_review_summary_view(request):
    """View summary statistics of reviews"""
    # Get all venues owned by the provider
    venues = Venue.objects.filter(owner=request.user)

    # Get reviews for these venues
    reviews = Review.objects.filter(venue__in=venues, is_approved=True)

    # Calculate summary statistics
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_distribution = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

    # Calculate statistics per venue
    venue_stats = []
    for venue in venues:
        venue_reviews = reviews.filter(venue=venue)
        venue_stats.append({
            'venue': venue,
            'total_reviews': venue_reviews.count(),
            'average_rating': venue_reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        })

    return render(request, 'review_app/provider/review_summary.html', {
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'rating_distribution': rating_distribution,
        'venue_stats': venue_stats,
    })


# Admin views
@login_required
@user_passes_test(is_admin)
def admin_review_list_view(request):
    """View all reviews"""
    reviews = Review.objects.all().order_by('-created_at')

    # Filter by venue if specified
    venue_id = request.GET.get('venue')
    if venue_id:
        reviews = reviews.filter(venue_id=venue_id)

    # Filter by rating if specified
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)

    # Filter by status if specified
    status = request.GET.get('status')
    if status == 'flagged':
        reviews = reviews.filter(is_flagged=True)
    elif status == 'unapproved':
        reviews = reviews.filter(is_approved=False)

    paginator = Paginator(reviews, 20)
    page = request.GET.get('page')

    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'review_app/admin/review_list.html', {
        'reviews': reviews,
        'selected_venue': venue_id,
        'selected_rating': rating,
        'selected_status': status,
    })


@login_required
@user_passes_test(is_admin)
def admin_review_detail_view(request, review_id):
    """View details of a review"""
    review = get_object_or_404(Review, id=review_id)
    flags = review.flags.all().order_by('-created_at')

    return render(request, 'review_app/admin/review_detail.html', {
        'review': review,
        'flags': flags,
    })


@login_required
@user_passes_test(is_admin)
def admin_review_edit_view(request, review_id):
    """Edit a review"""
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        form = AdminReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully!")
            return redirect('review_app:admin_review_detail', review_id=review.id)
    else:
        form = AdminReviewForm(instance=review)

    return render(request, 'review_app/admin/review_edit.html', {
        'form': form,
        'review': review,
    })


@login_required
@user_passes_test(is_admin)
def admin_review_delete_view(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect('review_app:admin_review_list')

    return render(request, 'review_app/admin/review_delete.html', {
        'review': review,
    })


@login_required
@user_passes_test(is_admin)
def admin_flagged_reviews_view(request):
    """View and manage flagged reviews"""
    flags = ReviewFlag.objects.filter(status='pending').order_by('-created_at')

    paginator = Paginator(flags, 20)
    page = request.GET.get('page')

    try:
        flags = paginator.page(page)
    except PageNotAnInteger:
        flags = paginator.page(1)
    except EmptyPage:
        flags = paginator.page(paginator.num_pages)

    return render(request, 'review_app/admin/flagged_reviews.html', {
        'flags': flags,
    })


@login_required
@user_passes_test(is_admin)
def admin_approve_flag_view(request, flag_id):
    """Approve a flag and remove the review"""
    flag = get_object_or_404(ReviewFlag, id=flag_id, status='pending')

    if request.method == 'POST':
        flag.approve(request.user)
        messages.success(request, "Flag approved and review removed.")
        return redirect('review_app:admin_flagged_reviews')

    return render(request, 'review_app/admin/approve_flag.html', {
        'flag': flag,
    })


@login_required
@user_passes_test(is_admin)
def admin_reject_flag_view(request, flag_id):
    """Reject a flag and keep the review"""
    flag = get_object_or_404(ReviewFlag, id=flag_id, status='pending')

    if request.method == 'POST':
        flag.reject(request.user)
        messages.success(request, "Flag rejected and review kept.")
        return redirect('review_app:admin_flagged_reviews')

    return render(request, 'review_app/admin/reject_flag.html', {
        'flag': flag,
    })


# Public views
def venue_reviews_view(request, venue_id):
    """View all reviews for a venue"""
    venue = get_object_or_404(Venue, id=venue_id)
    reviews = Review.objects.filter(venue=venue, is_approved=True).order_by('-created_at')

    # Calculate summary statistics
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_distribution = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

    # Prepare rating distribution for display
    rating_counts = {r['rating']: r['count'] for r in rating_distribution}
    rating_percentages = {}
    for i in range(1, 6):
        count = rating_counts.get(i, 0)
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_percentages[i] = percentage

    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')

    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    # Check if user can review this venue
    can_review = False
    has_reviewed = False
    if request.user.is_authenticated:
        can_review = has_completed_booking(request.user, venue)
        has_reviewed = Review.objects.filter(user=request.user, venue=venue).exists()

    return render(request, 'review_app/venue_reviews.html', {
        'venue': venue,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'rating_percentages': rating_percentages,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    })
