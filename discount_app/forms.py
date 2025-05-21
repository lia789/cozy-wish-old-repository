from django import forms
from django.utils import timezone
from .models import VenueDiscount, ServiceDiscount, PlatformDiscount
from venues_app.models import Venue, Service, Category


class DiscountBaseForm(forms.ModelForm):
    """Base form for all discount types"""
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="When the discount will start"
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="When the discount will end"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate start_date is not in the past
        if start_date and start_date < timezone.now():
            self.add_error('start_date', "Start date cannot be in the past.")
        
        # Validate end_date is after start_date
        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', "End date must be after start date.")
        
        # Validate discount_value based on discount_type
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        
        if discount_type == 'percentage' and discount_value:
            if discount_value > 100:
                self.add_error('discount_value', "Percentage discount cannot exceed 100%.")
        
        return cleaned_data


class VenueDiscountForm(DiscountBaseForm):
    """Form for venue-wide discounts"""
    class Meta:
        model = VenueDiscount
        fields = [
            'name', 'description', 'discount_type', 'discount_value',
            'start_date', 'end_date', 'min_booking_value', 'max_discount_amount'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is a service provider, limit venues to those owned by the user
        if self.user and hasattr(self, 'instance') and not self.instance.pk:
            self.fields['venue'] = forms.ModelChoiceField(
                queryset=Venue.objects.filter(owner=self.user, approval_status='approved'),
                empty_label="Select a venue"
            )


class ServiceDiscountForm(DiscountBaseForm):
    """Form for service-specific discounts"""
    class Meta:
        model = ServiceDiscount
        fields = [
            'name', 'description', 'discount_type', 'discount_value',
            'start_date', 'end_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.venue = kwargs.pop('venue', None)
        super().__init__(*args, **kwargs)
        
        # If venue is provided, limit services to those belonging to the venue
        if self.venue:
            self.fields['service'] = forms.ModelChoiceField(
                queryset=Service.objects.filter(venue=self.venue, is_active=True),
                empty_label="Select a service"
            )
        # If user is a service provider, limit services to those from venues owned by the user
        elif self.user and hasattr(self, 'instance') and not self.instance.pk:
            venues = Venue.objects.filter(owner=self.user, approval_status='approved')
            self.fields['service'] = forms.ModelChoiceField(
                queryset=Service.objects.filter(venue__in=venues, is_active=True),
                empty_label="Select a service"
            )


class PlatformDiscountForm(DiscountBaseForm):
    """Form for platform-wide discounts (admin only)"""
    class Meta:
        model = PlatformDiscount
        fields = [
            'name', 'description', 'discount_type', 'discount_value',
            'start_date', 'end_date', 'category', 'min_booking_value',
            'max_discount_amount', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = "All Categories"
        self.fields['category'].required = False


class DiscountApprovalForm(forms.Form):
    """Form for approving or rejecting discounts"""
    APPROVAL_CHOICES = [
        (True, 'Approve'),
        (False, 'Reject')
    ]
    
    is_approved = forms.ChoiceField(
        choices=APPROVAL_CHOICES,
        widget=forms.RadioSelect,
        label="Approval Decision"
    )
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Reason for Rejection (if applicable)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        is_approved = cleaned_data.get('is_approved')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        # Convert string to boolean
        is_approved = is_approved == 'True'
        cleaned_data['is_approved'] = is_approved
        
        # If rejecting, require a reason
        if not is_approved and not rejection_reason:
            self.add_error('rejection_reason', "Please provide a reason for rejection.")
        
        return cleaned_data


class DiscountFilterForm(forms.Form):
    """Form for filtering discounts"""
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('active', 'Active'),
        ('scheduled', 'Scheduled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ]
    
    TYPE_CHOICES = [
        ('', 'All Types'),
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    discount_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_value = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Value'})
    )
    
    max_value = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Value'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search discounts...'})
    )
