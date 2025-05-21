import os
import uuid
import datetime
from io import BytesIO
from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils import timezone


# Image format specifications
IMAGE_SPECS = {
    'profile': {
        'format': 'JPEG',
        'quality': 85,
        'size': (800, 800),
        'aspect_ratio': 1.0,  # 1:1 square
        'max_file_size': 100 * 1024,  # 100KB
    },
    'logo': {
        'format': 'PNG',
        'quality': 90,
        'size': (500, 500),
        'aspect_ratio': None,  # Varies
        'max_file_size': 150 * 1024,  # 150KB
        'high_res_size': (1000, 1000),
    },
    'venue': {
        'format': 'JPEG',
        'quality': 90,
        'size': (1200, 800),  # 3:2 aspect ratio
        'aspect_ratio': 1.5,  # 3:2
        'max_file_size': 500 * 1024,  # 500KB
    },
    'thumbnail': {
        'format': 'JPEG',
        'quality': 80,
        'size': (300, 200),
        'aspect_ratio': 1.5,  # 3:2
        'max_file_size': 50 * 1024,  # 50KB
    }
}

# Allowed file extensions by image type
ALLOWED_EXTENSIONS = {
    'profile': ['.jpg', '.jpeg', '.png'],
    'logo': ['.png', '.jpg', '.jpeg'],
    'venue': ['.jpg', '.jpeg', '.png'],
}

def get_file_extension(filename):
    """Get the lowercase file extension with dot."""
    return os.path.splitext(filename)[1].lower()

def validate_image_extension(filename, image_type='profile'):
    """Validate that the file has an allowed extension for the given image type."""
    ext = get_file_extension(filename)
    if ext not in ALLOWED_EXTENSIONS.get(image_type, ALLOWED_EXTENSIONS['profile']):
        allowed = ', '.join(ALLOWED_EXTENSIONS.get(image_type, ALLOWED_EXTENSIONS['profile']))
        raise ValidationError(f"Unsupported file extension. Allowed extensions are: {allowed}")
    return True

def validate_image_size(file, max_size_kb=500):
    """Validate that the file size is under the maximum allowed size."""
    max_size_bytes = max_size_kb * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f"File size exceeds maximum allowed size of {max_size_kb}KB.")
    return True

def generate_filename(entity_type, entity_id, image_type, original_filename):
    """Generate a filename with timestamp and random string to prevent collisions."""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_string = uuid.uuid4().hex[:8]
    ext = get_file_extension(original_filename)
    return f"{timestamp}_{random_string}{ext}"

def generate_image_path(entity_type, entity_id, image_type, filename):
    """Generate the full path for storing an image according to the directory structure."""
    return os.path.join(entity_type, str(entity_id), 'images', image_type, filename)

def strip_exif_data(image):
    """Remove EXIF data from an image for privacy."""
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    return image_without_exif

def process_image(image_file, image_type='profile', entity_type=None, entity_id=None):
    """
    Process an uploaded image according to specifications.
    
    Args:
        image_file: The uploaded image file
        image_type: Type of image (profile, logo, venue)
        entity_type: Type of entity (customers, professionals, venues)
        entity_id: ID of the entity
        
    Returns:
        dict: A dictionary containing processed image data and metadata
    """
    # Validate file extension
    validate_image_extension(image_file.name, image_type)
    
    # Validate file size against the maximum allowed for this type
    max_size = IMAGE_SPECS[image_type]['max_file_size'] // 1024  # Convert to KB
    validate_image_size(image_file, max_size)
    
    # Open the image using PIL
    img = Image.open(image_file)
    
    # Strip EXIF data
    img = strip_exif_data(img)
    
    # Get image specifications
    specs = IMAGE_SPECS[image_type]
    target_size = specs['size']
    target_format = specs['format']
    quality = specs['quality']
    
    # Resize image while maintaining aspect ratio if specified
    if specs['aspect_ratio']:
        img_ratio = img.width / img.height
        target_ratio = specs['aspect_ratio']
        
        if abs(img_ratio - target_ratio) > 0.1:  # If ratios differ significantly
            # Crop to target aspect ratio
            if img_ratio > target_ratio:  # Image is wider
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:  # Image is taller
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))
    
    # Resize to target dimensions
    img = img.resize(target_size, Image.LANCZOS)
    
    # Save to BytesIO
    output = BytesIO()
    
    # Save with appropriate format and quality
    if target_format == 'JPEG':
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output, format=target_format, quality=quality, optimize=True)
    elif target_format == 'PNG':
        img.save(output, format=target_format, optimize=True)
    
    # Get the processed image as bytes
    output.seek(0)
    processed_image = ContentFile(output.read())
    
    # Generate filename and path
    if not entity_type:
        entity_type = 'misc'
    if not entity_id:
        entity_id = 'temp'
        
    filename = generate_filename(entity_type, entity_id, image_type, image_file.name)
    path = generate_image_path(entity_type, entity_id, image_type, filename)
    
    # Create high-res version for logos if needed
    high_res_image = None
    high_res_path = None
    if image_type == 'logo' and 'high_res_size' in specs:
        high_res_img = Image.open(image_file)
        high_res_img = strip_exif_data(high_res_img)
        high_res_img = high_res_img.resize(specs['high_res_size'], Image.LANCZOS)
        
        high_res_output = BytesIO()
        high_res_img.save(high_res_output, format=target_format, optimize=True)
        high_res_output.seek(0)
        high_res_image = ContentFile(high_res_output.read())
        
        high_res_filename = f"highres_{filename}"
        high_res_path = generate_image_path(entity_type, entity_id, image_type, high_res_filename)
    
    # Create thumbnail version
    thumbnail_img = img.copy()
    thumbnail_specs = IMAGE_SPECS['thumbnail']
    thumbnail_img = thumbnail_img.resize(thumbnail_specs['size'], Image.LANCZOS)
    
    thumbnail_output = BytesIO()
    if target_format == 'JPEG':
        thumbnail_img.save(thumbnail_output, format=target_format, quality=thumbnail_specs['quality'], optimize=True)
    else:
        thumbnail_img.save(thumbnail_output, format=target_format, optimize=True)
    
    thumbnail_output.seek(0)
    thumbnail_image = ContentFile(thumbnail_output.read())
    thumbnail_filename = f"thumb_{filename}"
    thumbnail_path = generate_image_path(entity_type, entity_id, image_type, thumbnail_filename)
    
    # Collect metadata
    metadata = {
        'original_filename': image_file.name,
        'original_size': image_file.size,
        'processed_size': processed_image.size,
        'width': target_size[0],
        'height': target_size[1],
        'format': target_format,
        'content_type': f'image/{target_format.lower()}',
    }
    
    result = {
        'image': processed_image,
        'path': path,
        'filename': filename,
        'thumbnail': {
            'image': thumbnail_image,
            'path': thumbnail_path,
            'filename': thumbnail_filename,
        },
        'metadata': metadata,
    }
    
    if high_res_image:
        result['high_res'] = {
            'image': high_res_image,
            'path': high_res_path,
            'filename': high_res_filename,
        }
    
    return result
