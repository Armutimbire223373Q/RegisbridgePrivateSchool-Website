from django.db import models
from django.conf import settings

# Create your models here.

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients = models.TextField()  # Comma-separated user IDs or group names

class EmergencyAlert(models.Model):
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    via_sms = models.BooleanField(default=False)
    via_email = models.BooleanField(default=True)

class Feedback(models.Model):
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
