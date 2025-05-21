from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'status')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def post_count(self, obj):
        return obj.blog_posts.count()
    post_count.short_description = 'Posts'


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'content', 'status', 'created_at')
    can_delete = True


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'is_featured', 'published_at', 'created_at')
    list_filter = ('status', 'is_featured', 'categories', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    filter_horizontal = ('categories',)
    inlines = [BlogCommentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'featured_image')
        }),
        ('Categories', {
            'fields': ('categories',),
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'allow_comments', 'published_at'),
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'author', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'author__email', 'blog_post__title')
    readonly_fields = ('blog_post', 'author', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('blog_post', 'author', 'content', 'status')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'file_preview', 'uploaded_by', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('title', 'description', 'alt_text')
    readonly_fields = ('file_preview', 'file_size_display', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'file', 'file_type', 'description', 'alt_text')
        }),
        ('File Information', {
            'fields': ('file_preview', 'file_size_display'),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    def file_preview(self, obj):
        if obj.file_type == 'image' and obj.file:
            return format_html('<img src="{}" width="100" height="auto" />', obj.file_url)
        return '-'
    file_preview.short_description = 'Preview'
    
    def file_size_display(self, obj):
        size = obj.file_size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    file_size_display.short_description = 'File Size'
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'maintenance_mode', 'updated_at')
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address'),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url'),
            'classes': ('collapse',),
        }),
        ('SEO & Analytics', {
            'fields': ('google_analytics_id', 'default_meta_description', 'default_meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Check if there's already an instance
        return not SiteConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'is_active', 'is_current_display', 'start_date', 'end_date')
    list_filter = ('announcement_type', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'announcement_type', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date'),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def is_current_display(self, obj):
        return obj.is_current
    is_current_display.boolean = True
    is_current_display.short_description = 'Is Current'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
