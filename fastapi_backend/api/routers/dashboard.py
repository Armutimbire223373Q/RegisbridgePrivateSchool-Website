"""
Dashboard endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from django.db.models import Count, Q
from datetime import date, timedelta

from api.models import DashboardStats, BaseResponse
from api.auth import get_current_user, require_roles
from students.models import StudentProfile
from teachers.models import TeacherProfile
from parents.models import Parent
from classes.models import ClassRoom
from core_attendance.models import AttendanceRecord, AttendanceSession
from fees.models import Invoice

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"]))
):
    """
    Get dashboard statistics
    """
    # Basic counts
    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_parents = Parent.objects.count()
    active_students = StudentProfile.objects.filter(academic_status='ACTIVE').count()
    total_classes = ClassRoom.objects.count()
    
    # Today's attendance
    today = date.today()
    today_sessions = AttendanceSession.objects.filter(date=today)
    total_attendance_today = AttendanceRecord.objects.filter(session__in=today_sessions).count()
    
    # Pending fees
    pending_fees = Invoice.objects.filter(status='PENDING').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Recent activities (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    recent_activities = []
    
    # Recent student enrollments
    recent_students = StudentProfile.objects.filter(
        created_at__gte=week_ago
    ).values('user__first_name', 'user__last_name', 'created_at')[:5]
    
    for student in recent_students:
        recent_activities.append({
            "type": "student_enrollment",
            "message": f"New student {student['user__first_name']} {student['user__last_name']} enrolled",
            "date": student['created_at'].isoformat()
        })
    
    # Recent teacher additions
    recent_teachers = TeacherProfile.objects.filter(
        created_at__gte=week_ago
    ).values('user__first_name', 'user__last_name', 'created_at')[:5]
    
    for teacher in recent_teachers:
        recent_activities.append({
            "type": "teacher_addition",
            "message": f"New teacher {teacher['user__first_name']} {teacher['user__last_name']} added",
            "date": teacher['created_at'].isoformat()
        })
    
    return DashboardStats(
        total_students=total_students,
        total_teachers=total_teachers,
        total_parents=total_parents,
        active_students=active_students,
        total_classes=total_classes,
        total_attendance_today=total_attendance_today,
        pending_fees=pending_fees,
        recent_activities=recent_activities
    )

@router.get("/student-stats")
async def get_student_statistics(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get student statistics by grade level and status
    """
    # Students by grade level
    students_by_grade = StudentProfile.objects.values('grade_level__name').annotate(
        count=Count('id')
    ).order_by('grade_level__level')
    
    # Students by status
    students_by_status = StudentProfile.objects.values('academic_status').annotate(
        count=Count('id')
    )
    
    # Boarding vs Day students
    boarding_students = StudentProfile.objects.filter(is_boarder=True).count()
    day_students = StudentProfile.objects.filter(is_boarder=False).count()
    
    return {
        "students_by_grade": list(students_by_grade),
        "students_by_status": list(students_by_status),
        "boarding_vs_day": {
            "boarding": boarding_students,
            "day": day_students
        }
    }

@router.get("/attendance-stats")
async def get_attendance_statistics(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get attendance statistics
    """
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Today's attendance
    today_sessions = AttendanceSession.objects.filter(date=today)
    today_attendance = AttendanceRecord.objects.filter(session__in=today_sessions)
    
    today_present = today_attendance.filter(status='PRESENT').count()
    today_absent = today_attendance.filter(status='ABSENT').count()
    today_late = today_attendance.filter(status='LATE').count()
    
    # Weekly attendance trend
    weekly_sessions = AttendanceSession.objects.filter(
        date__gte=week_ago,
        date__lte=today
    )
    weekly_attendance = AttendanceRecord.objects.filter(session__in=weekly_sessions)
    
    weekly_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_sessions = weekly_sessions.filter(date=day)
        day_attendance = weekly_attendance.filter(session__in=day_sessions)
        
        weekly_stats.append({
            "date": day.isoformat(),
            "present": day_attendance.filter(status='PRESENT').count(),
            "absent": day_attendance.filter(status='ABSENT').count(),
            "late": day_attendance.filter(status='LATE').count()
        })
    
    return {
        "today": {
            "present": today_present,
            "absent": today_absent,
            "late": today_late,
            "total": today_present + today_absent + today_late
        },
        "weekly_trend": weekly_stats
    }

@router.get("/fee-stats")
async def get_fee_statistics(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get fee statistics
    """
    # Fee collection status
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='PAID').count()
    pending_invoices = Invoice.objects.filter(status='PENDING').count()
    overdue_invoices = Invoice.objects.filter(
        status='PENDING',
        due_date__lt=date.today()
    ).count()
    
    # Revenue by month (last 6 months)
    revenue_by_month = []
    for i in range(6):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_revenue = Invoice.objects.filter(
            status='PAID',
            paid_date__gte=month_start,
            paid_date__lt=month_end
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        revenue_by_month.append({
            "month": month_start.strftime('%Y-%m'),
            "revenue": month_revenue
        })
    
    return {
        "collection_status": {
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "pending_invoices": pending_invoices,
            "overdue_invoices": overdue_invoices
        },
        "revenue_by_month": revenue_by_month
    }

@router.get("/teacher-stats")
async def get_teacher_statistics(
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Get teacher statistics
    """
    # Teachers by specialization
    teachers_by_specialization = TeacherProfile.objects.values('specialization').annotate(
        count=Count('id')
    ).exclude(specialization__isnull=True)
    
    # Active vs Inactive teachers
    active_teachers = TeacherProfile.objects.filter(is_active=True).count()
    inactive_teachers = TeacherProfile.objects.filter(is_active=False).count()
    
    # Teachers by experience
    new_teachers = TeacherProfile.objects.filter(experience_years__lt=2).count()
    experienced_teachers = TeacherProfile.objects.filter(experience_years__gte=2).count()
    
    return {
        "teachers_by_specialization": list(teachers_by_specialization),
        "active_vs_inactive": {
            "active": active_teachers,
            "inactive": inactive_teachers
        },
        "experience_levels": {
            "new": new_teachers,
            "experienced": experienced_teachers
        }
    }
