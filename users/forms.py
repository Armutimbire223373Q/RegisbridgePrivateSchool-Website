from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User


class UserProfileForm(UserChangeForm):
    """Form for editing user profile"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields more user-friendly
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-input", "placeholder": "Enter your first name"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-input", "placeholder": "Enter your last name"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-input", "placeholder": "Enter your email address"}
        )
