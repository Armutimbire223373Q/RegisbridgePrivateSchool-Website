from django.contrib import admin
from .models import (
    AcademicSession,
    Classroom,
    ClassGroup,
    ClassEnrollment,
    SubjectAllocation,
    ClassSchedule,
    ClassEvent,
)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'description')
    ordering = ('-start_date',)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'capacity', 'building', 'floor', 'is_active')
    list_filter = ('is_active', 'building', 'floor')
    search_fields = ('name', 'code', 'building')
    ordering = ('code',)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'grade_level', 'academic_session', 'class_teacher', 'max_students', 'is_active')
    list_filter = ('is_active', 'academic_session', 'grade_level')
    search_fields = ('name', 'code', 'class_motto')
    ordering = ('grade_level__name', 'name')


@admin.register(ClassEnrollment)
class ClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_group', 'enrollment_date', 'is_active')
    list_filter = ('is_active', 'enrollment_date')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    ordering = ('-enrollment_date',)


@admin.register(SubjectAllocation)
class SubjectAllocationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_group', 'academic_session', 'periods_per_week', 'is_active')
    list_filter = ('is_active', 'academic_session', 'subject')
    search_fields = ('teacher__user__first_name', 'subject__name', 'class_group__name')
    ordering = ('class_group__name', 'subject__name')


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_group', 'subject_allocation', 'get_weekday_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'weekday')
    ordering = ('class_group__name', 'weekday', 'start_time')


@admin.register(ClassEvent)
class ClassEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_group', 'event_type', 'event_date', 'location', 'is_active')
    list_filter = ('is_active', 'event_type', 'event_date')
    search_fields = ('title', 'description', 'class_group__name')
    ordering = ('-event_date',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
