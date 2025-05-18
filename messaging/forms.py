from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from .models import Message, MessageThread, Announcement

User = get_user_model()

class MessageThreadForm(forms.ModelForm):
    """Form for creating a new message thread"""
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        help_text='Select one or more recipients'
    )
    initial_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Write your message here'
    )

    class Meta:
        model = MessageThread
        fields = ['subject', 'participants']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Message subject'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude the current user from the participants list
        if 'request' in kwargs:
            self.fields['participants'].queryset = User.objects.exclude(
                pk=kwargs['request'].user.pk
            )

class MessageForm(forms.ModelForm):
    """Form for sending a message in a thread"""
    attachments = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
        )],
        help_text='Allowed file types: PDF, Word, Excel, Images'
    )

    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Type your message here...',
                'class': 'auto-expand'
            })
        }

class AnnouncementForm(forms.ModelForm):
    """Form for creating and editing announcements"""
    class Meta:
        model = Announcement
        fields = [
            'title',
            'body',
            'priority',
            'recipient_group',
            'expires_at',
            'send_email',
            'send_sms',
            'attachment'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Announcement title'}),
            'body': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Announcement content...'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'expires_at': 'Leave empty if the announcement should not expire',
            'send_email': 'Send this announcement via email to recipients',
            'send_sms': 'Send this announcement via SMS to recipients',
            'attachment': 'Attach a file to this announcement (optional)'
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size cannot exceed 10MB.')
        return attachment 