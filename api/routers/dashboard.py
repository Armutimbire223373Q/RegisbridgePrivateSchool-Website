"""
Dashboard endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import (
    User, StudentProfile, TeacherProfile, Parent, GradeLevel, ClassRoom,
    Dormitory, Grade, AttendanceRecord, Invoice
)

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    stats = {
        "total_students": db.query(StudentProfile).count(),
        "total_teachers": db.query(TeacherProfile).count(),
        "total_parents": db.query(Parent).count(),
        "active_students": db.query(StudentProfile).filter(
            StudentProfile.academic_status == "ACTIVE"
        ).count(),
        "total_classes": db.query(ClassRoom).count(),
        "total_dormitories": db.query(Dormitory).count(),
        "total_invoices": db.query(Invoice).count(),
        "pending_invoices": db.query(Invoice).filter(
            Invoice.status == "PENDING"
        ).count(),
        "paid_invoices": db.query(Invoice).filter(
            Invoice.status == "PAID"
        ).count(),
    }
    
    return stats

@router.get("/student-stats")
async def get_student_stats(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get student statistics by grade level
    """
    student_stats = db.query(
        GradeLevel.name,
        func.count(StudentProfile.id).label('count')
    ).join(StudentProfile).group_by(GradeLevel.name).all()
    
    return {
        "by_grade_level": [
            {"grade_level": stat.name, "count": stat.count}
            for stat in student_stats
        ]
    }

@router.get("/attendance-stats")
async def get_attendance_stats(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get attendance statistics
    """
    attendance_stats = db.query(
        func.count(AttendanceRecord.id).label('total_records'),
        func.sum(func.case([(AttendanceRecord.status == "PRESENT", 1)], else_=0)).label('present'),
        func.sum(func.case([(AttendanceRecord.status == "ABSENT", 1)], else_=0)).label('absent'),
        func.sum(func.case([(AttendanceRecord.status == "LATE", 1)], else_=0)).label('late')
    ).first()
    
    return {
        "total_records": attendance_stats.total_records or 0,
        "present": attendance_stats.present or 0,
        "absent": attendance_stats.absent or 0,
        "late": attendance_stats.late or 0,
        "attendance_rate": (
            (attendance_stats.present or 0) / (attendance_stats.total_records or 1) * 100
        ) if attendance_stats.total_records else 0
    }

@router.get("/recent-activity")
async def get_recent_activity(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get recent activity
    """
    # This would typically include recent grades, attendance, etc.
    # For now, return a placeholder
    return {
        "recent_grades": [],
        "recent_attendance": [],
        "recent_invoices": []
    }