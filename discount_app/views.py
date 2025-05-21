from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import VenueDiscount, ServiceDiscount, PlatformDiscount, DiscountUsage
from .forms import VenueDiscountForm, ServiceDiscountForm, PlatformDiscountForm, DiscountFilterForm, DiscountApprovalForm
from venues_app.models import Venue, Service, Category


# Service Provider Views
@login_required
def service_provider_discounts(request):
    """View for service providers to see all their discounts"""
    # Get venues owned by the service provider
    venues = Venue.objects.filter(owner=request.user, approval_status='approved')

    # Get filter parameters
    filter_form = DiscountFilterForm(request.GET)
    filters = {}

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        discount_type = filter_form.cleaned_data.get('discount_type')
        min_value = filter_form.cleaned_data.get('min_value')
        max_value = filter_form.cleaned_data.get('max_value')
        search = filter_form.cleaned_data.get('search')

        # Apply filters
        if status:
            now = timezone.now()
            if status == 'active':
                filters.update({'start_date__lte': now, 'end_date__gte': now})
            elif status == 'scheduled':
                filters.update({'start_date__gt': now})
            elif status == 'expired':
                filters.update({'end_date__lt': now})

        if discount_type:
            filters.update({'discount_type': discount_type})

        if min_value is not None:
            filters.update({'discount_value__gte': min_value})

        if max_value is not None:
            filters.update({'discount_value__lte': max_value})

    # Get venue discounts
    venue_discounts = VenueDiscount.objects.filter(venue__in=venues, **filters)

    # Get service discounts
    service_discounts = ServiceDiscount.objects.filter(service__venue__in=venues, **filters)

    # Apply search if provided
    if filter_form.is_valid() and filter_form.cleaned_data.get('search'):
        search = filter_form.cleaned_data.get('search')
        venue_discounts = venue_discounts.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
        service_discounts = service_discounts.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Combine and paginate results
    venue_discounts = list(venue_discounts)
    service_discounts = list(service_discounts)
    all_discounts = venue_discounts + service_discounts
    all_discounts.sort(key=lambda x: x.created_at, reverse=True)

    paginator = Paginator(all_discounts, 10)  # Show 10 discounts per page
    page = request.GET.get('page')

    try:
        discounts = paginator.page(page)
    except PageNotAnInteger:
        discounts = paginator.page(1)
    except EmptyPage:
        discounts = paginator.page(paginator.num_pages)

    context = {
        'discounts': discounts,
        'filter_form': filter_form,
        'venues': venues,
    }

    return render(request, 'discount_app/service_provider/discount_list.html', context)


@login_required
def create_venue_discount(request):
    """View for service providers to create a venue-wide discount"""
    if request.method == 'POST':
        form = VenueDiscountForm(request.POST, user=request.user)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.venue = form.cleaned_data['venue']
            discount.save()

            messages.success(request, f'Discount "{discount.name}" has been created and is pending approval.')
            return redirect('discount_app:service_provider_discounts')
    else:
        form = VenueDiscountForm(user=request.user)

    context = {
        'form': form,
        'title': 'Create Venue Discount',
    }

    return render(request, 'discount_app/service_provider/discount_form.html', context)


@login_required
def create_service_discount(request):
    """View for service providers to create a service-specific discount"""
    venue_id = request.GET.get('venue_id')
    venue = None

    if venue_id:
        venue = get_object_or_404(Venue, id=venue_id, owner=request.user, approval_status='approved')

    if request.method == 'POST':
        form = ServiceDiscountForm(request.POST, user=request.user, venue=venue)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.service = form.cleaned_data['service']
            discount.save()

            messages.success(request, f'Discount "{discount.name}" has been created and is pending approval.')
            return redirect('discount_app:service_provider_discounts')
    else:
        form = ServiceDiscountForm(user=request.user, venue=venue)

    context = {
        'form': form,
        'title': 'Create Service Discount',
        'venue': venue,
    }

    return render(request, 'discount_app/service_provider/discount_form.html', context)


@login_required
def edit_venue_discount(request, discount_id):
    """View for service providers to edit a venue-wide discount"""
    # Get the discount and verify ownership
    discount = get_object_or_404(VenueDiscount, id=discount_id, venue__owner=request.user)

    # Check if discount can be edited (not expired or cancelled)
    if discount.get_status() == 'expired':
        messages.error(request, 'Expired discounts cannot be edited.')
        return redirect('discount_app:service_provider_discounts')

    if request.method == 'POST':
        form = VenueDiscountForm(request.POST, instance=discount, user=request.user)
        if form.is_valid():
            updated_discount = form.save(commit=False)
            updated_discount.is_approved = False  # Reset approval status
            updated_discount.approved_by = None
            updated_discount.approved_at = None
            updated_discount.save()

            messages.success(request, f'Discount "{updated_discount.name}" has been updated and is pending approval.')
            return redirect('discount_app:service_provider_discounts')
    else:
        form = VenueDiscountForm(instance=discount, user=request.user)

    context = {
        'form': form,
        'title': 'Edit Venue Discount',
        'discount': discount,
    }

    return render(request, 'discount_app/service_provider/discount_form.html', context)


@login_required
def edit_service_discount(request, discount_id):
    """View for service providers to edit a service-specific discount"""
    # Get the discount and verify ownership
    discount = get_object_or_404(ServiceDiscount, id=discount_id, service__venue__owner=request.user)

    # Check if discount can be edited (not expired or cancelled)
    if discount.get_status() == 'expired':
        messages.error(request, 'Expired discounts cannot be edited.')
        return redirect('discount_app:service_provider_discounts')

    venue = discount.service.venue

    if request.method == 'POST':
        form = ServiceDiscountForm(request.POST, instance=discount, user=request.user, venue=venue)
        if form.is_valid():
            updated_discount = form.save(commit=False)
            updated_discount.is_approved = False  # Reset approval status
            updated_discount.approved_by = None
            updated_discount.approved_at = None
            updated_discount.save()

            messages.success(request, f'Discount "{updated_discount.name}" has been updated and is pending approval.')
            return redirect('discount_app:service_provider_discounts')
    else:
        form = ServiceDiscountForm(instance=discount, user=request.user, venue=venue)

    context = {
        'form': form,
        'title': 'Edit Service Discount',
        'discount': discount,
        'venue': venue,
    }

    return render(request, 'discount_app/service_provider/discount_form.html', context)


@login_required
def delete_discount(request, discount_type, discount_id):
    """View for service providers to delete a discount"""
    if discount_type == 'venue':
        discount = get_object_or_404(VenueDiscount, id=discount_id, venue__owner=request.user)
    elif discount_type == 'service':
        discount = get_object_or_404(ServiceDiscount, id=discount_id, service__venue__owner=request.user)
    else:
        messages.error(request, 'Invalid discount type.')
        return redirect('discount_app:service_provider_discounts')

    if request.method == 'POST':
        discount_name = discount.name
        discount.delete()
        messages.success(request, f'Discount "{discount_name}" has been deleted.')
        return redirect('discount_app:service_provider_discounts')

    context = {
        'discount': discount,
        'discount_type': discount_type,
    }

    return render(request, 'discount_app/service_provider/discount_delete.html', context)


@login_required
def discount_detail(request, discount_type, discount_id):
    """View for service providers to see discount details"""
    if discount_type == 'venue':
        discount = get_object_or_404(VenueDiscount, id=discount_id, venue__owner=request.user)
        related_entity = discount.venue
        entity_type = 'venue'
    elif discount_type == 'service':
        discount = get_object_or_404(ServiceDiscount, id=discount_id, service__venue__owner=request.user)
        related_entity = discount.service
        entity_type = 'service'
    else:
        messages.error(request, 'Invalid discount type.')
        return redirect('discount_app:service_provider_discounts')

    # Get usage statistics
    usage_count = DiscountUsage.objects.filter(
        discount_type=discount_type.capitalize() + 'Discount',
        discount_id=discount_id
    ).count()

    context = {
        'discount': discount,
        'discount_type': discount_type,
        'related_entity': related_entity,
        'entity_type': entity_type,
        'usage_count': usage_count,
    }

    return render(request, 'discount_app/service_provider/discount_detail.html', context)


# Admin Views
def is_admin(user):
    """Check if user is admin"""
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_discount_dashboard(request):
    """Admin dashboard for discounts"""
    # Get counts
    total_venue_discounts = VenueDiscount.objects.count()
    total_service_discounts = ServiceDiscount.objects.count()
    total_platform_discounts = PlatformDiscount.objects.count()

    # Get active discounts
    now = timezone.now()
    active_venue_discounts = VenueDiscount.objects.filter(start_date__lte=now, end_date__gte=now).count()
    active_service_discounts = ServiceDiscount.objects.filter(start_date__lte=now, end_date__gte=now).count()
    active_platform_discounts = PlatformDiscount.objects.filter(start_date__lte=now, end_date__gte=now).count()

    # Get pending approvals
    pending_venue_approvals = VenueDiscount.objects.filter(is_approved=False).count()
    pending_service_approvals = ServiceDiscount.objects.filter(is_approved=False).count()

    # Get usage statistics
    total_usages = DiscountUsage.objects.count()
    venue_discount_usages = DiscountUsage.objects.filter(discount_type='VenueDiscount').count()
    service_discount_usages = DiscountUsage.objects.filter(discount_type='ServiceDiscount').count()
    platform_discount_usages = DiscountUsage.objects.filter(discount_type='PlatformDiscount').count()

    # Get top discounts by usage
    top_venue_discounts = DiscountUsage.objects.filter(discount_type='VenueDiscount')\
        .values('discount_id')\
        .annotate(usage_count=Count('id'))\
        .order_by('-usage_count')[:5]

    top_service_discounts = DiscountUsage.objects.filter(discount_type='ServiceDiscount')\
        .values('discount_id')\
        .annotate(usage_count=Count('id'))\
        .order_by('-usage_count')[:5]

    top_platform_discounts = DiscountUsage.objects.filter(discount_type='PlatformDiscount')\
        .values('discount_id')\
        .annotate(usage_count=Count('id'))\
        .order_by('-usage_count')[:5]

    # Enrich top discounts with actual discount objects
    for item in top_venue_discounts:
        try:
            item['discount'] = VenueDiscount.objects.get(id=item['discount_id'])
        except VenueDiscount.DoesNotExist:
            item['discount'] = None

    for item in top_service_discounts:
        try:
            item['discount'] = ServiceDiscount.objects.get(id=item['discount_id'])
        except ServiceDiscount.DoesNotExist:
            item['discount'] = None

    for item in top_platform_discounts:
        try:
            item['discount'] = PlatformDiscount.objects.get(id=item['discount_id'])
        except PlatformDiscount.DoesNotExist:
            item['discount'] = None

    context = {
        'total_venue_discounts': total_venue_discounts,
        'total_service_discounts': total_service_discounts,
        'total_platform_discounts': total_platform_discounts,
        'active_venue_discounts': active_venue_discounts,
        'active_service_discounts': active_service_discounts,
        'active_platform_discounts': active_platform_discounts,
        'pending_venue_approvals': pending_venue_approvals,
        'pending_service_approvals': pending_service_approvals,
        'total_usages': total_usages,
        'venue_discount_usages': venue_discount_usages,
        'service_discount_usages': service_discount_usages,
        'platform_discount_usages': platform_discount_usages,
        'top_venue_discounts': top_venue_discounts,
        'top_service_discounts': top_service_discounts,
        'top_platform_discounts': top_platform_discounts,
    }

    return render(request, 'discount_app/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_discount_list(request, discount_type):
    """Admin view to list discounts by type"""
    # Get filter parameters
    filter_form = DiscountFilterForm(request.GET)
    filters = {}

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        discount_type_filter = filter_form.cleaned_data.get('discount_type')
        min_value = filter_form.cleaned_data.get('min_value')
        max_value = filter_form.cleaned_data.get('max_value')
        search = filter_form.cleaned_data.get('search')

        # Apply filters
        if status:
            now = timezone.now()
            if status == 'active':
                filters.update({'start_date__lte': now, 'end_date__gte': now})
            elif status == 'scheduled':
                filters.update({'start_date__gt': now})
            elif status == 'expired':
                filters.update({'end_date__lt': now})

        if discount_type_filter:
            filters.update({'discount_type': discount_type_filter})

        if min_value is not None:
            filters.update({'discount_value__gte': min_value})

        if max_value is not None:
            filters.update({'discount_value__lte': max_value})

    # Get discounts based on type
    if discount_type == 'venue':
        discounts = VenueDiscount.objects.filter(**filters).select_related('venue', 'created_by')
        title = 'Venue Discounts'
    elif discount_type == 'service':
        discounts = ServiceDiscount.objects.filter(**filters).select_related('service', 'service__venue', 'created_by')
        title = 'Service Discounts'
    elif discount_type == 'platform':
        discounts = PlatformDiscount.objects.filter(**filters).select_related('category', 'created_by')
        title = 'Platform Discounts'
    else:
        messages.error(request, 'Invalid discount type.')
        return redirect('discount_app:admin_discount_dashboard')

    # Apply search if provided
    if filter_form.is_valid() and filter_form.cleaned_data.get('search'):
        search = filter_form.cleaned_data.get('search')
        discounts = discounts.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Paginate results
    paginator = Paginator(discounts, 20)  # Show 20 discounts per page
    page = request.GET.get('page')

    try:
        discounts_page = paginator.page(page)
    except PageNotAnInteger:
        discounts_page = paginator.page(1)
    except EmptyPage:
        discounts_page = paginator.page(paginator.num_pages)

    context = {
        'discounts': discounts_page,
        'filter_form': filter_form,
        'discount_type': discount_type,
        'title': title,
    }

    return render(request, 'discount_app/admin/discount_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_discount_detail(request, discount_type, discount_id):
    """Admin view to see discount details"""
    if discount_type == 'venue':
        discount = get_object_or_404(VenueDiscount, id=discount_id)
        related_entity = discount.venue
        entity_type = 'venue'
    elif discount_type == 'service':
        discount = get_object_or_404(ServiceDiscount, id=discount_id)
        related_entity = discount.service
        entity_type = 'service'
    elif discount_type == 'platform':
        discount = get_object_or_404(PlatformDiscount, id=discount_id)
        related_entity = discount.category
        entity_type = 'category'
    else:
        messages.error(request, 'Invalid discount type.')
        return redirect('discount_app:admin_discount_dashboard')

    # Get usage statistics
    usage_count = DiscountUsage.objects.filter(
        discount_type=discount_type.capitalize() + 'Discount',
        discount_id=discount_id
    ).count()

    # Get recent usages
    recent_usages = DiscountUsage.objects.filter(
        discount_type=discount_type.capitalize() + 'Discount',
        discount_id=discount_id
    ).select_related('user', 'booking').order_by('-used_at')[:10]

    context = {
        'discount': discount,
        'discount_type': discount_type,
        'related_entity': related_entity,
        'entity_type': entity_type,
        'usage_count': usage_count,
        'recent_usages': recent_usages,
    }

    return render(request, 'discount_app/admin/discount_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_approve_discount(request, discount_type, discount_id):
    """Admin view to approve or reject a discount"""
    if discount_type == 'venue':
        discount = get_object_or_404(VenueDiscount, id=discount_id)
    elif discount_type == 'service':
        discount = get_object_or_404(ServiceDiscount, id=discount_id)
    else:
        messages.error(request, 'Invalid discount type.')
        return redirect('discount_app:admin_discount_dashboard')

    if request.method == 'POST':
        form = DiscountApprovalForm(request.POST)
        if form.is_valid():
            is_approved = form.cleaned_data['is_approved']
            rejection_reason = form.cleaned_data.get('rejection_reason')

            discount.is_approved = is_approved
            if is_approved:
                discount.approved_by = request.user
                discount.approved_at = timezone.now()
                messages.success(request, f'Discount "{discount.name}" has been approved.')
            else:
                # Handle rejection (could send notification to provider)
                messages.success(request, f'Discount "{discount.name}" has been rejected.')

            discount.save()

            return redirect('discount_app:admin_discount_list', discount_type=discount_type)
    else:
        form = DiscountApprovalForm()

    context = {
        'form': form,
        'discount': discount,
        'discount_type': discount_type,
    }

    return render(request, 'discount_app/admin/discount_approval.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_platform_discount(request):
    """Admin view to create a platform-wide discount"""
    if request.method == 'POST':
        form = PlatformDiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.save()

            messages.success(request, f'Platform discount "{discount.name}" has been created.')
            return redirect('discount_app:admin_discount_list', discount_type='platform')
    else:
        form = PlatformDiscountForm()

    context = {
        'form': form,
        'title': 'Create Platform Discount',
    }

    return render(request, 'discount_app/admin/platform_discount_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_platform_discount(request, discount_id):
    """Admin view to edit a platform-wide discount"""
    discount = get_object_or_404(PlatformDiscount, id=discount_id)

    if request.method == 'POST':
        form = PlatformDiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()

            messages.success(request, f'Platform discount "{discount.name}" has been updated.')
            return redirect('discount_app:admin_discount_list', discount_type='platform')
    else:
        form = PlatformDiscountForm(instance=discount)

    context = {
        'form': form,
        'title': 'Edit Platform Discount',
        'discount': discount,
    }

    return render(request, 'discount_app/admin/platform_discount_form.html', context)


# Customer Views
def featured_discounts(request):
    """View for customers to see featured discounts"""
    now = timezone.now()

    # Get featured platform discounts
    featured_platform_discounts = PlatformDiscount.objects.filter(
        is_featured=True,
        start_date__lte=now,
        end_date__gte=now
    ).select_related('category')[:6]

    # Get venue discounts with highest percentage
    top_venue_discounts = VenueDiscount.objects.filter(
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now,
        discount_type='percentage'
    ).select_related('venue').order_by('-discount_value')[:6]

    # Get service discounts with highest percentage
    top_service_discounts = ServiceDiscount.objects.filter(
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now,
        discount_type='percentage'
    ).select_related('service', 'service__venue').order_by('-discount_value')[:6]

    context = {
        'featured_platform_discounts': featured_platform_discounts,
        'top_venue_discounts': top_venue_discounts,
        'top_service_discounts': top_service_discounts,
    }

    return render(request, 'discount_app/customer/featured_discounts.html', context)


def venue_discounts(request, venue_id):
    """View for customers to see all discounts for a specific venue"""
    venue = get_object_or_404(Venue, id=venue_id, approval_status='approved')
    now = timezone.now()

    # Get active venue discounts
    venue_discounts = VenueDiscount.objects.filter(
        venue=venue,
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now
    )

    # Get active service discounts for this venue
    service_discounts = ServiceDiscount.objects.filter(
        service__venue=venue,
        is_approved=True,
        start_date__lte=now,
        end_date__gte=now
    ).select_related('service')

    context = {
        'venue': venue,
        'venue_discounts': venue_discounts,
        'service_discounts': service_discounts,
    }

    return render(request, 'discount_app/customer/venue_discounts.html', context)


def search_discounts(request):
    """View for customers to search for discounts"""
    filter_form = DiscountFilterForm(request.GET)
    filters = {
        'is_approved': True,
        'start_date__lte': timezone.now(),
        'end_date__gte': timezone.now(),
    }

    if filter_form.is_valid():
        discount_type = filter_form.cleaned_data.get('discount_type')
        min_value = filter_form.cleaned_data.get('min_value')
        max_value = filter_form.cleaned_data.get('max_value')
        search = filter_form.cleaned_data.get('search')

        # Apply filters
        if discount_type:
            filters.update({'discount_type': discount_type})

        if min_value is not None:
            filters.update({'discount_value__gte': min_value})

        if max_value is not None:
            filters.update({'discount_value__lte': max_value})

    # Get venue discounts
    venue_discounts = VenueDiscount.objects.filter(**filters).select_related('venue')

    # Get service discounts
    service_discounts = ServiceDiscount.objects.filter(**filters).select_related('service', 'service__venue')

    # Apply search if provided
    if filter_form.is_valid() and filter_form.cleaned_data.get('search'):
        search = filter_form.cleaned_data.get('search')
        venue_discounts = venue_discounts.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(venue__name__icontains=search)
        )
        service_discounts = service_discounts.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(service__title__icontains=search) |
            Q(service__venue__name__icontains=search)
        )

    # Combine and paginate results
    venue_discounts = list(venue_discounts)
    service_discounts = list(service_discounts)
    all_discounts = venue_discounts + service_discounts
    all_discounts.sort(key=lambda x: x.discount_value, reverse=True)

    paginator = Paginator(all_discounts, 12)  # Show 12 discounts per page
    page = request.GET.get('page')

    try:
        discounts = paginator.page(page)
    except PageNotAnInteger:
        discounts = paginator.page(1)
    except EmptyPage:
        discounts = paginator.page(paginator.num_pages)

    context = {
        'discounts': discounts,
        'filter_form': filter_form,
        'venue_discount_count': len(venue_discounts),
        'service_discount_count': len(service_discounts),
    }

    return render(request, 'discount_app/customer/search_discounts.html', context)


def test_view(request):
    """Test view to make sure the app is working"""
    return render(request, 'discount_app/test.html')