from django.conf import settings
from django.db import models


class GradeLevel(models.Model):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    STAGE_CHOICES = (
        (PRIMARY, "Primary"),
        (SECONDARY, "Secondary"),
    )

    name = models.CharField(max_length=50, unique=True)
    stage = models.CharField(max_length=16, choices=STAGE_CHOICES)
    description = models.TextField(blank=True)
    min_age = models.PositiveIntegerField(blank=True, null=True)
    max_age = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_stage_display()})"


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    grade_level = models.ForeignKey(
        GradeLevel, on_delete=models.PROTECT, related_name="classes"
    )
    capacity = models.PositiveIntegerField(default=30)
    room_number = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "grade_level")
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self) -> str:
        return f"{self.name} - {self.grade_level.name}"


class Dormitory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=0)
    gender = models.CharField(
        max_length=10,
        choices=[("MALE", "Male"), ("FEMALE", "Female"), ("MIXED", "Mixed")],
        default="MIXED",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class StudentProfile(models.Model):
    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    admission_number = models.CharField(max_length=30, unique=True)
    grade_level = models.ForeignKey(
        GradeLevel, on_delete=models.PROTECT, related_name="students"
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    is_boarder = models.BooleanField(default=False)
    dormitory = models.ForeignKey(
        Dormitory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boarders",
    )

    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(
        max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True
    )
    nationality = models.CharField(max_length=50, default="Kenyan")

    # Academic Information
    enrollment_date = models.DateField(auto_now_add=True)
    expected_graduation = models.DateField(null=True, blank=True)
    previous_school = models.CharField(max_length=200, blank=True)
    academic_status = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Active"),
            ("SUSPENDED", "Suspended"),
            ("WITHDRAWN", "Withdrawn"),
            ("GRADUATED", "Graduated"),
        ],
        default="ACTIVE",
    )

    # Health Information
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)

    # Additional Information
    hobbies = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional profile photo used by portal header
    photo = models.ImageField(upload_to="student_photos/", blank=True, null=True)

    class Meta:
        ordering = ["admission_number"]
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} ({self.admission_number})"

    @property
    def age(self):
        """Calculate student's age"""
        if self.date_of_birth:
            from datetime import date

            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None

    @property
    def full_name(self):
        """Get student's full name"""
        return self.user.get_full_name() or self.user.username

    def get_grade_average(self):
        """Calculate student's grade average"""
        from grades.models import StudentTermGrade

        grades = StudentTermGrade.objects.filter(student=self)
        if grades.exists():
            return grades.aggregate(avg=models.Avg("percentage"))["avg"]
        return 0
