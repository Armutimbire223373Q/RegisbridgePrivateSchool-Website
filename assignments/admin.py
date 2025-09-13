from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Assignment, AssignmentSubmission, AssignmentComment


class AssignmentCommentInline(admin.TabularInline):
    model = AssignmentComment
    extra = 0
    readonly_fields = ["created_at"]
    fields = ["author", "content", "is_private", "created_at"]


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ["submitted_at", "is_late", "percentage"]
    fields = ["student", "status", "marks_obtained", "submitted_at", "is_late"]

    def percentage(self, obj):
        if obj.percentage:
            return f"{obj.percentage:.1f}%"
        return "-"

    percentage.short_description = "Score %"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "term",
        "status",
        "due_date",
        "submission_count",
        "graded_count",
        "is_overdue_display",
    ]
    list_filter = ["status", "subject", "term", "created_by", "due_date"]
    search_fields = ["title", "description", "subject__name"]
    readonly_fields = ["created_at", "updated_at", "submission_count", "graded_count"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "description", "subject", "term", "created_by")},
        ),
        (
            "Assignment Details",
            {"fields": ("due_date", "max_marks", "instructions", "rubric")},
        ),
        ("File Attachment", {"fields": ("attachment",)}),
        (
            "Settings",
            {
                "fields": (
                    "allow_late_submission",
                    "late_penalty",
                    "allow_resubmission",
                    "max_submissions",
                )
            },
        ),
        ("Status", {"fields": ("status",)}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [AssignmentSubmissionInline, AssignmentCommentInline]

    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠️ Overdue</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')

    is_overdue_display.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "assignment",
        "status",
        "submitted_at",
        "marks_obtained",
        "is_late",
        "percentage_display",
    ]
    list_filter = ["status", "is_late", "assignment__subject", "assignment__term"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "assignment__title",
    ]
    readonly_fields = ["submitted_at", "is_late", "percentage", "final_marks"]

    fieldsets = (
        (
            "Submission Information",
            {"fields": ("assignment", "student", "submission_number", "status")},
        ),
        ("Content", {"fields": ("content", "attachment")}),
        (
            "Grading",
            {"fields": ("marks_obtained", "feedback", "graded_by", "graded_at")},
        ),
        (
            "Metadata",
            {
                "fields": ("submitted_at", "is_late", "percentage", "final_marks"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [AssignmentCommentInline]

    def percentage_display(self, obj):
        if obj.percentage:
            return f"{obj.percentage:.1f}%"
        return "-"

    percentage_display.short_description = "Score %"

    def save_model(self, request, obj, form, change):
        if not change:  # Only set graded_by for new objects
            obj.graded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssignmentComment)
class AssignmentCommentAdmin(admin.ModelAdmin):
    list_display = [
        "assignment",
        "author",
        "content_preview",
        "is_private",
        "created_at",
    ]
    list_filter = ["is_private", "created_at", "assignment__subject"]
    search_fields = ["content", "author__username", "assignment__title"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Comment Information",
            {"fields": ("assignment", "submission", "author", "content")},
        ),
        ("Settings", {"fields": ("is_private",)}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Content"
