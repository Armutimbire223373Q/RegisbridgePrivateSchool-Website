from django.db import models
from django.utils import timezone
from students.models import GradeLevel, StudentProfile
from django.conf import settings


class Application(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("REVIEW", "In Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("ENROLLED", "Enrolled"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other")],
    )
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.PROTECT)

    guardian_name = models.CharField(max_length=150)
    guardian_phone = models.CharField(max_length=30)
    guardian_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    previous_school = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="NEW")
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} - {self.grade_level.name} ({self.status})"


class Enrollment(models.Model):
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="enrollment"
    )
    student = models.OneToOneField(
        StudentProfile, null=True, blank=True, on_delete=models.SET_NULL
    )
    enrollment_date = models.DateField(default=timezone.now)
    admission_number = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return f"Enrollment: {self.admission_number}"
