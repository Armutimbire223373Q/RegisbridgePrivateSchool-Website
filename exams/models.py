from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import StudentProfile, ClassRoom
from teachers.models import Subject
from grades.models import Term


class ExamType(models.Model):
    """Types of exams (e.g., Mid-term, Final, Mock)"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Weight as percentage of total grade",
    )
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class ExamSchedule(models.Model):
    """Exam schedule with timing and room allocation"""

    title = models.CharField(max_length=200)
    exam_type = models.ForeignKey(
        ExamType, on_delete=models.CASCADE, related_name="exam_schedules"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="exam_schedules"
    )
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name="exam_schedules"
    )

    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")

    # Room allocation
    classrooms = models.ManyToManyField(ClassRoom, related_name="exam_schedules")
    max_students_per_room = models.PositiveIntegerField(default=30)

    # Settings
    allow_early_submission = models.BooleanField(default=True)
    allow_late_entry = models.BooleanField(
        default=False, help_text="Allow students to enter after start time"
    )
    instructions = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("SCHEDULED", "Scheduled"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="SCHEDULED",
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time", "subject__name"]
        verbose_name = "Exam Schedule"
        verbose_name_plural = "Exam Schedules"

    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_overdue(self):
        """Check if exam is overdue"""
        return timezone.now() > self.end_time

    @property
    def is_in_progress(self):
        """Check if exam is currently in progress"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def total_students(self):
        """Get total number of students taking this exam"""
        return sum(classroom.students.count() for classroom in self.classrooms.all())

    def get_room_allocation(self):
        """Get room allocation for students"""
        allocations = {}
        students_per_room = self.max_students_per_room

        for classroom in self.classrooms.all():
            students = list(classroom.students.all())
            room_allocations = []

            for i in range(0, len(students), students_per_room):
                room_allocations.append(students[i : i + students_per_room])

            allocations[classroom] = room_allocations

        return allocations


class ExamSession(models.Model):
    """Individual student exam session"""

    exam_schedule = models.ForeignKey(
        ExamSchedule, on_delete=models.CASCADE, related_name="exam_sessions"
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="exam_sessions"
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="exam_sessions"
    )

    # Timing
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    actual_duration = models.PositiveIntegerField(
        null=True, blank=True, help_text="Actual duration in minutes"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("REGISTERED", "Registered"),
            ("STARTED", "Started"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
            ("ABSENT", "Absent"),
            ("DISQUALIFIED", "Disqualified"),
        ],
        default="REGISTERED",
    )

    # Results
    marks_obtained = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    remarks = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["exam_schedule", "student"]
        ordering = ["exam_schedule__start_time", "student__admission_number"]
        verbose_name = "Exam Session"
        verbose_name_plural = "Exam Sessions"

    def __str__(self):
        return f"{self.student} - {self.exam_schedule.title}"

    def start_exam(self):
        """Start the exam for the student"""
        if self.status == "REGISTERED":
            self.status = "STARTED"
            self.start_time = timezone.now()
            self.save()

    def complete_exam(self):
        """Complete the exam for the student"""
        if self.status in ["STARTED", "IN_PROGRESS"]:
            self.status = "COMPLETED"
            self.end_time = timezone.now()

            if self.start_time:
                duration = (self.end_time - self.start_time).total_seconds() / 60
                self.actual_duration = int(duration)

            self.save()

    @property
    def is_late(self):
        """Check if student started late"""
        if self.start_time and self.exam_schedule.start_time:
            return self.start_time > self.exam_schedule.start_time
        return False

    @property
    def time_remaining(self):
        """Get time remaining for the exam"""
        if self.status == "IN_PROGRESS" and self.start_time:
            elapsed = (timezone.now() - self.start_time).total_seconds() / 60
            remaining = self.exam_schedule.duration_minutes - elapsed
            return max(0, int(remaining))
        return 0


class ExamInvigilator(models.Model):
    """Exam invigilators and their assignments"""

    exam_schedule = models.ForeignKey(
        ExamSchedule, on_delete=models.CASCADE, related_name="invigilators"
    )
    invigilator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invigilation_assignments",
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="invigilators"
    )

    # Role
    role = models.CharField(
        max_length=20,
        choices=[
            ("CHIEF", "Chief Invigilator"),
            ("INVIGILATOR", "Invigilator"),
            ("ASSISTANT", "Assistant"),
        ],
        default="INVIGILATOR",
    )

    # Assignment details
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ["exam_schedule", "invigilator", "classroom"]
        verbose_name = "Exam Invigilator"
        verbose_name_plural = "Exam Invigilators"

    def __str__(self):
        return f"{self.invigilator.get_full_name()} - {self.exam_schedule.title} ({self.classroom.name})"
