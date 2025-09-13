from django.contrib import admin
from .models import (
    Dormitory,
    Bed,
    BoardingStudent,
    MealPlan,
    MealRecord,
    WellBeingCheck,
)


@admin.register(Dormitory)
class DormitoryAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "occupied_beds")


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("dormitory", "number", "is_occupied")
    list_filter = ("dormitory", "is_occupied")


@admin.register(BoardingStudent)
class BoardingStudentAdmin(admin.ModelAdmin):
    list_display = ("student", "status", "dormitory", "assigned_on")
    list_filter = ("status", "dormitory")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
    )


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)


@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "meal_type", "taken")
    list_filter = ("meal_type", "date", "taken")


@admin.register(WellBeingCheck)
class WellBeingCheckAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "recorded_by")
    list_filter = ("date",)
