from django.contrib import admin
from django.utils import timezone
from .models import (
    AttendanceSession,
    AttendanceRecord,
    StudentAttendance,
    BoardingMealAttendance,
)


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("date", "classroom", "taken_by", "created_at")
    list_filter = ("date", "classroom")
    inlines = [AttendanceRecordInline]
    actions = ("mark_today",)

    def mark_today(self, request, queryset):
        updated = queryset.update(date=timezone.now().date())
        self.message_user(request, f"Updated {updated} sessions to today.")

    mark_today.short_description = "Set selected sessions' date to today"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "status")
    list_filter = ("status",)


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "student", "status", "recorded_by")
    list_filter = ("status", "date")
    search_fields = ("student__admission_number", "student__user__username")


@admin.register(BoardingMealAttendance)
class BoardingMealAttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "meal", "student", "present")
    list_filter = ("meal", "date", "present")
