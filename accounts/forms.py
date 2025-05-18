from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'date_of_birth', 
                 'phone_number', 'address', 'profile_picture')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email address must be unique.'))
        return email


class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    
    password = None  # Remove password field from the form
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'date_of_birth',
                 'phone_number', 'address', 'profile_picture')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'date_of_birth',
                 'phone_number', 'address', 'profile_picture')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EmailVerificationForm(forms.Form):
    """Form for email verification code."""
    
    code = forms.CharField(
        label=_('Verification Code'),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter 6-digit code')
        })
    )
