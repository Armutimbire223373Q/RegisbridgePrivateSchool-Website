from django.db import models
from django.conf import settings
from school.models import Student

# Create your models here.

class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    subject = models.CharField(max_length=100)
    class_group = models.CharField(max_length=100)

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    subject = models.CharField(max_length=100)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)

class MCQ(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)
    subject = models.CharField(max_length=100)

class MCQSubmission(models.Model):
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField()
