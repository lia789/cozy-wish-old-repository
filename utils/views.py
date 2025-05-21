from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

from .forms import ImageUploadForm, ProfileImageForm, LogoImageForm, VenueImageForm
from .image_service import ImageService
from .models import ImageMetadata


@login_required
def image_upload_view(request, image_type='profile', entity_type=None, entity_id=None):
    """Generic view for image uploads with processing"""
    
    # Select the appropriate form based on image type
    form_classes = {
        'profile': ProfileImageForm,
        'logo': LogoImageForm,
        'venue': VenueImageForm,
    }
    
    form_class = form_classes.get(image_type, ImageUploadForm)
    
    if request.method == 'POST':
        form = form_class(
            request.POST, 
            request.FILES,
            image_type=image_type,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        if form.is_valid():
            try:
                # Process the image
                processed_data = form.process()
                
                # Save the processed image
                image_path, metadata = ImageService.save_image(
                    processed_data,
                    user=request.user
                )
                
                # Return success response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'image_url': ImageService.get_image_url(image_path),
                        'thumbnail_url': ImageService.get_thumbnail_url(metadata),
                        'metadata': {
                            'width': metadata.width,
                            'height': metadata.height,
                            'file_size': metadata.file_size_kb,
                            'format': metadata.format,
                        }
                    })
                
                messages.success(request, 'Image uploaded successfully.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
                
            except ValidationError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': str(e),
                    }, status=400)
                
                messages.error(request, f'Error processing image: {e}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                }, status=400)
    else:
        form = form_class(
            image_type=image_type,
            entity_type=entity_type,
            entity_id=entity_id
        )
    
    return render(request, 'utils/image_upload.html', {
        'form': form,
        'image_type': image_type,
        'entity_type': entity_type,
        'entity_id': entity_id,
    })


@login_required
@require_POST
def ajax_image_upload(request):
    """AJAX endpoint for image uploads"""
    image_type = request.POST.get('image_type', 'profile')
    entity_type = request.POST.get('entity_type')
    entity_id = request.POST.get('entity_id')
    
    # Select the appropriate form based on image type
    form_classes = {
        'profile': ProfileImageForm,
        'logo': LogoImageForm,
        'venue': VenueImageForm,
    }
    
    form_class = form_classes.get(image_type, ImageUploadForm)
    
    form = form_class(
        request.POST, 
        request.FILES,
        image_type=image_type,
        entity_type=entity_type,
        entity_id=entity_id
    )
    
    if form.is_valid():
        try:
            # Process the image
            processed_data = form.process()
            
            # Save the processed image
            image_path, metadata = ImageService.save_image(
                processed_data,
                user=request.user
            )
            
            # Return success response
            return JsonResponse({
                'success': True,
                'image_url': ImageService.get_image_url(image_path),
                'thumbnail_url': ImageService.get_thumbnail_url(metadata),
                'metadata': {
                    'width': metadata.width,
                    'height': metadata.height,
                    'file_size': metadata.file_size_kb,
                    'format': metadata.format,
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'errors': str(e),
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)
