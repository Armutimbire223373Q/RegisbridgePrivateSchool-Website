from django.conf import settings
from django.db import models


class Subject(models.Model):
    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_core = models.BooleanField(
        default=False, help_text="Core subject for all students"
    )
    is_active = models.BooleanField(default=True)

    # Subject details
    grade_levels = models.ManyToManyField(
        "students.GradeLevel", related_name="subjects", blank=True
    )
    credit_hours = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["code"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class TeacherProfile(models.Model):
    QUALIFICATION_CHOICES = [
        ("BACHELORS", "Bachelor's Degree"),
        ("MASTERS", "Master's Degree"),
        ("PHD", "PhD"),
        ("DIPLOMA", "Diploma"),
        ("CERTIFICATE", "Certificate"),
        ("OTHER", "Other"),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ("FULL_TIME", "Full Time"),
        ("PART_TIME", "Part Time"),
        ("CONTRACT", "Contract"),
        ("INTERN", "Intern"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)

    # Professional Information
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    qualification = models.CharField(
        max_length=20, choices=QUALIFICATION_CHOICES, blank=True
    )
    specialization = models.CharField(max_length=200, blank=True)
    employment_status = models.CharField(
        max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default="FULL_TIME"
    )
    hire_date = models.DateField(auto_now_add=True)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    alternative_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Professional Details
    years_of_experience = models.PositiveIntegerField(default=0)
    previous_schools = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    # Administrative
    is_head_of_department = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        """Get teacher's full name"""
        return self.user.get_full_name() or self.user.username

    def get_total_students(self):
        """Get total number of students taught by this teacher"""
        from core_timetable.models import Lesson

        lessons = Lesson.objects.filter(teacher=self)
        classrooms = lessons.values_list("classroom", flat=True).distinct()
        from students.models import StudentProfile

        return StudentProfile.objects.filter(classroom__in=classrooms).count()

    def get_subject_names(self):
        """Get comma-separated list of subject names"""
        return ", ".join([subject.name for subject in self.subjects.all()])
