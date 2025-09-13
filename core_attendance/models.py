from django.db import models
from django.conf import settings
from students.models import StudentProfile
from teachers.models import TeacherProfile


class AttendanceSession(models.Model):
    date = models.DateField()
    classroom = models.ForeignKey(
        "students.ClassRoom",
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "classroom")
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.classroom} - {self.date}"


class AttendanceRecord(models.Model):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    STATUS_CHOICES = (
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (LATE, "Late"),
    )

    session = models.ForeignKey(
        AttendanceSession, on_delete=models.CASCADE, related_name="records"
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="session_attendance_records",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("session", "student")
        ordering = ("student__admission_number",)

    def __str__(self) -> str:
        return f"{self.student} - {self.session.date} - {self.status}"


class StudentAttendance(models.Model):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    STATUS_CHOICES = (
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (LATE, "Late"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="daily_attendance_records",
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    remarks = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ("-date", "student__admission_number")

    def __str__(self) -> str:
        return f"{self.student} - {self.date} - {self.status}"


class BoardingMealAttendance(models.Model):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    MEAL_CHOICES = (
        (BREAKFAST, "Breakfast"),
        (LUNCH, "Lunch"),
        (DINNER, "Dinner"),
    )

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="meal_attendance"
    )
    date = models.DateField()
    meal = models.CharField(max_length=10, choices=MEAL_CHOICES)
    present = models.BooleanField(default=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "date", "meal")
        ordering = ("-date", "meal")

    def __str__(self) -> str:
        return f"{self.student} - {self.date} - {self.meal}"
