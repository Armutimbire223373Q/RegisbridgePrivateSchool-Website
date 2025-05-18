from django.db import models
from school.models import Student

# Create your models here.

class MedicalRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class IncidentReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    incident_date = models.DateField()
    description = models.TextField()
    reported_by = models.CharField(max_length=100)

class Vaccination(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    date_administered = models.DateField()

class CovidScreening(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    screening_date = models.DateField()
    symptoms = models.TextField()
    result = models.CharField(max_length=20)
