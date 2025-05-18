from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class HomePageContent(models.Model):
    """Model for managing home page content."""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    hero_image = models.ImageField(upload_to='home/', blank=True)
    hero_text = models.TextField()
    about_section = models.TextField()
    mission_statement = models.TextField()
    vision_statement = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Home Page Content'
        verbose_name_plural = 'Home Page Content'

    def __str__(self):
        return 'Home Page Content'

class NewsItem(models.Model):
    """Model for managing news items on the home page."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_posted']
        verbose_name = 'News Item'
        verbose_name_plural = 'News Items'

    def __str__(self):
        return self.title

class Event(models.Model):
    """Model for managing events on the home page."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('announcement', 'Announcement'),
        ('event', 'Event'),
        ('assignment', 'Assignment'),
        ('grade', 'Grade'),
        ('attendance', 'Attendance'),
        ('message', 'Message'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False 