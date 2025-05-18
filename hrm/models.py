from django.db import models
from django.conf import settings

# Create your models here.

class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    contract_file = models.FileField(upload_to='staff_contracts/', blank=True, null=True)
    documents = models.FileField(upload_to='staff_documents/', blank=True, null=True)

class Payroll(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.FloatField()
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)

class LeaveRequest(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

class PerformanceReview(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    review_date = models.DateField()
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviews_given')
    comments = models.TextField()
    score = models.IntegerField()
