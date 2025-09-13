from django.contrib import admin
from .models import (
    AcademicYear,
    Term,
    AssessmentType,
    Assessment,
    Grade,
    StudentTermGrade,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["-start_date"]


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ["name", "academic_year", "start_date", "end_date", "is_active"]
    list_filter = ["academic_year", "is_active", "name"]
    search_fields = ["academic_year__name"]
    ordering = ["academic_year", "name"]


@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "weight", "description"]
    list_filter = ["weight"]
    search_fields = ["name"]
    ordering = ["name"]


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    readonly_fields = ["graded_at"]
    fields = ["student", "marks_obtained", "remarks", "graded_by"]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "classroom",
        "assessment_type",
        "term",
        "total_marks",
        "due_date",
        "created_by",
    ]
    list_filter = ["assessment_type", "term", "subject", "classroom"]
    search_fields = ["title", "subject__name", "classroom__name"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "subject", "classroom", "assessment_type", "term")},
        ),
        ("Assessment Details", {"fields": ("total_marks", "due_date", "instructions")}),
        (
            "Metadata",
            {"fields": ("created_by", "created_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [GradeInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "assessment",
        "marks_obtained",
        "total_marks",
        "percentage",
        "letter_grade",
        "graded_by",
        "graded_at",
    ]
    list_filter = ["assessment__term", "assessment__subject", "assessment__classroom"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "assessment__title",
    ]
    readonly_fields = ["graded_at", "percentage", "letter_grade"]

    fieldsets = (
        (
            "Grade Information",
            {"fields": ("student", "assessment", "marks_obtained", "remarks")},
        ),
        ("Metadata", {"fields": ("graded_by", "graded_at"), "classes": ("collapse",)}),
    )

    def total_marks(self, obj):
        return obj.assessment.total_marks

    total_marks.short_description = "Total Marks"

    def save_model(self, request, obj, form, change):
        if not change:  # Only set graded_by for new objects
            obj.graded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentTermGrade)
class StudentTermGradeAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "subject",
        "term",
        "marks_obtained",
        "total_marks",
        "percentage",
        "letter_grade",
    ]
    list_filter = ["term", "subject", "letter_grade"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "subject__name",
    ]
    readonly_fields = ["percentage", "letter_grade"]

    actions = ["recalculate_grades"]

    def recalculate_grades(self, request, queryset):
        """Recalculate grades for selected term grades"""
        updated = 0
        for term_grade in queryset:
            term_grade.calculate_term_grade()
            updated += 1

        self.message_user(request, f"Successfully recalculated {updated} term grades.")

    recalculate_grades.short_description = "Recalculate selected term grades"
