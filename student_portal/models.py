from django.db import models
from django.conf import settings
from school.models import Student

# Create your models here.

class DashboardWidget(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    widget_type = models.CharField(max_length=50)
    data = models.JSONField()

class AnnouncementView(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    announcement_id = models.IntegerField()
    viewed_at = models.DateTimeField(auto_now_add=True)

class FeeStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    status = models.CharField(max_length=20)  # e.g., Paid, Unpaid, Partial
    amount_due = models.FloatField()
    amount_paid = models.FloatField()
