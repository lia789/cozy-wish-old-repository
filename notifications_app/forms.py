from django import forms
from .models import NotificationPreference, NotificationCategory, Notification


class NotificationPreferenceForm(forms.ModelForm):
    """Form for updating notification preferences"""
    class Meta:
        model = NotificationPreference
        fields = ['channel', 'is_enabled']
        widgets = {
            'channel': forms.Select(attrs={'class': 'form-select'}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SystemAnnouncementForm(forms.ModelForm):
    """Form for creating system announcements"""
    expires_in_days = forms.IntegerField(
        min_value=1,
        max_value=30,
        initial=7,
        help_text="Number of days until this announcement expires",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = "Short, descriptive title for the announcement"
        self.fields['message'].help_text = "Detailed message for the announcement"
        self.fields['priority'].help_text = "Priority level affects how the announcement is displayed"


class NotificationCategoryForm(forms.ModelForm):
    """Form for creating and editing notification categories"""
    class Meta:
        model = NotificationCategory
        fields = ['name', 'description', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].help_text = "Font Awesome icon class (e.g., 'fa-bell')"
        self.fields['color'].help_text = "CSS color class or hex code (e.g., 'primary' or '#007bff')"
