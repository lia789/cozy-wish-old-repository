from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import CartItem, Booking, ServiceAvailability


class AddToCartForm(forms.ModelForm):
    """Form for adding a service to the cart"""

    class Meta:
        model = CartItem
        fields = ['date', 'time_slot', 'quantity']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat(),
                'max': (timezone.now().date() + timedelta(days=30)).isoformat(),
            }),
            'time_slot': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
        }

    def __init__(self, service=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        quantity = cleaned_data.get('quantity')

        if not all([date, time_slot, quantity]):
            return cleaned_data

        # Check if date is in the future
        if date < timezone.now().date():
            raise forms.ValidationError("You cannot book a service in the past.")

        # Check if service is available for the selected date and time
        try:
            availability = ServiceAvailability.objects.get(
                service=self.service,
                date=date,
                time_slot=time_slot
            )

            if availability.is_fully_booked():
                raise forms.ValidationError("This service is fully booked for the selected date and time.")

            if availability.current_bookings + quantity > availability.max_bookings:
                raise forms.ValidationError(f"Only {availability.max_bookings - availability.current_bookings} slots available for this time.")

        except ServiceAvailability.DoesNotExist:
            # If no availability record exists, create one
            ServiceAvailability.objects.create(
                service=self.service,
                date=date,
                time_slot=time_slot,
                max_bookings=10,  # Default max bookings
                current_bookings=0,
                is_available=True
            )

        return cleaned_data


class UpdateCartItemForm(forms.ModelForm):
    """Form for updating a cart item"""

    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
        }

    def clean_quantity(self):
        """Validate the quantity field"""
        quantity = self.cleaned_data.get('quantity')

        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")

        if quantity > 5:
            raise forms.ValidationError("Quantity cannot exceed 5.")

        return quantity


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""

    class Meta:
        model = Booking
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or notes for the service provider?',
            }),
        }


class BookingCancellationForm(forms.Form):
    """Form for cancelling a booking"""

    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide a reason for cancellation',
        }),
        required=False
    )


class ServiceAvailabilityForm(forms.ModelForm):
    """Form for managing service availability"""

    class Meta:
        model = ServiceAvailability
        fields = ['date', 'time_slot', 'max_bookings', 'is_available']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat(),
            }),
            'time_slot': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'max_bookings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')

        # Check if date is in the future
        if date and date < timezone.now().date():
            raise forms.ValidationError("You cannot set availability for a past date.")

        return cleaned_data


class DateRangeAvailabilityForm(forms.Form):
    """Form for setting availability for a date range"""

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat(),
        })
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat(),
        })
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
        })
    )

    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
        })
    )

    interval = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 15,
            'max': 120,
            'step': 15,
        }),
        help_text="Time interval in minutes (e.g., 30 for half-hour slots)",
        initial=60
    )

    max_bookings = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 10,
        }),
        initial=1
    )

    is_available = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        required=False,
        initial=True
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not all([start_date, end_date, start_time, end_time]):
            return cleaned_data

        # Check if dates are in the future
        if start_date < timezone.now().date():
            raise forms.ValidationError("Start date cannot be in the past.")

        # Check if end date is after start date
        if end_date < start_date:
            raise forms.ValidationError("End date must be after start date.")

        # Check if end time is after start time
        if end_time <= start_time:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data
