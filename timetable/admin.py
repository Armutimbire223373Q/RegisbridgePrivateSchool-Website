from django.contrib import admin
from .models import TimeSlot, Lesson


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "start_time", "end_time")
    list_filter = ("day_of_week",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("classroom", "subject", "teacher", "timeslot")
    list_filter = ("classroom", "teacher", "timeslot__day_of_week")
