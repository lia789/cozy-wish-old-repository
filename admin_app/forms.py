from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts_app.models import ServiceProviderProfile
from venues_app.models import Venue
from .models import AdminTask, SystemConfig, SecurityEvent

User = get_user_model()


class AdminUserCreationForm(UserCreationForm):
    """Form for creating new users in the admin interface"""
    
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    
    is_staff = forms.BooleanField(
        label=_("Staff status"),
        required=False,
        help_text=_("Designates whether the user can log into this admin site."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_superuser = forms.BooleanField(
        label=_("Superuser status"),
        required=False,
        help_text=_("Designates that this user has all permissions without explicitly assigning them."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_customer = forms.BooleanField(
        label=_("Customer status"),
        required=False,
        help_text=_("Designates whether the user is a customer."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_service_provider = forms.BooleanField(
        label=_("Service provider status"),
        required=False,
        help_text=_("Designates whether the user is a service provider."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text=_("The groups this user belongs to. A user will get all permissions granted to each of their groups.")
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_customer', 'is_service_provider', 'groups')


class AdminUserChangeForm(UserChangeForm):
    """Form for updating users in the admin interface"""
    
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        label=_("First name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    is_active = forms.BooleanField(
        label=_("Active"),
        required=False,
        help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_staff = forms.BooleanField(
        label=_("Staff status"),
        required=False,
        help_text=_("Designates whether the user can log into this admin site."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_superuser = forms.BooleanField(
        label=_("Superuser status"),
        required=False,
        help_text=_("Designates that this user has all permissions without explicitly assigning them."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_customer = forms.BooleanField(
        label=_("Customer status"),
        required=False,
        help_text=_("Designates whether the user is a customer."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_service_provider = forms.BooleanField(
        label=_("Service provider status"),
        required=False,
        help_text=_("Designates whether the user is a service provider."),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text=_("The groups this user belongs to. A user will get all permissions granted to each of their groups.")
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_customer', 'is_service_provider', 'groups')


class VenueApprovalForm(forms.Form):
    """Form for approving or rejecting venues"""
    
    APPROVAL_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=APPROVAL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_("Action")
    )
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label=_("Rejection Reason"),
        help_text=_("Required if rejecting the venue.")
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            self.add_error('rejection_reason', _("Please provide a reason for rejection."))
        
        return cleaned_data


class AdminTaskForm(forms.ModelForm):
    """Form for creating and editing admin tasks"""
    
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("Title")
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label=_("Description")
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Assigned To")
    )
    
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=False,
        label=_("Due Date")
    )
    
    priority = forms.ChoiceField(
        choices=AdminTask.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Priority")
    )
    
    status = forms.ChoiceField(
        choices=AdminTask.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Status")
    )
    
    class Meta:
        model = AdminTask
        fields = ('title', 'description', 'assigned_to', 'due_date', 'priority', 'status')


class SystemConfigForm(forms.ModelForm):
    """Form for configuring system settings"""
    
    maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("Maintenance Mode"),
        help_text=_("Enable maintenance mode to prevent users from accessing the site.")
    )
    
    maintenance_message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label=_("Maintenance Message"),
        help_text=_("Message to display during maintenance mode.")
    )
    
    registration_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("Registration Enabled"),
        help_text=_("Allow new users to register.")
    )
    
    max_login_attempts = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        label=_("Max Login Attempts"),
        help_text=_("Maximum number of failed login attempts before account lockout.")
    )
    
    login_lockout_duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        label=_("Login Lockout Duration (minutes)"),
        help_text=_("Duration in minutes for account lockout after max failed login attempts.")
    )
    
    password_expiry_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        label=_("Password Expiry (days)"),
        help_text=_("Number of days after which passwords expire. Set to 0 to disable.")
    )
    
    session_timeout_minutes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
        label=_("Session Timeout (minutes)"),
        help_text=_("Number of minutes of inactivity before a user is logged out.")
    )
    
    enable_two_factor_auth = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("Enable Two-Factor Authentication"),
        help_text=_("Require two-factor authentication for all users.")
    )
    
    class Meta:
        model = SystemConfig
        fields = (
            'maintenance_mode', 'maintenance_message', 'registration_enabled',
            'max_login_attempts', 'login_lockout_duration', 'password_expiry_days',
            'session_timeout_minutes', 'enable_two_factor_auth'
        )


class BulkUserActionForm(forms.Form):
    """Form for performing bulk actions on users"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate Selected Users'),
        ('deactivate', 'Deactivate Selected Users'),
        ('make_staff', 'Make Selected Users Staff'),
        ('remove_staff', 'Remove Staff Status'),
        ('add_to_group', 'Add to Group'),
        ('remove_from_group', 'Remove from Group'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Action")
    )
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Group"),
        help_text=_("Required for group-related actions.")
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        group = cleaned_data.get('group')
        
        if action in ['add_to_group', 'remove_from_group'] and not group:
            self.add_error('group', _("Please select a group for this action."))
        
        return cleaned_data


class SecurityEventResolveForm(forms.ModelForm):
    """Form for resolving security events"""
    
    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True,
        label=_("Resolution Notes"),
        help_text=_("Provide notes on how this security event was resolved.")
    )
    
    class Meta:
        model = SecurityEvent
        fields = ('resolution_notes',)


class DateRangeForm(forms.Form):
    """Form for selecting a date range for reports"""
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_("Start Date")
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_("End Date")
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', _("End date must be after start date."))
        
        return cleaned_data
