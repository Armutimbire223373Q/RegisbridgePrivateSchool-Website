"""
Attendance management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import date, datetime

from api.models import (
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from core_attendance.models import AttendanceRecord, AttendanceSession
from students.models import StudentProfile
from classes.models import ClassRoom

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_attendance_records(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of attendance records with pagination and filtering
    """
    queryset = AttendanceRecord.objects.select_related('student__user', 'session__classroom').all()
    
    # Apply filters
    if student_id:
        queryset = queryset.filter(student_id=student_id)
    
    if session_id:
        queryset = queryset.filter(session_id=session_id)
    
    if date_from:
        queryset = queryset.filter(session__date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(session__date__lte=date_to)
    
    if status:
        queryset = queryset.filter(status=status)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    records = []
    for record in page_obj:
        records.append({
            "id": record.id,
            "student": {
                "id": record.student.id,
                "admission_number": record.student.admission_number,
                "user": {
                    "id": record.student.user.id,
                    "first_name": record.student.user.first_name,
                    "last_name": record.student.user.last_name,
                    "email": record.student.user.email
                }
            },
            "session": {
                "id": record.session.id,
                "classroom": {
                    "id": record.session.classroom.id,
                    "name": record.session.classroom.name,
                    "code": record.session.classroom.code
                },
                "date": record.session.date,
                "start_time": record.session.start_time,
                "end_time": record.session.end_time
            },
            "status": record.status,
            "notes": record.notes,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        })
    
    return PaginatedResponse(
        data=records,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/{record_id}", response_model=AttendanceRecordResponse)
async def get_attendance_record(
    record_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get a specific attendance record by ID
    """
    try:
        record = AttendanceRecord.objects.select_related('student__user', 'session__classroom').get(id=record_id)
    except AttendanceRecord.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    return AttendanceRecordResponse(
        id=record.id,
        student={
            "id": record.student.id,
            "admission_number": record.student.admission_number,
            "user": {
                "id": record.student.user.id,
                "first_name": record.student.user.first_name,
                "last_name": record.student.user.last_name,
                "email": record.student.user.email
            }
        },
        session={
            "id": record.session.id,
            "classroom": {
                "id": record.session.classroom.id,
                "name": record.session.classroom.name,
                "code": record.session.classroom.code
            },
            "date": record.session.date,
            "start_time": record.session.start_time,
            "end_time": record.session.end_time
        },
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

@router.post("/", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    record_data: AttendanceRecordCreate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Create a new attendance record
    """
    try:
        # Check if student exists
        student = StudentProfile.objects.get(id=record_data.student_id)
        
        # Check if session exists
        session = AttendanceSession.objects.get(id=record_data.session_id)
        
        # Check if attendance record already exists for this student and session
        if AttendanceRecord.objects.filter(student=student, session=session).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance record already exists for this student and session"
            )
        
        # Create attendance record
        record = AttendanceRecord.objects.create(
            student=student,
            session=session,
            status=record_data.status,
            notes=record_data.notes
        )
        
        return AttendanceRecordResponse(
            id=record.id,
            student={
                "id": record.student.id,
                "admission_number": record.student.admission_number,
                "user": {
                    "id": record.student.user.id,
                    "first_name": record.student.user.first_name,
                    "last_name": record.student.user.last_name,
                    "email": record.student.user.email
                }
            },
            session={
                "id": record.session.id,
                "classroom": {
                    "id": record.session.classroom.id,
                    "name": record.session.classroom.name,
                    "code": record.session.classroom.code
                },
                "date": record.session.date,
                "start_time": record.session.start_time,
                "end_time": record.session.end_time
            },
            status=record.status,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
        
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    except AttendanceSession.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance session not found"
        )

@router.put("/{record_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    record_id: int,
    record_data: AttendanceRecordUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Update an attendance record
    """
    try:
        record = AttendanceRecord.objects.get(id=record_id)
    except AttendanceRecord.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update fields
    update_data = record_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    record.save()
    
    return AttendanceRecordResponse(
        id=record.id,
        student={
            "id": record.student.id,
            "admission_number": record.student.admission_number,
            "user": {
                "id": record.student.user.id,
                "first_name": record.student.user.first_name,
                "last_name": record.student.user.last_name,
                "email": record.student.user.email
            }
        },
        session={
            "id": record.session.id,
            "classroom": {
                "id": record.session.classroom.id,
                "name": record.session.classroom.name,
                "code": record.session.classroom.code
            },
            "date": record.session.date,
            "start_time": record.session.start_time,
            "end_time": record.session.end_time
        },
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

@router.delete("/{record_id}")
async def delete_attendance_record(
    record_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Delete an attendance record
    """
    try:
        record = AttendanceRecord.objects.get(id=record_id)
        record.delete()
        return {"message": "Attendance record deleted successfully"}
    except AttendanceRecord.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

@router.get("/statistics/student/{student_id}")
async def get_student_attendance_statistics(
    student_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "PARENT"]))
):
    """
    Get attendance statistics for a specific student
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    queryset = AttendanceRecord.objects.filter(student=student)
    
    if date_from:
        queryset = queryset.filter(session__date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(session__date__lte=date_to)
    
    # Calculate statistics
    total_records = queryset.count()
    present_count = queryset.filter(status="PRESENT").count()
    absent_count = queryset.filter(status="ABSENT").count()
    late_count = queryset.filter(status="LATE").count()
    excused_count = queryset.filter(status="EXCUSED").count()
    
    attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
    
    return {
        "student": {
            "id": student.id,
            "admission_number": student.admission_number,
            "user": {
                "id": student.user.id,
                "first_name": student.user.first_name,
                "last_name": student.user.last_name
            }
        },
        "statistics": {
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "excused_count": excused_count,
            "attendance_rate": round(attendance_rate, 2)
        }
    }
