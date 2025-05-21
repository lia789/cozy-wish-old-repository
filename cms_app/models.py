from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import os
import uuid


def get_media_upload_path(instance, filename):
    """Generate file path for media uploads"""
    # Use username as directory name if uploaded by a service provider
    if instance.uploaded_by and instance.uploaded_by.is_service_provider:
        username = instance.uploaded_by.email.split('@')[0]
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        return os.path.join(f'media/cms/{username}', filename)
    else:
        # For admin uploads
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        return os.path.join('media/cms/admin', filename)


class Page(models.Model):
    """Model for static pages like About, Contact, Terms, etc."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True, help_text="Meta description for SEO (max 160 characters)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Meta keywords for SEO (comma separated)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_pages')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_pages')
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('cms_app:page_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class BlogCategory(models.Model):
    """Model for blog categories"""
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('cms_app:blog_category', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Model for blog posts"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text="Short description for previews")
    featured_image = models.ImageField(upload_to=get_media_upload_path, blank=True, null=True)
    categories = models.ManyToManyField(BlogCategory, related_name='blog_posts')
    meta_description = models.CharField(max_length=160, blank=True, help_text="Meta description for SEO (max 160 characters)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Meta keywords for SEO (comma separated)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('cms_app:blog_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)


class BlogComment(models.Model):
    """Model for blog comments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.email} on {self.blog_post.title}"


class MediaItem(models.Model):
    """Model for media library items"""
    
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=get_media_upload_path)
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='image')
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for images")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_items')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def file_url(self):
        return self.file.url if self.file else None
    
    @property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''


class SiteConfiguration(models.Model):
    """Model for site-wide settings and SEO"""
    
    site_name = models.CharField(max_length=100, default='CozyWish')
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(default='info@cozywish.com')
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    default_meta_description = models.CharField(max_length=160, blank=True)
    default_meta_keywords = models.CharField(max_length=255, blank=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        instance, created = cls.objects.get_or_create()
        return instance


class Announcement(models.Model):
    """Model for site-wide announcements"""
    
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_current(self):
        """Check if the announcement is currently active"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.end_date and now > self.end_date:
            return False
        return now >= self.start_date
