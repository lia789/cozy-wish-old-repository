from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)
from utils.forms import ImageUploadForm
from utils.image_service import ImageService


class PageForm(forms.ModelForm):
    """Form for creating and updating pages"""

    class Meta:
        model = Page
        fields = ['title', 'content', 'meta_description', 'meta_keywords', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if self.instance.pk is None:  # New page
            slug = slugify(title)
            if Page.objects.filter(slug=slug).exists():
                raise forms.ValidationError("A page with this title already exists. Please choose a different title.")
        return title


class BlogCategoryForm(forms.ModelForm):
    """Form for creating and updating blog categories"""

    class Meta:
        model = BlogCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.pk is None:  # New category
            slug = slugify(name)
            if BlogCategory.objects.filter(slug=slug).exists():
                raise forms.ValidationError("A category with this name already exists. Please choose a different name.")
        return name


class BlogPostForm(forms.ModelForm):
    """Form for creating and updating blog posts"""

    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'featured_image', 'categories',
            'meta_description', 'meta_keywords', 'status', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if self.instance.pk is None:  # New post
            slug = slugify(title)
            if BlogPost.objects.filter(slug=slug).exists():
                raise forms.ValidationError("A blog post with this title already exists. Please choose a different title.")
        return title

    def clean_featured_image(self):
        """Process and validate the featured image"""
        featured_image = self.cleaned_data.get('featured_image')
        if not featured_image:
            return None

        # Create an ImageUploadForm to validate the image
        image_form = ImageUploadForm(
            files={'image': featured_image},
            image_type='venue',  # Use venue type for blog images (larger, landscape format)
            entity_type='blog',
            entity_id=self.instance.id if self.instance and self.instance.id else None
        )

        if not image_form.is_valid():
            raise ValidationError(f"Image validation failed: {image_form.errors.get('image', 'Invalid image')}")

        return featured_image

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Adjust status choices based on user role
        if self.user and not self.user.is_staff:
            # Service providers can only submit for approval or save as draft
            self.fields['status'].choices = [
                ('draft', 'Draft'),
                ('pending', 'Submit for Approval')
            ]

    def save(self, commit=True):
        """Override save to process the featured image"""
        blog_post = super().save(commit=False)

        # Process the featured image if provided
        featured_image = self.cleaned_data.get('featured_image')
        if featured_image:
            # Create an ImageUploadForm to process the image
            image_form = ImageUploadForm(
                files={'image': featured_image},
                image_type='venue',  # Use venue type for blog images (larger, landscape format)
                entity_type='blog',
                entity_id=blog_post.id if blog_post.id else None
            )

            if image_form.is_valid():
                # Process the image
                processed_data = image_form.process()

                # Save the processed image
                image_path, metadata = ImageService.save_image(
                    processed_data,
                    user=self.user
                )

                # Update the featured image field with the processed image path
                blog_post.featured_image = image_path

        if commit:
            blog_post.save()
            self.save_m2m()

        return blog_post


class BlogCommentForm(forms.ModelForm):
    """Form for creating blog comments"""

    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MediaUploadForm(forms.ModelForm):
    """Form for uploading media"""

    class Meta:
        model = MediaItem
        fields = ['title', 'file', 'file_type', 'description', 'alt_text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_file(self):
        """Process and validate the file if it's an image"""
        file = self.cleaned_data.get('file')
        if not file:
            return None

        file_type = self.cleaned_data.get('file_type')

        # Only process images
        if file_type == 'image':
            # Determine the image type based on usage
            image_type = 'profile'  # Default
            if 'logo' in self.cleaned_data.get('title', '').lower() or 'logo' in self.cleaned_data.get('description', '').lower():
                image_type = 'logo'
            elif 'venue' in self.cleaned_data.get('title', '').lower() or 'venue' in self.cleaned_data.get('description', '').lower():
                image_type = 'venue'

            # Create an ImageUploadForm to validate the image
            image_form = ImageUploadForm(
                files={'image': file},
                image_type=image_type,
                entity_type='media',
                entity_id=self.instance.id if self.instance and self.instance.id else None
            )

            if not image_form.is_valid():
                raise ValidationError(f"Image validation failed: {image_form.errors.get('image', 'Invalid image')}")

        return file

    def save(self, commit=True):
        """Override save to process images"""
        media_item = super().save(commit=False)

        # Set the uploaded_by if provided
        if self.user and not media_item.uploaded_by:
            media_item.uploaded_by = self.user

        # Process the file if it's an image
        file = self.cleaned_data.get('file')
        file_type = self.cleaned_data.get('file_type')

        if file and file_type == 'image':
            # Determine the image type based on usage
            image_type = 'profile'  # Default
            if 'logo' in self.cleaned_data.get('title', '').lower() or 'logo' in self.cleaned_data.get('description', '').lower():
                image_type = 'logo'
            elif 'venue' in self.cleaned_data.get('title', '').lower() or 'venue' in self.cleaned_data.get('description', '').lower():
                image_type = 'venue'

            # Create an ImageUploadForm to process the image
            image_form = ImageUploadForm(
                files={'image': file},
                image_type=image_type,
                entity_type='media',
                entity_id=media_item.id if media_item.id else None
            )

            if image_form.is_valid():
                # Process the image
                processed_data = image_form.process()

                # Save the processed image
                image_path, metadata = ImageService.save_image(
                    processed_data,
                    user=media_item.uploaded_by
                )

                # Update the file field with the processed image path
                media_item.file = image_path

        if commit:
            media_item.save()

        return media_item


class SiteConfigurationForm(forms.ModelForm):
    """Form for configuring site settings"""

    class Meta:
        model = SiteConfiguration
        fields = [
            'site_name', 'site_description', 'contact_email', 'contact_phone', 'contact_address',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url',
            'google_analytics_id', 'default_meta_description', 'default_meta_keywords',
            'maintenance_mode', 'maintenance_message'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'google_analytics_id': forms.TextInput(attrs={'class': 'form-control'}),
            'default_meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'default_meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AnnouncementForm(forms.ModelForm):
    """Form for creating and updating announcements"""

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'announcement_type', 'is_active', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'announcement_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")

        return cleaned_data


class SearchForm(forms.Form):
    """Form for searching content"""

    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )
