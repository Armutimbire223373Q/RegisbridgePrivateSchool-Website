from django.contrib import admin
from .models import StudentProfile, Attendance, Grade

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'date_of_birth', 'gender', 'admission_date')
    search_fields = ('user__first_name', 'user__last_name', 'student_id', 'parent_name', 'parent_phone')
    list_filter = ('gender', 'admission_date')
    date_hierarchy = 'admission_date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'notes')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__student_id')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'score', 'date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__student_id', 'subject__name')
    list_filter = ('term', 'subject', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)