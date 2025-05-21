from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Venue, Service, Category, Review, OpeningHours, TeamMember, USCity
from .forms import VenueSearchForm, VenueFilterForm, ReviewForm, VenueForm, ServiceForm, VenueImageForm, OpeningHoursForm, FAQForm, TeamMemberForm




def home_view(request):
    """Home page view for venues app"""
    # Get featured categories
    categories = Category.objects.filter(is_active=True)[:6]

    # Get top rated venues using review_app reviews
    top_venues = Venue.objects.filter(
        approval_status='approved',
        is_active=True
    ).annotate(
        avg_rating=Avg('review_app_reviews__rating'),
        review_count=Count('review_app_reviews')
    ).order_by('-avg_rating')[:4]

    # Get trending venues (most reviewed) using review_app reviews
    trending_venues = Venue.objects.filter(
        approval_status='approved',
        is_active=True
    ).annotate(
        review_count=Count('review_app_reviews')
    ).order_by('-review_count')[:4]

    # Get venues with discounts
    discounted_venues = Venue.objects.filter(
        approval_status='approved',
        is_active=True,
        services__discounted_price__isnull=False
    ).distinct()[:4]

    # Search form
    search_form = VenueSearchForm()

    context = {
        'categories': categories,
        'top_venues': top_venues,
        'trending_venues': trending_venues,
        'discounted_venues': discounted_venues,
        'featured_venues': top_venues,  # Add featured_venues for test compatibility
        'search_form': search_form,
        'hero_section': True  # Enable hero section for home page
    }

    return render(request, 'venues_app/home.html', context)




def venue_list_view(request):
    """View for listing venues with search and filter"""
    # Get all approved and active venues
    venues = Venue.objects.filter(
        approval_status='approved',
        is_active=True
    ).annotate(
        avg_rating=Avg('review_app_reviews__rating'),
        review_count=Count('review_app_reviews')
    ).order_by('-avg_rating', 'name')  # Default to highest rated venues first

    # Process search form
    search_form = VenueSearchForm(request.GET or None)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        location = search_form.cleaned_data.get('location')
        category = search_form.cleaned_data.get('category')

        if query:
            venues = venues.filter(
                Q(name__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(services__title__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()

        if location:
            # Try to find matching US cities first
            city_matches = USCity.objects.filter(
                Q(city__icontains=location) |
                Q(state_name__icontains=location) |
                Q(county_name__icontains=location) |
                Q(state_id__iexact=location)
            )

            if city_matches.exists():
                # Use the us_city relationship if available
                venues = venues.filter(
                    Q(us_city__in=city_matches) |
                    Q(city__icontains=location) |
                    Q(state__icontains=location) |
                    Q(county__icontains=location)
                ).distinct()
            else:
                # Fall back to text search
                venues = venues.filter(
                    Q(city__icontains=location) |
                    Q(state__icontains=location) |
                    Q(county__icontains=location)
                )

        if category:
            venues = venues.filter(category__slug=category)

    # Process filter form
    filter_form = VenueFilterForm(request.GET or None)
    if filter_form.is_valid():
        sort_by = filter_form.cleaned_data.get('sort_by')
        venue_type = filter_form.cleaned_data.get('venue_type')
        has_discount = filter_form.cleaned_data.get('has_discount')
        state = filter_form.cleaned_data.get('state')
        county = filter_form.cleaned_data.get('county')
        city = filter_form.cleaned_data.get('city')

        if venue_type:
            venues = venues.filter(venue_type=venue_type)

        if has_discount:
            venues = venues.filter(services__discounted_price__isnull=False).distinct()

        # Apply location filters
        if state:
            venues = venues.filter(Q(state__iexact=state) | Q(us_city__state_name__iexact=state))

        if county:
            venues = venues.filter(Q(county__iexact=county) | Q(us_city__county_name__iexact=county))

        if city:
            venues = venues.filter(Q(city__iexact=city) | Q(us_city__city__iexact=city))

        if sort_by:
            if sort_by == 'rating_high':
                venues = venues.order_by('-avg_rating', 'name')
            elif sort_by == 'rating_low':
                venues = venues.order_by('avg_rating', 'name')
            elif sort_by == 'price_high':
                venues = venues.order_by('-services__price', 'name').distinct()
            elif sort_by == 'price_low':
                venues = venues.order_by('services__price', 'name').distinct()
            elif sort_by == 'discount':
                # Order by discount percentage (calculated in the query)
                venues = venues.filter(services__discounted_price__isnull=False).distinct()
                # Use raw SQL for complex ordering
                venues = venues.extra(
                    select={'discount_pct': '(services_service.price - services_service.discounted_price) / services_service.price * 100'},
                    tables=['services_service'],
                    where=['venues_app_venue.id = services_service.venue_id'],
                ).order_by('-discount_pct', 'name')

    # Ensure distinct results
    venues = venues.distinct()

    # Pagination
    paginator = Paginator(venues, 12)  # Show 12 venues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'venues': page_obj.object_list,  # Add venues for test compatibility
        'search_form': search_form,
        'filter_form': filter_form,
        'categories': categories,
    }

    return render(request, 'venues_app/venue_list.html', context)




def venue_detail_view(request, slug):
    """View for venue details"""
    # Get the venue
    venue = get_object_or_404(Venue, slug=slug, approval_status='approved', is_active=True)

    # Get venue services
    services = venue.services.filter(is_active=True)

    # Get venue opening hours
    opening_hours = venue.opening_hours.all().order_by('day')

    # Get venue team members
    team_members = venue.team_members.filter(is_active=True)

    # Get venue images
    images = venue.images.all().order_by('image_order')

    # Get venue FAQs
    faqs = venue.faqs.all().order_by('order')

    # Check if user can review this venue
    can_review = False
    has_reviewed = False
    if request.user.is_authenticated and hasattr(request.user, 'is_customer') and request.user.is_customer:
        # Import the has_completed_booking function from review_app
        from review_app.views import has_completed_booking
        can_review = has_completed_booking(request.user, venue)

        # Check if user has already reviewed this venue using review_app
        from review_app.models import Review as ReviewAppReview
        has_reviewed = ReviewAppReview.objects.filter(venue=venue, user=request.user).exists()

    context = {
        'venue': venue,
        'services': services,
        'opening_hours': opening_hours,
        'team_members': team_members,
        'images': images,
        'faqs': faqs,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    }

    return render(request, 'venues_app/venue_detail.html', context)



def service_detail_view(request, venue_slug, service_slug):
    """View for service details"""
    # Get the venue and service
    venue = get_object_or_404(Venue, slug=venue_slug, approval_status='approved', is_active=True)
    service = get_object_or_404(Service, venue=venue, slug=service_slug, is_active=True)

    # Get venue opening hours
    opening_hours = venue.opening_hours.all().order_by('day')

    context = {
        'venue': venue,
        'service': service,
        'opening_hours': opening_hours,
    }

    return render(request, 'venues_app/service_detail.html', context)



@login_required
def submit_review_view(request, venue_slug):
    """View for submitting reviews"""
    # Get the venue
    venue = get_object_or_404(Venue, slug=venue_slug, approval_status='approved', is_active=True)

    # Check if user is a customer
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer:
        messages.error(request, "Only customers can submit reviews.")
        return redirect('venues_app:venue_detail', slug=venue_slug)

    # Check if user has already reviewed this venue
    existing_review = Review.objects.filter(venue=venue, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.venue = venue
            review.user = request.user
            review.save()

            messages.success(request, "Your review has been submitted successfully.")
            return redirect('venues_app:venue_detail', slug=venue_slug)
    else:
        form = ReviewForm(instance=existing_review)

    context = {
        'form': form,
        'venue': venue,
        'existing_review': existing_review,
    }

    return render(request, 'venues_app/submit_review.html', context)



# Service Provider Views

@login_required
def create_venue_view(request):
    """View for service provider to create a new venue"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Check if the service provider already has a venue
    existing_venues = Venue.objects.filter(owner=request.user)
    if existing_venues.count() > 0:
        messages.error(request, "You can only create one venue. Please manage your existing venue.")
        return redirect('venues_app:provider_venue_detail', slug=existing_venues.first().slug)

    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user
            venue.save()

            # Process FAQs
            faq_counter = 1
            faq_count = 0
            max_faqs = 5  # Maximum number of FAQs allowed

            while faq_count < max_faqs:
                question_key = f'faq_question_{faq_counter}'
                answer_key = f'faq_answer_{faq_counter}'

                if question_key not in request.POST or answer_key not in request.POST:
                    faq_counter += 1
                    continue

                question = request.POST.get(question_key).strip()
                answer = request.POST.get(answer_key, '').strip()

                if question and answer:
                    # Create new FAQ
                    from venues_app.models import FAQ
                    FAQ.objects.create(
                        venue=venue,
                        question=question,
                        answer=answer,
                        order=faq_counter
                    )
                    faq_count += 1

                faq_counter += 1

            messages.success(request, "Venue created successfully. Please add images, opening hours, and services.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = VenueForm()

    context = {
        'form': form,
        'title': 'Create Venue',
    }

    return render(request, 'venues_app/provider/venue_form.html', context)



@login_required
def provider_venue_detail_view(request, slug):
    """View for service provider to see venue details"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=slug, owner=request.user)

    # Handle opening hours form submission
    if request.method == 'POST':
        opening_hours_form = OpeningHoursForm(request.POST)
        if opening_hours_form.is_valid():
            opening_hours = opening_hours_form.save(commit=False)
            opening_hours.venue = venue
            opening_hours.save()
            messages.success(request, "Opening hours added successfully.")
    else:
        opening_hours_form = OpeningHoursForm()

    # Get venue services
    services = venue.services.all()

    # Get venue opening hours
    opening_hours = venue.opening_hours.all().order_by('day')

    # Get venue team members
    team_members = venue.team_members.all()

    # Get venue images
    images = venue.images.all().order_by('image_order')

    # Get venue FAQs
    faqs = venue.faqs.all().order_by('order')

    context = {
        'venue': venue,
        'services': services,
        'opening_hours': opening_hours,
        'team_members': team_members,
        'images': images,
        'faqs': faqs,
        'opening_hours_form': opening_hours_form,
    }

    return render(request, 'venues_app/provider/venue_detail.html', context)



@login_required
def edit_venue_view(request, slug):
    """View for service provider to edit a venue"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=slug, owner=request.user)

    if request.method == 'POST':
        form = VenueForm(request.POST, instance=venue)
        if form.is_valid():
            venue = form.save()

            # Process FAQs
            # First, get all existing FAQs for this venue
            existing_faqs = list(venue.faqs.all())
            existing_faq_ids = [faq.id for faq in existing_faqs]

            # Track which FAQs have been processed
            processed_faq_ids = []

            # Process all FAQ fields from the form (maximum 5)
            faq_counter = 1
            faq_count = 0
            max_faqs = 5  # Maximum number of FAQs allowed

            while faq_count < max_faqs:
                question_key = f'faq_question_{faq_counter}'
                answer_key = f'faq_answer_{faq_counter}'
                faq_id_key = f'faq_id_{faq_counter}'

                # Check if this FAQ exists in the form
                if question_key not in request.POST or not request.POST.get(question_key).strip():
                    # No more FAQs to process
                    break

                question = request.POST.get(question_key).strip()
                answer = request.POST.get(answer_key, '').strip()
                faq_id = request.POST.get(faq_id_key, '')

                if faq_id and faq_id.isdigit():
                    # Update existing FAQ
                    faq_id = int(faq_id)
                    try:
                        faq = FAQ.objects.get(id=faq_id, venue=venue)
                        faq.question = question
                        faq.answer = answer
                        faq.order = faq_counter
                        faq.save()
                        processed_faq_ids.append(faq_id)
                        faq_count += 1
                    except FAQ.DoesNotExist:
                        # Create new FAQ if ID doesn't exist
                        if faq_count < max_faqs:
                            FAQ.objects.create(
                                venue=venue,
                                question=question,
                                answer=answer,
                                order=faq_counter
                            )
                            faq_count += 1
                else:
                    # Create new FAQ
                    if faq_count < max_faqs:
                        FAQ.objects.create(
                            venue=venue,
                            question=question,
                            answer=answer,
                            order=faq_counter
                        )
                        faq_count += 1

                faq_counter += 1

            # Delete FAQs that were not included in the form
            for faq_id in existing_faq_ids:
                if faq_id not in processed_faq_ids:
                    try:
                        faq = FAQ.objects.get(id=faq_id, venue=venue)
                        faq.delete()
                    except FAQ.DoesNotExist:
                        pass

            messages.success(request, "Venue updated successfully.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = VenueForm(instance=venue)

    context = {
        'form': form,
        'venue': venue,
        'title': 'Edit Venue',
    }

    return render(request, 'venues_app/provider/venue_form.html', context)


@login_required
def delete_venue_view(request, slug):
    """View for service provider to delete a venue"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=slug, owner=request.user)

    if request.method == 'POST':
        try:
            # Delete all related data
            # Django will handle most related data through CASCADE, but we'll be explicit
            # to ensure everything is properly cleaned up

            # Delete venue images
            venue.images.all().delete()

            # Delete venue services
            venue.services.all().delete()

            # Delete venue opening hours
            venue.opening_hours.all().delete()

            # Delete venue FAQs
            venue.faqs.all().delete()

            # Delete venue team members
            venue.team_members.all().delete()

            # Finally delete the venue itself
            venue.delete()

            messages.success(request, "Venue and all related data deleted successfully.")
            return redirect('dashboard_app:provider_dashboard')
        except Exception as e:
            messages.error(request, f"Error deleting venue: {str(e)}")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)

    context = {
        'venue': venue,
    }

    return render(request, 'venues_app/provider/venue_confirm_delete.html', context)


@login_required
def delete_opening_hours_view(request, venue_slug, hour_id):
    """View for service provider to delete opening hours"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue and opening hours
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)
    opening_hours = get_object_or_404(OpeningHours, id=hour_id, venue=venue)

    if request.method == 'POST':
        opening_hours.delete()
        messages.success(request, "Opening hours deleted successfully.")

    return redirect('venues_app:provider_venue_detail', slug=venue_slug)


@login_required
def create_service_view(request, venue_slug):
    """View for service provider to create a new service"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.venue = venue
            service.save()

            messages.success(request, "Service created successfully.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'venue': venue,
        'title': 'Add Service',  # Change title to match test expectation
    }

    return render(request, 'venues_app/provider/service_form.html', context)


@login_required
def edit_service_view(request, venue_slug, service_slug):
    """View for service provider to edit a service"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue and service
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)
    service = get_object_or_404(Service, slug=service_slug, venue=venue)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = ServiceForm(instance=service)

    context = {
        'form': form,
        'venue': venue,
        'service': service,
        'title': 'Edit Service',
    }

    return render(request, 'venues_app/provider/service_form.html', context)


@login_required
def delete_service_view(request, venue_slug, service_slug):
    """View for service provider to delete a service"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue and service
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)
    service = get_object_or_404(Service, slug=service_slug, venue=venue)

    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect('venues_app:provider_venue_detail', slug=venue.slug)

    context = {
        'venue': venue,
        'service': service,
    }

    return render(request, 'venues_app/provider/service_confirm_delete.html', context)


@login_required
def service_create_redirect(request):
    """Redirect to the service creation page for the provider's venue"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the provider's venue
    venue = Venue.objects.filter(owner=request.user).first()

    if not venue:
        messages.error(request, "You need to create a venue before adding services.")
        return redirect('venues_app:create_venue')

    # Redirect to the service creation page for this venue
    return redirect('venues_app:create_service', venue_slug=venue.slug)


# Admin Views
@login_required
def admin_venue_list_view(request):
    """View for admin to see all venues"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('accounts_app:home')

    # Get all venues
    venues = Venue.objects.all().annotate(
        avg_rating=Avg('review_app_reviews__rating'),
        review_count=Count('review_app_reviews')
    ).order_by('name')  # Add default ordering to avoid UnorderedObjectListWarning

    # Filter by approval status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        venues = venues.filter(approval_status=status_filter)

    # Pagination
    paginator = Paginator(venues, 20)  # Show 20 venues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'venues': page_obj.object_list,  # Add venues for test compatibility
        'status_filter': status_filter,
    }

    return render(request, 'venues_app/admin/venue_list.html', context)


@login_required
def admin_venue_detail_view(request, slug):
    """View for admin to see venue details"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=slug)

    # Get venue services
    services = venue.services.all()

    # Get venue opening hours
    opening_hours = venue.opening_hours.all().order_by('day')

    # Get venue team members
    team_members = venue.team_members.all()

    # Get venue images
    images = venue.images.all().order_by('image_order')

    # Get venue FAQs
    faqs = venue.faqs.all().order_by('order')

    context = {
        'venue': venue,
        'services': services,
        'opening_hours': opening_hours,
        'team_members': team_members,
        'images': images,
        'faqs': faqs,
    }

    return render(request, 'venues_app/admin/venue_detail.html', context)


@login_required
def admin_venue_approval_view(request, slug):
    """View for admin to approve or reject a venue"""
    # Check if user is an admin
    if not request.user.is_staff:
        messages.error(request, "Only administrators can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=slug)

    # Create a form for approval/rejection
    from admin_app.forms import VenueApprovalForm

    if request.method == 'POST':
        form = VenueApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason', '')

            if action == 'approve':
                venue.approval_status = 'approved'
                messages.success(request, "Venue has been approved successfully.")
            elif action == 'reject':
                if not rejection_reason:
                    messages.error(request, "Please provide a reason for rejection.")
                    return redirect('venues_app:admin_venue_approval', slug=venue.slug)
                venue.approval_status = 'rejected'
                venue.rejection_reason = rejection_reason
                messages.success(request, "Venue has been rejected successfully.")

            venue.save()
            return redirect('venues_app:admin_venue_list')
    else:
        form = VenueApprovalForm()

    context = {
        'venue': venue,
        'form': form,
    }

    return render(request, 'venues_app/admin/venue_approval.html', context)


# API Views
def location_suggestions_api(request):
    """API endpoint for location autocomplete suggestions"""
    query = request.GET.get('query', '')
    search_form = VenueSearchForm()
    suggestions = search_form.get_location_suggestions(query)
    return JsonResponse({'suggestions': suggestions})


def get_location_data_api(request):
    """API endpoint for getting location data (states, counties, cities)"""
    state = request.GET.get('state', '')
    county = request.GET.get('county', '')

    filter_form = VenueFilterForm()

    if not state and not county:
        # Return all states
        states = list(filter_form.get_states())
        return JsonResponse({'states': states})

    if state and not county:
        # Return counties for the given state
        counties = list(filter_form.get_counties(state))
        return JsonResponse({'counties': counties})

    if state and county:
        # Return cities for the given state and county
        cities = list(filter_form.get_cities(state, county))
        return JsonResponse({'cities': cities})

    return JsonResponse({'error': 'Invalid parameters'})


# Team Member Views
@login_required
def create_team_member_view(request, venue_slug):
    """View for service provider to create a new team member"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)

    # Check if the venue already has 5 team members
    if venue.team_members.count() >= 5:
        messages.error(request, "You can only have a maximum of 5 team members per venue.")
        return redirect('venues_app:provider_venue_detail', slug=venue.slug)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            team_member = form.save(commit=False)
            team_member.venue = venue
            team_member.save()

            messages.success(request, "Team member added successfully.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = TeamMemberForm(initial={'venue': venue})

    context = {
        'form': form,
        'venue': venue,
        'title': 'Add Team Member',
    }

    return render(request, 'venues_app/provider/team_member_form.html', context)


@login_required
def edit_team_member_view(request, venue_slug, team_member_id):
    """View for service provider to edit a team member"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue and team member
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)
    team_member = get_object_or_404(TeamMember, id=team_member_id, venue=venue)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member updated successfully.")
            return redirect('venues_app:provider_venue_detail', slug=venue.slug)
    else:
        form = TeamMemberForm(instance=team_member)

    context = {
        'form': form,
        'venue': venue,
        'team_member': team_member,
        'title': 'Edit Team Member',
    }

    return render(request, 'venues_app/provider/team_member_form.html', context)


@login_required
def delete_team_member_view(request, venue_slug, team_member_id):
    """View for service provider to delete a team member"""
    # Check if user is a service provider
    if not hasattr(request.user, 'is_service_provider') or not request.user.is_service_provider:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts_app:home')

    # Get the venue and team member
    venue = get_object_or_404(Venue, slug=venue_slug, owner=request.user)
    team_member = get_object_or_404(TeamMember, id=team_member_id, venue=venue)

    if request.method == 'POST':
        team_member.delete()
        messages.success(request, "Team member deleted successfully.")
        return redirect('venues_app:provider_venue_detail', slug=venue.slug)

    context = {
        'venue': venue,
        'team_member': team_member,
    }

    return render(request, 'venues_app/provider/team_member_confirm_delete.html', context)