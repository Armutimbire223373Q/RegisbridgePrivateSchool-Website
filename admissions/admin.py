from django.contrib import admin
from .models import Application, Enrollment


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "grade_level", "status", "submitted_at")
    list_filter = ("status", "grade_level")
    search_fields = ("first_name", "last_name", "guardian_name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("admission_number", "application", "enrollment_date")
    search_fields = ("admission_number",)
