from django.db import models
from django.conf import settings
from school.models import Student

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_holiday = models.BooleanField(default=False)
    term = models.CharField(max_length=20, blank=True)

class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
