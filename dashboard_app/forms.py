from django import forms
# Dashboard preference forms have been removed as per requirements


class DateRangeForm(forms.Form):
    """Form for selecting date range for dashboard data"""

    PERIOD_CHOICES = [
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('this_week', 'This Week'),
        ('last_week', 'Last Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_year', 'This Year'),
        ('last_year', 'Last Year'),
        ('custom', 'Custom Range'),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        initial='this_month'
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if period == 'custom' and (not start_date or not end_date):
            raise forms.ValidationError("Both start date and end date are required for custom range.")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")

        return cleaned_data
