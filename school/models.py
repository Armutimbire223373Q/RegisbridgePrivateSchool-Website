from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MinLengthValidator, FileExtensionValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=10)
    section = models.CharField(max_length=5)
    date_of_birth = models.DateField()
    parent = models.ForeignKey('ParentProfile', on_delete=models.SET_NULL, null=True, related_name='children')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.grade}{self.section}"

class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    occupation = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name()

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    joining_date = models.DateField()

    def __str__(self):
        return self.user.get_full_name()

class LeadershipMember(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    bio = models.TextField()
    photo = models.ImageField(upload_to='leadership/')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.position}"

class TuitionFee(models.Model):
    GRADE_CHOICES = [
        ('pre-school', 'Pre-School'),
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('high', 'High School'),
    ]
    
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['grade']
        
    def __str__(self):
        return f"{self.get_grade_display()} - ${self.amount}"

class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    requirements = models.TextField()
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['deadline']
        
    def __str__(self):
        return self.name

class ImportantDate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['date']
        
    def __str__(self):
        return f"{self.title} - {self.date}"

def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))

def get_upload_path(instance, filename):
    return os.path.join('hostel', str(instance.id), filename)

class HostelFacility(models.Model):
    """Model for hostel facilities and amenities."""
    name = models.CharField(max_length=100)
    description = models.TextField(validators=[MinLengthValidator(10)])
    image = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ]
    )
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Hostel Facility')
        verbose_name_plural = _('Hostel Facilities')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.order < 0:
            raise ValidationError(_("Order must be a positive number."))

class StudentService(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

class ParentResource(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='parent_resources/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class PrivacyPolicy(models.Model):
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Privacy Policy - {self.last_updated}"

# Academic Models
class AcademicYear(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} - {self.section}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

# User Profile Models
class Student(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    current_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True)
    date_admitted = models.DateField(auto_now_add=True)
    guardian = models.ForeignKey('ParentProfile', on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['admission_number']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    qualification = models.CharField(max_length=100)
    date_joined = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name()

# Academic Records
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    reason = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['student', 'date']

class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('exam', 'Examination'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='school_assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    description = models.TextField(blank=True)
    date = models.DateField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                               help_text="Weight of this assessment in the final grade calculation")
    
    class Meta:
        ordering = ['-date', 'subject']
        
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_assessment_type_display()})"

class Grade(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    assessment = models.ForeignKey('Assessment', on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=2)
    comments = models.TextField(blank=True)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    date_recorded = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'assessment')
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade_letter}"

# Financial Models
class FeeStructure(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    boarding_fee = models.DecimalField(max_digits=10, decimal_places=2)
    other_fees = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.tuition_fee + self.boarding_fee + self.other_fees
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('TUITION', 'Tuition Fee'),
        ('BOARDING', 'Boarding Fee'),
        ('OTHER', 'Other Fees'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reference_number = models.CharField(max_length=50)
    description = models.TextField(blank=True)

# Boarding Models
class Dormitory(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)
    warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Dormitories"

    def __str__(self):
        return self.name

class DormitoryAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE)
    bed_number = models.IntegerField()
    allocated_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

# Staff Models
class Staff(models.Model):
    STAFF_TYPES = [
        ('ACCOUNTANT', 'Accountant'),
        ('LIBRARIAN', 'Librarian'),
        ('NURSE', 'Nurse'),
        ('BOARDING', 'Boarding Staff'),
        ('ADMIN', 'Administrative Staff'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    employee_id = models.CharField(max_length=20, unique=True)
    date_joined = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_staff_type_display()}"

# Inventory Models
class InventoryCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Inventory Categories"

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField()
    last_restocked = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='department_head')
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    contact_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20)
    address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('contract', 'Employment Contract'),
        ('id', 'ID Documents'),
        ('certification', 'Certifications'),
        ('evaluation', 'Performance Evaluations'),
        ('other', 'Other Documents'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.start_date} to {self.end_date})"

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    review_date = models.DateField()
    performance_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals = models.TextField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - Review {self.review_date}"

    class Meta:
        ordering = ['-review_date']

class TrainingProgram(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField()
    instructor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='training_programs_led')
    participants = models.ManyToManyField(Employee, related_name='training_programs_enrolled')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity

class Term(models.Model):
    """Academic term/semester"""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class ClassGroup(models.Model):
    """Class/Grade level group"""
    name = models.CharField(max_length=100)
    grade_level = models.IntegerField()
    section = models.CharField(max_length=10, blank=True)
    academic_year = models.IntegerField()
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['grade_level', 'section']
        unique_together = ['grade_level', 'section', 'academic_year']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class Room(models.Model):
    """Physical room/classroom"""
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    floor = models.IntegerField()
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['building', 'floor', 'room_number']
        unique_together = ['building', 'floor', 'room_number']

    def __str__(self):
        return f"{self.name} ({self.building} - {self.room_number})" 