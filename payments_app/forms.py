from django import forms
from django.utils import timezone
from .models import PaymentMethod, Transaction


class PaymentMethodForm(forms.ModelForm):
    """Form for creating and updating payment methods"""
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'name', 'last_four', 'expiry_date', 'is_default']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PaymentForm(forms.Form):
    """Form for processing payments"""
    PAYMENT_METHOD_CHOICES = [
        ('new', 'Use a new payment method'),
        ('saved', 'Use a saved payment method'),
    ]
    
    payment_method_choice = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='new'
    )
    
    # Fields for new payment method
    payment_type = forms.ChoiceField(choices=PaymentMethod.PAYMENT_TYPE_CHOICES, required=False)
    name = forms.CharField(max_length=100, required=False)
    card_number = forms.CharField(max_length=16, required=False)
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    cvv = forms.CharField(max_length=4, required=False)
    save_payment_method = forms.BooleanField(required=False, initial=False)
    
    # Field for saved payment method
    saved_payment_method = forms.ModelChoiceField(queryset=None, required=False)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['saved_payment_method'].queryset = PaymentMethod.objects.filter(user=user)
        else:
            self.fields['saved_payment_method'].queryset = PaymentMethod.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method_choice = cleaned_data.get('payment_method_choice')
        
        if payment_method_choice == 'new':
            # Validate new payment method fields
            payment_type = cleaned_data.get('payment_type')
            name = cleaned_data.get('name')
            card_number = cleaned_data.get('card_number')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')
            
            if not payment_type:
                self.add_error('payment_type', 'This field is required.')
            if not name:
                self.add_error('name', 'This field is required.')
            if not card_number:
                self.add_error('card_number', 'This field is required.')
            elif len(card_number) < 13 or len(card_number) > 16:
                self.add_error('card_number', 'Card number must be between 13 and 16 digits.')
            if not expiry_date:
                self.add_error('expiry_date', 'This field is required.')
            elif expiry_date < timezone.now().date():
                self.add_error('expiry_date', 'Expiry date must be in the future.')
            if not cvv:
                self.add_error('cvv', 'This field is required.')
            elif len(cvv) < 3 or len(cvv) > 4:
                self.add_error('cvv', 'CVV must be 3 or 4 digits.')
        
        elif payment_method_choice == 'saved':
            # Validate saved payment method field
            saved_payment_method = cleaned_data.get('saved_payment_method')
            if not saved_payment_method:
                self.add_error('saved_payment_method', 'This field is required.')
        
        return cleaned_data


class RefundForm(forms.ModelForm):
    """Form for processing refunds"""
    class Meta:
        model = Transaction
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for refund'}),
        }
