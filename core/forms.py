from django import forms
from .models import HomePageContent, NewsItem, Event

class HomePageContentForm(forms.ModelForm):
    class Meta:
        model = HomePageContent
        fields = [
            'title', 'subtitle', 'hero_image', 'hero_text',
            'about_section', 'mission_statement', 'vision_statement',
            'contact_email', 'contact_phone', 'address',
            'facebook_url', 'twitter_url', 'instagram_url', 'youtube_url'
        ]
        widgets = {
            'hero_text': forms.Textarea(attrs={'rows': 4}),
            'about_section': forms.Textarea(attrs={'rows': 6}),
            'mission_statement': forms.Textarea(attrs={'rows': 4}),
            'vision_statement': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date',
            'location', 'image', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 