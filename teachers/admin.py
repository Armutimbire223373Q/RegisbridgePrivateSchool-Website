from django.contrib import admin
from .models import (
    TeacherProfile, Subject, Class, ClassSubject,
    ClassStudent, Assignment, AssignmentSubmission
)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher_id', 'qualification', 'specialization', 'joining_date')
    search_fields = ('user__first_name', 'user__last_name', 'teacher_id', 'qualification')
    list_filter = ('qualification', 'specialization')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher')
    search_fields = ('name', 'code')
    list_filter = ('teacher',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_level', 'section', 'academic_year')
    search_fields = ('name', 'grade_level', 'section')
    list_filter = ('grade_level', 'academic_year')

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'subject', 'teacher')
    search_fields = ('class_name__name', 'subject__name', 'teacher__user__username')
    list_filter = ('class_name__grade_level', 'subject')

@admin.register(ClassStudent)
class ClassStudentAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'student', 'enrollment_date')
    search_fields = ('class_name__name', 'student__user__username')
    list_filter = ('class_name__grade_level', 'enrollment_date')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_subject', 'due_date', 'created_at')
    search_fields = ('title', 'class_subject__subject__name')
    list_filter = ('class_subject__class_name__grade_level', 'due_date')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submission_date', 'grade')
    search_fields = ('assignment__title', 'student__user__username')
    list_filter = ('submission_date', 'grade')