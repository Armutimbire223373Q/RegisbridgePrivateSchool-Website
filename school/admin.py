from django.contrib import admin
from .models import (
    ImportantDate, LeadershipMember, ParentResource, PaymentMethod,
    PrivacyPolicy, Scholarship, StudentService, TuitionFee, HostelFacility,
    ParentProfile, TeacherProfile, AcademicYear, Class, Subject, Student, Teacher,
    Staff, Attendance, Grade, Payment, Dormitory, InventoryItem
)

@admin.register(HostelFacility)
class HostelFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available', 'order', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ImportantDate)
class ImportantDateAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('-date', 'title')

@admin.register(LeadershipMember)
class LeadershipMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'position', 'bio')
    ordering = ('order', 'name')

@admin.register(ParentResource)
class ParentResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    ordering = ('-created_at', 'title')
    readonly_fields = ('created_at',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('last_updated',)
    readonly_fields = ('last_updated',)

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'deadline', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('deadline',)

@admin.register(StudentService)
class StudentServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ('grade', 'amount', 'is_active')
    list_filter = ('is_active', 'grade')
    search_fields = ('grade', 'description')
    ordering = ('grade',)

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__email', 'phone_number')
    ordering = ('user__username',)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization')
    search_fields = ('user__username', 'user__email', 'department', 'specialization')
    ordering = ('user__username',)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'academic_year', 'class_teacher')
    search_fields = ('name', 'section')
    list_filter = ('academic_year',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'user', 'current_class', 'is_boarder')
    search_fields = ('admission_number', 'user__first_name', 'user__last_name')
    list_filter = ('current_class', 'is_boarder')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'qualification', 'date_joined')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'staff_type', 'date_joined')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')
    list_filter = ('staff_type',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present', 'recorded_by')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    list_filter = ('date', 'is_present')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_year', 'term', 'score')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    list_filter = ('academic_year', 'term', 'subject')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'payment_type', 'amount', 'payment_date', 'reference_number')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'reference_number')
    list_filter = ('payment_type', 'payment_date')

@admin.register(Dormitory)
class DormitoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'current_occupancy', 'warden')
    search_fields = ('name',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit_price', 'reorder_level')
    search_fields = ('name',)
    list_filter = ('category',) 