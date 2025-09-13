from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import TimeSlot, Lesson


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_time", "end_time")
    list_filter = ("weekday",)


class LessonAdmin(admin.ModelAdmin):
    list_display = ("classroom", "subject", "teacher", "timeslot")
    list_filter = ("classroom", "teacher", "subject")


for model, admin_class in (
    (TimeSlot, TimeSlotAdmin),
    (Lesson, LessonAdmin),
):
    try:
        admin.site.register(model, admin_class)
    except AlreadyRegistered:
        pass
