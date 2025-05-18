from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10, blank=True)
    year = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} {self.section} ({self.year})"

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday')
    ])

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['day_of_week', 'start_time', 'end_time']

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_('End time must be after start time'))

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Teacher availabilities'
        unique_together = ['teacher', 'time_slot']

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.time_slot}"

class TimetableEntry(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10)
    period = models.IntegerField()
    room = models.CharField(max_length=50, blank=True)

class ClassSchedule(models.Model):
    class_group = models.ForeignKey('school.ClassGroup', on_delete=models.CASCADE)
    subject = models.ForeignKey('school.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Teachers'})
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    room = models.ForeignKey('school.Room', on_delete=models.CASCADE)
    term = models.ForeignKey('school.Term', on_delete=models.CASCADE)
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ['time_slot', 'room', 'term'],  # Same room can't be used in the same time slot
            ['time_slot', 'teacher', 'term'],  # Teacher can't teach multiple classes at the same time
            ['time_slot', 'class_group', 'term']  # Class can't have multiple subjects at the same time
        ]

    def clean(self):
        if not TeacherAvailability.objects.filter(
            teacher=self.teacher,
            time_slot=self.time_slot,
            is_available=True
        ).exists():
            raise ValidationError(_('Teacher is not available during this time slot'))

    def __str__(self):
        return f"{self.class_group} - {self.subject} ({self.time_slot})"

class Schedule(models.Model):
    """Weekly schedule view for students and teachers"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    term = models.ForeignKey('school.Term', on_delete=models.CASCADE)
    last_generated = models.DateTimeField(auto_now=True)
    cached_schedule = models.JSONField(default=dict)  # Stores pre-computed schedule for performance

    class Meta:
        unique_together = ['user', 'term']

    def generate_schedule(self):
        """Generates and caches the weekly schedule for quick access"""
        if self.user.groups.filter(name='Teachers').exists():
            classes = ClassSchedule.objects.filter(teacher=self.user, term=self.term)
        else:  # Student
            classes = ClassSchedule.objects.filter(
                class_group=self.user.student_profile.class_group,
                term=self.term
            )
        
        schedule = {str(day): [] for day in range(5)}  # Monday to Friday
        for class_schedule in classes:
            day = str(class_schedule.time_slot.day_of_week)
            schedule[day].append({
                'subject': class_schedule.subject.name,
                'teacher': class_schedule.teacher.get_full_name(),
                'room': class_schedule.room.name,
                'start_time': class_schedule.time_slot.start_time.strftime('%H:%M'),
                'end_time': class_schedule.time_slot.end_time.strftime('%H:%M')
            })
        
        self.cached_schedule = schedule
        self.save()
        return schedule

    def __str__(self):
        return f"Schedule for {self.user.get_full_name()} - {self.term}"
