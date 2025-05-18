from django.db import models
from django.conf import settings
from school.models import Student

# Create your models here.

class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50)  # e.g., Android, iOS
    push_token = models.CharField(max_length=255)

class PushNotification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)

class QRCheckIn(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
