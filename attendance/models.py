from django.conf import settings
from django.db import models
from students.models import ClassRoom, StudentProfile


class AttendanceSession(models.Model):
    date = models.DateField()
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="attendance_sessions"
    )
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "classroom")
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.date} - {self.classroom}"


class AttendanceRecord(models.Model):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    STATUS = (
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (LATE, "Late"),
    )

    session = models.ForeignKey(
        AttendanceSession, on_delete=models.CASCADE, related_name="records"
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="attendance_records"
    )
    status = models.CharField(max_length=10, choices=STATUS)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self) -> str:
        return f"{self.student} - {self.status}"


from django.db import models

# Create your models here.
