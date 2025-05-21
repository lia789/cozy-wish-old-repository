from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Review, ReviewResponse, ReviewFlag


class ReviewForm(forms.ModelForm):
    """Form for submitting and editing reviews"""
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'step': '1'
            }
        ),
        help_text="Rate from 1 to 5 stars"
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Share your experience with this venue...'
            }
        )
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def clean_rating(self):
        """Validate rating is between 1 and 5"""
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5 stars")
        return rating


class StarRatingForm(ReviewForm):
    """Form with star rating widget"""
    
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'id': 'star-rating-input'})


class ReviewResponseForm(forms.ModelForm):
    """Form for responding to reviews"""
    
    response_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Respond to this review...'
            }
        )
    )
    
    class Meta:
        model = ReviewResponse
        fields = ['response_text']


class ReviewFlagForm(forms.ModelForm):
    """Form for flagging inappropriate reviews"""
    
    reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Please explain why this review is inappropriate...'
            }
        )
    )
    
    class Meta:
        model = ReviewFlag
        fields = ['reason']


class AdminReviewForm(forms.ModelForm):
    """Form for admin to edit reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'is_approved', 'is_flagged']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_flagged': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
