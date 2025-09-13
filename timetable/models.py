from django.db import models
from students.models import ClassRoom
from teachers.models import Subject, TeacherProfile


class TimeSlot(models.Model):
    day_of_week = models.IntegerField(
        choices=[
            (i, d) for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("day_of_week", "start_time", "end_time")
        ordering = ("day_of_week", "start_time")

    def __str__(self) -> str:
        return f"{self.day_of_week} {self.start_time}-{self.end_time}"


class Lesson(models.Model):
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="lessons"
    )
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.PROTECT)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("classroom", "timeslot")

    def __str__(self) -> str:
        return f"{self.classroom} - {self.subject} ({self.timeslot})"
