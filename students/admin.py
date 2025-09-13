from django.contrib import admin
from .models import GradeLevel, ClassRoom, Dormitory, StudentProfile


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "stage")
    search_fields = ("name",)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "grade_level")
    list_filter = ("grade_level",)
    search_fields = ("name",)


@admin.register(Dormitory)
class DormitoryAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity")
    search_fields = ("name",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "admission_number",
        "user",
        "grade_level",
        "classroom",
        "is_boarder",
        "dormitory",
    )
    list_filter = ("grade_level", "is_boarder", "dormitory")
    search_fields = (
        "admission_number",
        "user__username",
        "user__first_name",
        "user__last_name",
    )


# Register your models here.
