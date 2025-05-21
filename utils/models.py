from django.db import models
from django.conf import settings


class ImageMetadata(models.Model):
    """Model to store metadata for images"""
    
    # Image types
    IMAGE_TYPES = [
        ('profile', 'Profile Image'),
        ('logo', 'Business Logo'),
        ('venue', 'Venue Image'),
        ('other', 'Other'),
    ]
    
    # Entity types
    ENTITY_TYPES = [
        ('customers', 'Customer'),
        ('professionals', 'Service Provider'),
        ('venues', 'Venue'),
        ('staff', 'Staff Member'),
        ('other', 'Other'),
    ]
    
    # Basic information
    image_path = models.CharField(max_length=255, unique=True)
    thumbnail_path = models.CharField(max_length=255, blank=True)
    high_res_path = models.CharField(max_length=255, blank=True)
    original_path = models.CharField(max_length=255, blank=True)
    
    # Image type and entity information
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='other')
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, default='other')
    entity_id = models.IntegerField(null=True, blank=True)
    
    # Technical metadata
    width = models.IntegerField()
    height = models.IntegerField()
    file_size = models.IntegerField(help_text="Size in bytes")
    original_file_size = models.IntegerField(help_text="Original size in bytes", null=True, blank=True)
    format = models.CharField(max_length=10)
    content_type = models.CharField(max_length=50)
    
    # Tracking information
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='uploaded_images'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Image Metadata"
        verbose_name_plural = "Image Metadata"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_image_type_display()} - {self.image_path}"
    
    @property
    def aspect_ratio(self):
        """Calculate the aspect ratio of the image"""
        if self.height > 0:
            return self.width / self.height
        return 0
    
    @property
    def file_size_kb(self):
        """Return the file size in KB"""
        return self.file_size / 1024
    
    @property
    def original_file_size_kb(self):
        """Return the original file size in KB"""
        if self.original_file_size:
            return self.original_file_size / 1024
        return 0
    
    @property
    def compression_ratio(self):
        """Calculate the compression ratio"""
        if self.original_file_size and self.original_file_size > 0:
            return self.file_size / self.original_file_size
        return 1.0
