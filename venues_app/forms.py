from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Venue, Service, VenueImage, OpeningHours, FAQ, TeamMember, Review, USCity
from utils.forms import VenueImageForm as BaseVenueImageForm, ProfileImageForm
from utils.image_service import ImageService


class VenueSearchForm(forms.Form):
    """Form for searching venues"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input form-control ps-5',
            'placeholder': 'Search venues, services, or categories...',
            'autocomplete': 'off',
            'data-bs-toggle': 'dropdown',
            'aria-expanded': 'false',
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input form-control ps-5',
            'placeholder': 'City, State, or County',
            'autocomplete': 'off',
            'data-bs-toggle': 'dropdown',
            'aria-expanded': 'false',
            'list': 'locationList',
        })
    )
    category = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def get_location_suggestions(self, query):
        """Get location suggestions based on the query"""
        if not query or len(query) < 2:
            return []

        # Search for cities, states, and counties that match the query
        locations = USCity.objects.filter(
            Q(city__icontains=query) |
            Q(state_name__icontains=query) |
            Q(county_name__icontains=query)
        ).distinct().order_by('state_name', 'city')[:10]

        # Format the results
        suggestions = []
        for location in locations:
            suggestions.append({
                'id': location.id,
                'text': f"{location.city}, {location.state_id}",
                'city': location.city,
                'state': location.state_name,
                'county': location.county_name,
                'state_id': location.state_id,
            })

        return suggestions


class VenueFilterForm(forms.Form):
    """Form for filtering venues"""
    SORT_CHOICES = [
        ('', 'Sort by'),
        ('rating_high', 'Rating: High to Low'),
        ('rating_low', 'Rating: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('price_low', 'Price: Low to High'),
        ('discount', 'Discount: High to Low'),
    ]

    VENUE_TYPE_CHOICES = [
        ('', 'All Types'),
        ('all', 'All Genders'),
        ('male', 'Male Only'),
        ('female', 'Female Only'),
    ]

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    venue_type = forms.ChoiceField(
        choices=VENUE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    has_discount = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    county = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def get_states(self):
        """Get list of states for filtering"""
        return USCity.objects.values_list('state_name', flat=True).distinct().order_by('state_name')

    def get_counties(self, state=None):
        """Get list of counties for filtering"""
        counties = USCity.objects.values_list('county_name', flat=True)
        if state:
            counties = counties.filter(state_name__iexact=state)
        return counties.distinct().order_by('county_name')

    def get_cities(self, state=None, county=None):
        """Get list of cities for filtering"""
        cities = USCity.objects.values_list('city', flat=True)
        if state:
            cities = cities.filter(state_name__iexact=state)
        if county:
            cities = cities.filter(county_name__iexact=county)
        return cities.distinct().order_by('city')


class VenueForm(forms.ModelForm):
    """Form for creating and updating venues"""
    # Add a field for selecting US city from dropdown
    us_city_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    # Add separate tag input fields
    tag_input_1 = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag 1'})
    )
    tag_input_2 = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag 2'})
    )
    tag_input_3 = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag 3'})
    )
    tag_input_4 = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag 4'})
    )
    tag_input_5 = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag 5'})
    )

    class Meta:
        model = Venue
        fields = [
            'name', 'category', 'venue_type', 'state', 'county', 'city',
            'street_number', 'street_name', 'about'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter venue name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'venue_type': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state',
                'autocomplete': 'off'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter county',
                'autocomplete': 'off'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city',
                'autocomplete': 'off'
            }),
            'street_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter street number'}),
            'street_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter street name'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your venue'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mark required fields
        self.fields['name'].required = True
        self.fields['category'].required = True
        self.fields['state'].required = True
        self.fields['county'].required = True
        self.fields['city'].required = True
        self.fields['street_number'].required = True
        self.fields['street_name'].required = True
        self.fields['about'].required = True

        # If we have an instance, populate the tag input fields
        if self.instance and self.instance.pk:
            tags = self.instance.tags.all()
            for i, tag in enumerate(tags[:5]):
                field_name = f'tag_input_{i+1}'
                if field_name in self.fields:
                    self.fields[field_name].initial = tag.name

    def clean(self):
        cleaned_data = super().clean()

        # Validate required fields
        required_fields = ['name', 'category', 'state', 'county', 'city', 'street_number', 'street_name', 'about']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f'{field.replace("_", " ").title()} is required')

        # Process tag input fields
        tag_inputs = []
        for i in range(1, 6):
            tag_value = cleaned_data.get(f'tag_input_{i}')
            if tag_value and tag_value.strip():
                tag_inputs.append(tag_value.strip())

        # Store tag inputs for processing in save method
        self.tag_inputs = tag_inputs

        return cleaned_data

    def save(self, commit=True):
        venue = super().save(commit=False)

        # Try to link to a US city if us_city_id is provided
        us_city_id = self.cleaned_data.get('us_city_id')
        if us_city_id:
            try:
                venue.us_city = USCity.objects.get(id=us_city_id)
                # Update coordinates from the city
                venue.latitude = venue.us_city.latitude
                venue.longitude = venue.us_city.longitude
            except (USCity.DoesNotExist, ValueError):
                pass

        if commit:
            venue.save()

            # Clear existing tags if this is an update
            if venue.pk:
                venue.tags.clear()

            # Process tag inputs
            if hasattr(self, 'tag_inputs') and self.tag_inputs:
                from django.utils.text import slugify
                from .models import Tag

                for tag_name in self.tag_inputs:
                    if tag_name:
                        # Create the tag if it doesn't exist
                        tag, created = Tag.objects.get_or_create(
                            name=tag_name,
                            defaults={'slug': slugify(tag_name)}
                        )
                        # Add the tag to the venue
                        venue.tags.add(tag)

        return venue


class VenueImageForm(forms.ModelForm):
    """Form for venue images"""
    class Meta:
        model = VenueImage
        fields = ['image', 'image_order', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        """Process and validate the venue image"""
        image = self.cleaned_data.get('image')
        if not image:
            return None

        # Get the venue ID if this is an existing image
        venue_id = None
        if self.instance and hasattr(self.instance, 'venue') and self.instance.venue:
            venue_id = self.instance.venue.id

        # Create a VenueImageForm to validate and process the image
        image_form = BaseVenueImageForm(
            files={'image': image},
            data={'caption': self.cleaned_data.get('caption', '')},
            entity_type='venues',
            entity_id=venue_id
        )

        if not image_form.is_valid():
            raise ValidationError(image_form.errors['image'])

        return image

    def save(self, commit=True):
        """Override save to process the venue image"""
        venue_image = super().save(commit=False)

        # Process the image if provided
        image = self.cleaned_data.get('image')
        if image and hasattr(venue_image, 'venue') and venue_image.venue:
            # Create a VenueImageForm to process the image
            image_form = BaseVenueImageForm(
                files={'image': image},
                data={'caption': self.cleaned_data.get('caption', '')},
                entity_type='venues',
                entity_id=venue_image.venue.id
            )

            if image_form.is_valid():
                # Process the image
                processed_data = image_form.process()

                # Save the processed image
                image_path, metadata = ImageService.save_image(
                    processed_data,
                    user=venue_image.venue.owner
                )

                # Update the image field with the processed image path
                venue_image.image = image_path

        if commit:
            venue_image.save()

        return venue_image


class OpeningHoursForm(forms.ModelForm):
    """Form for venue opening hours"""
    class Meta:
        model = OpeningHours
        fields = ['day', 'open_time', 'close_time', 'is_closed']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'open_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        open_time = cleaned_data.get('open_time')
        close_time = cleaned_data.get('close_time')
        is_closed = cleaned_data.get('is_closed')

        if not is_closed and open_time and close_time and open_time >= close_time:
            raise ValidationError("Closing time must be after opening time")

        return cleaned_data


class FAQForm(forms.ModelForm):
    """Form for venue FAQs"""
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'order']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ServiceForm(forms.ModelForm):
    """Form for venue services"""
    class Meta:
        model = Service
        fields = ['title', 'short_description', 'price', 'discounted_price', 'duration', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discounted_price = cleaned_data.get('discounted_price')

        if discounted_price is not None and discounted_price >= price:
            raise ValidationError("Discounted price must be less than the regular price")

        return cleaned_data


class TeamMemberForm(forms.ModelForm):
    """Form for venue team members"""
    class Meta:
        model = TeamMember
        fields = ['venue', 'name', 'profile_image', 'title', 'bio', 'is_active']
        widgets = {
            'venue': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        title = cleaned_data.get('title')

        if not name:
            self.add_error('name', 'Name is required')

        if not title:
            self.add_error('title', 'Title is required')

        return cleaned_data

    def clean_profile_image(self):
        """Process and validate the profile image"""
        profile_image = self.cleaned_data.get('profile_image')
        if not profile_image:
            return None

        # Get the venue ID if this is an existing team member
        venue_id = None
        if self.instance and hasattr(self.instance, 'venue') and self.instance.venue:
            venue_id = self.instance.venue.id

        # Create a ProfileImageForm to validate and process the image
        image_form = ProfileImageForm(
            files={'image': profile_image},
            entity_type='venues',
            entity_id=venue_id
        )

        if not image_form.is_valid():
            raise ValidationError(image_form.errors['image'])

        return profile_image

    def save(self, commit=True):
        """Override save to process the profile image"""
        team_member = super().save(commit=False)

        # Process the profile image if provided
        profile_image = self.cleaned_data.get('profile_image')
        if profile_image and hasattr(team_member, 'venue') and team_member.venue:
            # Create a ProfileImageForm to process the image
            image_form = ProfileImageForm(
                files={'image': profile_image},
                entity_type='venues',
                entity_id=team_member.venue.id
            )

            if image_form.is_valid():
                # Process the image
                processed_data = image_form.process()

                # Save the processed image
                image_path, metadata = ImageService.save_image(
                    processed_data,
                    user=team_member.venue.owner
                )

                # Update the profile image field with the processed image path
                team_member.profile_image = image_path

        if commit:
            team_member.save()

        return team_member


class ReviewForm(forms.ModelForm):
    """Form for venue reviews"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
        return rating
