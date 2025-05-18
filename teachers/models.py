from django.db import models
from django.conf import settings

# Create your models here.
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20, unique=True)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    joining_date = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.teacher_id}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Class(models.Model):
    name = models.CharField(max_length=50)
    grade_level = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=9)  # e.g., "2023-2024"
    subjects = models.ManyToManyField(Subject, through='ClassSubject')
    students = models.ManyToManyField('students.StudentProfile', through='ClassStudent')
    
    class Meta:
        unique_together = ['name', 'grade_level', 'section', 'academic_year']
    
    def __str__(self):
        return f"{self.name} - {self.grade_level} {self.section} ({self.academic_year})"

class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    schedule = models.TextField()  # Store as JSON or text
    
    class Meta:
        unique_together = ['class_name', 'subject']
    
    def __str__(self):
        return f"{self.class_name} - {self.subject}"

class ClassStudent(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['class_name', 'student']
    
    def __str__(self):
        return f"{self.student} - {self.class_name}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.class_subject}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='assignments/')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student} - {self.assignment}"

class Schedule(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ['teacher', 'class_group', 'subject', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.subject} - {self.class_group} ({self.day_of_week.title()} {self.start_time.strftime('%I:%M %p')})"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.class_group} ({self.created_at.strftime('%Y-%m-%d')})"
    