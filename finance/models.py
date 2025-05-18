from django.db import models
from school.models import Student

# Create your models here.

class FeeStructure(models.Model):
    class_name = models.CharField(max_length=100)
    term = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    amount = models.FloatField()

class Discount(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.FloatField()

class Scholarship(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    amount = models.FloatField()
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20)

class Expense(models.Model):
    category = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.FloatField()
    date = models.DateField()
