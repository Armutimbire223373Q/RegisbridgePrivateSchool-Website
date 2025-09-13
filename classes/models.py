from django.db import models
from django.conf import settings
from students.models import GradeLevel, StudentProfile
from teachers.models import Subject, TeacherProfile


class AcademicSession(models.Model):
    """Academic session/year (e.g., 2024-2025)"""
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Academic Session"
        verbose_name_plural = "Academic Sessions"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Ensure only one session is active at a time
            AcademicSession.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)


class Classroom(models.Model):
    """Physical classroom/room"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(default=30)
    floor = models.CharField(max_length=50, blank=True)
    building = models.CharField(max_length=100, blank=True)
    facilities = models.TextField(blank=True, help_text="Available facilities and equipment")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassGroup(models.Model):
    """A class group (like Form 1A, Grade 3B, etc.)"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    grade_level = models.ForeignKey(
        GradeLevel, 
        on_delete=models.CASCADE, 
        related_name="class_groups"
    )
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="class_groups"
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_groups"
    )
    class_teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_groups_managed"
    )
    max_students = models.PositiveIntegerField(default=35)
    is_active = models.BooleanField(default=True)
    
    # Additional class information
    class_motto = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['name', 'academic_session']
        ordering = ['grade_level__name', 'name']
        verbose_name = "Class Group"
        verbose_name_plural = "Class Groups"
    
    def __str__(self):
        return f"{self.name} ({self.academic_session.name})"
    
    @property
    def current_enrollment(self):
        """Get current number of enrolled students"""
        return self.students.filter(is_active=True).count()
    
    @property
    def available_slots(self):
        """Get available slots in this class"""
        return max(0, self.max_students - self.current_enrollment)


class ClassEnrollment(models.Model):
    """Track student enrollment in class groups"""
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="class_enrollments"
    )
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'class_group']
        ordering = ['-enrollment_date']
        verbose_name = "Class Enrollment"
        verbose_name_plural = "Class Enrollments"
    
    def __str__(self):
        return f"{self.student} in {self.class_group}"


class SubjectAllocation(models.Model):
    """Allocate subjects to teachers for specific class groups"""
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="subject_allocations"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="allocations"
    )
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="subject_allocations"
    )
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="subject_allocations"
    )
    periods_per_week = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['subject', 'class_group', 'academic_session']
        ordering = ['class_group__name', 'subject__name']
        verbose_name = "Subject Allocation"
        verbose_name_plural = "Subject Allocations"
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.class_group}"


class ClassSchedule(models.Model):
    """Class schedule/timetable"""
    WEEKDAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="schedules"
    )
    subject_allocation = models.ForeignKey(
        SubjectAllocation,
        on_delete=models.CASCADE,
        related_name="schedules"
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules"
    )
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['class_group', 'weekday', 'start_time']
        ordering = ['weekday', 'start_time']
        verbose_name = "Class Schedule"
        verbose_name_plural = "Class Schedules"
    
    def __str__(self):
        return f"{self.class_group} - {self.get_weekday_display()} {self.start_time}"


class ClassEvent(models.Model):
    """Class-specific events and activities"""
    EVENT_TYPES = [
        ('EXAM', 'Examination'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('FIELD_TRIP', 'Field Trip'),
        ('PRESENTATION', 'Presentation'),
        ('MEETING', 'Class Meeting'),
        ('OTHER', 'Other'),
    ]
    
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="events"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='OTHER')
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="class_events_created"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date']
        verbose_name = "Class Event"
        verbose_name_plural = "Class Events"
    
    def __str__(self):
        return f"{self.class_group} - {self.title}"
