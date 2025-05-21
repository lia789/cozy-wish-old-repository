from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q
from django.core.cache import cache
from django.http import Http404
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)
from .forms import (
    PageForm, BlogCategoryForm, BlogPostForm, BlogCommentForm,
    MediaUploadForm, SiteConfigurationForm, AnnouncementForm, SearchForm
)


# Helper functions
def is_service_provider(user):
    """Check if user is a service provider"""
    return user.is_authenticated and user.is_service_provider


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_staff


def get_current_announcements():
    """Get current active announcements"""
    announcements = cache.get('active_announcements')
    if announcements is None:
        now = timezone.now()
        announcements = Announcement.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('-created_at')
        cache.set('active_announcements', announcements, 3600)  # Cache for 1 hour
    return announcements


def get_site_config():
    """Get site configuration"""
    config = cache.get('site_configuration')
    if config is None:
        config = SiteConfiguration.get_instance()
        cache.set('site_configuration', config, 86400)  # Cache for 24 hours
    return config


# Public views
def page_view(request, slug):
    """Display a static page"""
    page = cache.get(f'page_{slug}')
    if page is None:
        page = get_object_or_404(Page, slug=slug, status='published')
        cache.set(f'page_{slug}', page, 3600)  # Cache for 1 hour

    announcements = get_current_announcements()
    site_config = get_site_config()

    return render(request, 'cms_app/page_detail.html', {
        'page': page,
        'announcements': announcements,
        'site_config': site_config,
    })


def blog_list_view(request):
    """Display blog posts"""
    category_slug = request.GET.get('category')

    if category_slug:
        category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = BlogPost.objects.filter(
            categories=category,
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')
    else:
        posts = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    # Get featured posts
    featured_posts = posts.filter(is_featured=True)[:3]

    # Paginate the remaining posts
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get all categories for sidebar
    categories = BlogCategory.objects.all()

    announcements = get_current_announcements()
    site_config = get_site_config()

    return render(request, 'cms_app/blog_list.html', {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'current_category': category_slug,
        'announcements': announcements,
        'site_config': site_config,
    })


def blog_detail_view(request, slug):
    """Display a single blog post"""
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        status='published',
        published_at__lte=timezone.now()
    )

    # Get related posts
    related_posts = BlogPost.objects.filter(
        categories__in=post.categories.all(),
        status='published',
        published_at__lte=timezone.now()
    ).exclude(id=post.id).distinct()[:3]

    # Get approved comments
    comments = post.comments.filter(status='approved').order_by('-created_at')

    # Comment form
    if request.method == 'POST' and post.allow_comments and request.user.is_authenticated:
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog_post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
            return redirect('cms_app:blog_detail', slug=slug)
    else:
        comment_form = BlogCommentForm()

    announcements = get_current_announcements()
    site_config = get_site_config()

    return render(request, 'cms_app/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'comment_form': comment_form,
        'announcements': announcements,
        'site_config': site_config,
    })


def blog_category_view(request, slug):
    """Display blog posts by category"""
    category = get_object_or_404(BlogCategory, slug=slug)

    posts = BlogPost.objects.filter(
        categories=category,
        status='published',
        published_at__lte=timezone.now()
    ).order_by('-published_at')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get all categories for sidebar
    categories = BlogCategory.objects.all()

    announcements = get_current_announcements()
    site_config = get_site_config()

    return render(request, 'cms_app/blog_category.html', {
        'category': category,
        'posts': posts,
        'categories': categories,
        'announcements': announcements,
        'site_config': site_config,
    })


def search_view(request):
    """Search content"""
    query = request.GET.get('query', '')
    search_form = SearchForm(initial={'query': query})

    results = {
        'pages': [],
        'blog_posts': [],
    }

    if query:
        # Search pages
        results['pages'] = Page.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        )

        # Search blog posts
        results['blog_posts'] = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(excerpt__icontains=query),
            status='published',
            published_at__lte=timezone.now()
        )

    announcements = get_current_announcements()
    site_config = get_site_config()

    return render(request, 'cms_app/search_results.html', {
        'query': query,
        'search_form': search_form,
        'results': results,
        'announcements': announcements,
        'site_config': site_config,
    })


# Service Provider views
@login_required
@user_passes_test(is_service_provider)
def provider_blog_list_view(request):
    """List service provider's blog posts"""
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'cms_app/provider/blog_list.html', {
        'posts': posts,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_blog_create_view(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Blog post created successfully.')
            return redirect('cms_app:provider_blog_list')
    else:
        form = BlogPostForm(user=request.user)

    return render(request, 'cms_app/provider/blog_form.html', {
        'form': form,
        'is_create': True,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_blog_update_view(request, slug):
    """Update a blog post"""
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('cms_app:provider_blog_list')
    else:
        form = BlogPostForm(instance=post, user=request.user)

    return render(request, 'cms_app/provider/blog_form.html', {
        'form': form,
        'post': post,
        'is_create': False,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_blog_delete_view(request, slug):
    """Delete a blog post"""
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully.')
        return redirect('cms_app:provider_blog_list')

    return render(request, 'cms_app/provider/blog_confirm_delete.html', {
        'post': post,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_media_list_view(request):
    """List service provider's media"""
    media_items = MediaItem.objects.filter(uploaded_by=request.user).order_by('-created_at')

    return render(request, 'cms_app/provider/media_list.html', {
        'media_items': media_items,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_media_upload_view(request):
    """Upload media"""
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            media = form.save()  # The form now handles setting uploaded_by
            messages.success(request, 'Media uploaded successfully.')
            return redirect('cms_app:provider_media_list')
    else:
        form = MediaUploadForm(user=request.user)

    return render(request, 'cms_app/provider/media_form.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_service_provider)
def provider_media_delete_view(request, pk):
    """Delete media"""
    media = get_object_or_404(MediaItem, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        media.delete()
        messages.success(request, 'Media deleted successfully.')
        return redirect('cms_app:provider_media_list')

    return render(request, 'cms_app/provider/media_confirm_delete.html', {
        'media': media,
    })


# Admin views
@login_required
@user_passes_test(is_admin)
def admin_page_list_view(request):
    """List all pages"""
    pages = Page.objects.all().order_by('title')

    return render(request, 'cms_app/admin/page_list.html', {
        'pages': pages,
    })


@login_required
@user_passes_test(is_admin)
def admin_page_create_view(request):
    """Create a new page"""
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.slug = slugify(page.title)
            page.created_by = request.user
            page.updated_by = request.user
            page.save()
            messages.success(request, 'Page created successfully.')
            return redirect('cms_app:admin_page_list')
    else:
        form = PageForm()

    return render(request, 'cms_app/admin/page_form.html', {
        'form': form,
        'is_create': True,
    })


@login_required
@user_passes_test(is_admin)
def admin_page_update_view(request, slug):
    """Update a page"""
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            page.updated_by = request.user
            page.save()
            messages.success(request, 'Page updated successfully.')
            return redirect('cms_app:admin_page_list')
    else:
        form = PageForm(instance=page)

    return render(request, 'cms_app/admin/page_form.html', {
        'form': form,
        'page': page,
        'is_create': False,
    })


@login_required
@user_passes_test(is_admin)
def admin_page_delete_view(request, slug):
    """Delete a page"""
    page = get_object_or_404(Page, slug=slug)

    if request.method == 'POST':
        page.delete()
        messages.success(request, 'Page deleted successfully.')
        return redirect('cms_app:admin_page_list')

    return render(request, 'cms_app/admin/page_confirm_delete.html', {
        'page': page,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_list_view(request):
    """List all blog posts"""
    status_filter = request.GET.get('status', '')

    if status_filter:
        posts = BlogPost.objects.filter(status=status_filter).order_by('-created_at')
    else:
        posts = BlogPost.objects.all().order_by('-created_at')

    return render(request, 'cms_app/admin/blog_list.html', {
        'posts': posts,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_update_view(request, slug):
    """Update a blog post"""
    post = get_object_or_404(BlogPost, slug=slug)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('cms_app:admin_blog_list')
    else:
        form = BlogPostForm(instance=post, user=request.user)

    return render(request, 'cms_app/admin/blog_form.html', {
        'form': form,
        'post': post,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_approve_view(request, slug):
    """Approve a blog post"""
    post = get_object_or_404(BlogPost, slug=slug, status='pending')

    if request.method == 'POST':
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        messages.success(request, 'Blog post approved and published successfully.')
        return redirect('cms_app:admin_blog_list')

    return render(request, 'cms_app/admin/blog_approve.html', {
        'post': post,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_delete_view(request, slug):
    """Delete a blog post"""
    post = get_object_or_404(BlogPost, slug=slug)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully.')
        return redirect('cms_app:admin_blog_list')

    return render(request, 'cms_app/admin/blog_confirm_delete.html', {
        'post': post,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_category_list_view(request):
    """List all blog categories"""
    categories = BlogCategory.objects.all().order_by('name')

    return render(request, 'cms_app/admin/blog_category_list.html', {
        'categories': categories,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_category_create_view(request):
    """Create a new blog category"""
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(category.name)
            category.save()
            messages.success(request, 'Blog category created successfully.')
            return redirect('cms_app:admin_blog_category_list')
    else:
        form = BlogCategoryForm()

    return render(request, 'cms_app/admin/blog_category_form.html', {
        'form': form,
        'is_create': True,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_category_update_view(request, slug):
    """Update a blog category"""
    category = get_object_or_404(BlogCategory, slug=slug)

    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog category updated successfully.')
            return redirect('cms_app:admin_blog_category_list')
    else:
        form = BlogCategoryForm(instance=category)

    return render(request, 'cms_app/admin/blog_category_form.html', {
        'form': form,
        'category': category,
        'is_create': False,
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_category_delete_view(request, slug):
    """Delete a blog category"""
    category = get_object_or_404(BlogCategory, slug=slug)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Blog category deleted successfully.')
        return redirect('cms_app:admin_blog_category_list')

    return render(request, 'cms_app/admin/blog_category_confirm_delete.html', {
        'category': category,
    })


@login_required
@user_passes_test(is_admin)
def admin_media_list_view(request):
    """List all media"""
    media_items = MediaItem.objects.all().order_by('-created_at')

    return render(request, 'cms_app/admin/media_list.html', {
        'media_items': media_items,
    })


@login_required
@user_passes_test(is_admin)
def admin_media_upload_view(request):
    """Upload media"""
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            media = form.save()  # The form now handles setting uploaded_by
            messages.success(request, 'Media uploaded successfully.')
            return redirect('cms_app:admin_media_list')
    else:
        form = MediaUploadForm(user=request.user)

    return render(request, 'cms_app/admin/media_form.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def admin_media_delete_view(request, pk):
    """Delete media"""
    media = get_object_or_404(MediaItem, pk=pk)

    if request.method == 'POST':
        media.delete()
        messages.success(request, 'Media deleted successfully.')
        return redirect('cms_app:admin_media_list')

    return render(request, 'cms_app/admin/media_confirm_delete.html', {
        'media': media,
    })


@login_required
@user_passes_test(is_admin)
def admin_site_configuration_view(request):
    """Configure site settings"""
    config = SiteConfiguration.get_instance()

    if request.method == 'POST':
        form = SiteConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            cache.delete('site_configuration')  # Clear cache
            messages.success(request, 'Site configuration updated successfully.')
            return redirect('cms_app:admin_site_configuration')
    else:
        form = SiteConfigurationForm(instance=config)

    return render(request, 'cms_app/admin/site_configuration.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def admin_announcement_list_view(request):
    """List all announcements"""
    announcements = Announcement.objects.all().order_by('-created_at')

    return render(request, 'cms_app/admin/announcement_list.html', {
        'announcements': announcements,
    })


@login_required
@user_passes_test(is_admin)
def admin_announcement_create_view(request):
    """Create a new announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            cache.delete('active_announcements')  # Clear cache
            messages.success(request, 'Announcement created successfully.')
            return redirect('cms_app:admin_announcement_list')
    else:
        form = AnnouncementForm()

    return render(request, 'cms_app/admin/announcement_form.html', {
        'form': form,
        'is_create': True,
    })


@login_required
@user_passes_test(is_admin)
def admin_announcement_update_view(request, pk):
    """Update an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            cache.delete('active_announcements')  # Clear cache
            messages.success(request, 'Announcement updated successfully.')
            return redirect('cms_app:admin_announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'cms_app/admin/announcement_form.html', {
        'form': form,
        'announcement': announcement,
        'is_create': False,
    })


@login_required
@user_passes_test(is_admin)
def admin_announcement_delete_view(request, pk):
    """Delete an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        announcement.delete()
        cache.delete('active_announcements')  # Clear cache
        messages.success(request, 'Announcement deleted successfully.')
        return redirect('cms_app:admin_announcement_list')

    return render(request, 'cms_app/admin/announcement_confirm_delete.html', {
        'announcement': announcement,
    })
