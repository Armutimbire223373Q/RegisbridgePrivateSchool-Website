from django.db import models
from students.models import ClassRoom
from teachers.models import Subject, TeacherProfile


class TimeSlot(models.Model):
    WEEKDAY_CHOICES = [
        (i, d) for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    ]
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("weekday", "start_time", "end_time")
        ordering = ("weekday", "start_time")

    def __str__(self) -> str:
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Lesson(models.Model):
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="lessons"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="lessons"
    )
    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.PROTECT, related_name="lessons"
    )
    timeslot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, related_name="lessons"
    )
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ("classroom", "timeslot")

    def __str__(self) -> str:
        return f"{self.classroom} - {self.subject} - {self.timeslot}"
