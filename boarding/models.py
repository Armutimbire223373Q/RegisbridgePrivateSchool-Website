from django.db import models
from django.utils import timezone

from students.models import StudentProfile


class Dormitory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name

    @property
    def occupied_beds(self) -> int:
        return self.beds.filter(is_occupied=True).count()


class Bed(models.Model):
    dormitory = models.ForeignKey(
        Dormitory, related_name="beds", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ("dormitory", "number")

    def __str__(self) -> str:
        return f"{self.dormitory.name} - {self.number}"


class BoardingStudent(models.Model):
    STATUS_CHOICES = (
        ("BOARDER", "Boarder"),
        ("DAY", "Day Scholar"),
        ("LEAVE", "On Leave"),
    )

    student = models.OneToOneField(
        StudentProfile, related_name="boarding", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="DAY")
    dormitory = models.ForeignKey(
        Dormitory, null=True, blank=True, on_delete=models.SET_NULL
    )
    bed = models.OneToOneField(Bed, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_on = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.student.user.get_full_name()} - {self.get_status_display()}"


class MealPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class MealRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    meal_type = models.CharField(
        max_length=20,
        choices=(("BREAKFAST", "Breakfast"), ("LUNCH", "Lunch"), ("DINNER", "Dinner")),
    )
    taken = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "date", "meal_type")


class WellBeingCheck(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField()
    recorded_by = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.student.user.get_full_name()} - {self.date.strftime('%Y-%m-%d')}"
