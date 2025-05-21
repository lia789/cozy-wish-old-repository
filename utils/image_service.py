import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import ImageMetadata


class ImageService:
    """Service for handling image storage and retrieval"""
    
    @staticmethod
    def save_image(processed_image_data, user=None):
        """
        Save a processed image and its metadata
        
        Args:
            processed_image_data: The result from process_image function
            user: The user who uploaded the image
            
        Returns:
            tuple: (main_image_path, metadata_object)
        """
        # Extract data
        image = processed_image_data['image']
        path = processed_image_data['path']
        thumbnail = processed_image_data.get('thumbnail')
        high_res = processed_image_data.get('high_res')
        metadata = processed_image_data['metadata']
        
        # Save the main image
        saved_path = default_storage.save(path, image)
        
        # Save the thumbnail if available
        thumbnail_path = None
        if thumbnail:
            thumbnail_path = default_storage.save(thumbnail['path'], thumbnail['image'])
        
        # Save the high-res version if available
        high_res_path = None
        if high_res:
            high_res_path = default_storage.save(high_res['path'], high_res['image'])
        
        # Save original image for future reprocessing
        original_path = None
        if 'original_image' in processed_image_data:
            original_filename = f"original_{os.path.basename(path)}"
            original_dir = os.path.dirname(path)
            original_path = os.path.join(original_dir, 'originals', original_filename)
            default_storage.save(original_path, processed_image_data['original_image'])
        
        # Create metadata record
        image_metadata = ImageMetadata(
            image_path=saved_path,
            thumbnail_path=thumbnail_path,
            high_res_path=high_res_path,
            original_path=original_path,
            image_type=processed_image_data.get('image_type', 'other'),
            entity_type=processed_image_data.get('entity_type', 'other'),
            entity_id=processed_image_data.get('entity_id'),
            width=metadata['width'],
            height=metadata['height'],
            file_size=metadata['processed_size'],
            original_file_size=metadata['original_size'],
            format=metadata['format'],
            content_type=metadata['content_type'],
            uploaded_by=user
        )
        image_metadata.save()
        
        return saved_path, image_metadata
    
    @staticmethod
    def get_image_url(image_path):
        """Get the full URL for an image path"""
        if not image_path:
            return None
        
        if default_storage.exists(image_path):
            return default_storage.url(image_path)
        return None
    
    @staticmethod
    def get_thumbnail_url(metadata_or_path):
        """Get the thumbnail URL for an image"""
        if isinstance(metadata_or_path, ImageMetadata):
            path = metadata_or_path.thumbnail_path
        else:
            path = metadata_or_path
            
        return ImageService.get_image_url(path)
    
    @staticmethod
    def get_high_res_url(metadata_or_path):
        """Get the high-res URL for an image"""
        if isinstance(metadata_or_path, ImageMetadata):
            path = metadata_or_path.high_res_path
        else:
            path = metadata_or_path
            
        return ImageService.get_image_url(path)
    
    @staticmethod
    def delete_image(metadata_or_path):
        """Delete an image and all its versions"""
        if isinstance(metadata_or_path, ImageMetadata):
            metadata = metadata_or_path
        else:
            try:
                metadata = ImageMetadata.objects.get(image_path=metadata_or_path)
            except ImageMetadata.DoesNotExist:
                # Just delete the file if no metadata exists
                if default_storage.exists(metadata_or_path):
                    default_storage.delete(metadata_or_path)
                return
        
        # Delete all image files
        for path in [
            metadata.image_path,
            metadata.thumbnail_path,
            metadata.high_res_path,
            metadata.original_path
        ]:
            if path and default_storage.exists(path):
                default_storage.delete(path)
        
        # Delete the metadata
        metadata.delete()
