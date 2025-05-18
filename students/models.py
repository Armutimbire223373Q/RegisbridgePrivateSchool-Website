from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ], default='O')
    address = models.TextField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ])
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date}"

class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE)
    term = models.CharField(max_length=20, choices=[
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term')
    ], default='first')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    date = models.DateField(auto_now_add=True)
    teacher_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.term}"
