from django.contrib import admin
from .models import Parent


class StudentInline(admin.TabularInline):
    model = Parent.students.through
    extra = 1
    verbose_name = "Student"
    verbose_name_plural = "Students"


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = [
        "user_full_name",
        "relationship",
        "phone_number",
        "city",
        "is_primary_contact",
        "student_count",
    ]
    list_filter = ["relationship", "is_primary_contact", "city", "country"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone_number",
        "emergency_contact_name",
    ]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "relationship", "students", "is_primary_contact")},
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone_number",
                    "alternative_phone",
                    "address",
                    "city",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                )
            },
        ),
        ("Additional Information", {"fields": ("occupation", "employer")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [StudentInline]

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = "Parent Name"

    def student_count(self, obj):
        return obj.students.count()

    student_count.short_description = "Students"
