from django import forms
from django.core.exceptions import ValidationError
from .image_utils import (
    validate_image_extension, 
    validate_image_size, 
    process_image,
    IMAGE_SPECS
)


class ImageUploadForm(forms.Form):
    """Base form for image uploads with validation and processing"""
    
    image = forms.ImageField(
        label="Image",
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    image_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    entity_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    entity_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        self.image_type = kwargs.pop('image_type', 'profile')
        self.entity_type = kwargs.pop('entity_type', None)
        self.entity_id = kwargs.pop('entity_id', None)
        super().__init__(*args, **kwargs)
        
        # Set initial values
        self.fields['image_type'].initial = self.image_type
        self.fields['entity_type'].initial = self.entity_type
        self.fields['entity_id'].initial = self.entity_id
        
        # Update help text based on image type
        specs = IMAGE_SPECS.get(self.image_type, {})
        if specs:
            size_text = f"{specs['size'][0]}x{specs['size'][1]}px"
            format_text = specs['format']
            max_size_kb = specs['max_file_size'] // 1024
            
            self.fields['image'].help_text = (
                f"Recommended format: {format_text}, "
                f"Size: {size_text}, "
                f"Maximum file size: {max_size_kb}KB"
            )
    
    def clean_image(self):
        """Validate the uploaded image"""
        image = self.cleaned_data.get('image')
        if not image:
            return None
        
        image_type = self.cleaned_data.get('image_type') or self.image_type
        
        # Validate extension
        validate_image_extension(image.name, image_type)
        
        # Validate size
        max_size = IMAGE_SPECS[image_type]['max_file_size'] // 1024  # Convert to KB
        validate_image_size(image, max_size)
        
        return image
    
    def process(self):
        """Process the image according to specifications"""
        if not self.is_valid():
            raise ValidationError("Form is not valid")
        
        image = self.cleaned_data.get('image')
        image_type = self.cleaned_data.get('image_type') or self.image_type
        entity_type = self.cleaned_data.get('entity_type') or self.entity_type
        entity_id = self.cleaned_data.get('entity_id') or self.entity_id
        
        if not image:
            return None
        
        # Process the image
        return process_image(
            image_file=image,
            image_type=image_type,
            entity_type=entity_type,
            entity_id=entity_id
        )


class ProfileImageForm(ImageUploadForm):
    """Form for uploading profile images"""
    
    def __init__(self, *args, **kwargs):
        kwargs['image_type'] = 'profile'
        super().__init__(*args, **kwargs)


class LogoImageForm(ImageUploadForm):
    """Form for uploading business logos"""
    
    def __init__(self, *args, **kwargs):
        kwargs['image_type'] = 'logo'
        super().__init__(*args, **kwargs)


class VenueImageForm(ImageUploadForm):
    """Form for uploading venue images"""
    
    def __init__(self, *args, **kwargs):
        kwargs['image_type'] = 'venue'
        super().__init__(*args, **kwargs)
        
    caption = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
