"""
Attendance management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from api.models import (
    AttendanceSessionCreate, AttendanceSessionUpdate, AttendanceSessionResponse,
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import AttendanceSession, AttendanceRecord, StudentProfile, ClassRoom, User

router = APIRouter()

# Attendance Session endpoints
@router.get("/sessions", response_model=PaginatedResponse)
async def get_attendance_sessions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    classroom_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of attendance sessions with pagination and filtering
    """
    query = db.query(AttendanceSession)
    
    # Apply filters
    if classroom_id:
        query = query.filter(AttendanceSession.classroom_id == classroom_id)
    
    if date_from:
        query = query.filter(AttendanceSession.date >= date_from)
    
    if date_to:
        query = query.filter(AttendanceSession.date <= date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    sessions_query = query.offset(offset).limit(size).all()
    
    sessions = []
    for session in sessions_query:
        sessions.append({
            "id": session.id,
            "classroom": {
                "id": session.classroom.id,
                "name": session.classroom.name,
                "code": session.classroom.code
            },
            "date": session.date,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "notes": session.notes,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=sessions,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.post("/sessions", response_model=AttendanceSessionResponse)
async def create_attendance_session(
    session_data: AttendanceSessionCreate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Create a new attendance session
    """
    # Validate classroom
    classroom = db.query(ClassRoom).filter(ClassRoom.id == session_data.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Create attendance session
    session = AttendanceSession(
        classroom_id=session_data.classroom_id,
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        notes=session_data.notes
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return AttendanceSessionResponse(
        id=session.id,
        classroom={
            "id": session.classroom.id,
            "name": session.classroom.name,
            "code": session.classroom.code
        },
        date=session.date,
        start_time=session.start_time,
        end_time=session.end_time,
        notes=session.notes,
        created_at=session.created_at,
        updated_at=session.updated_at
    )

# Attendance Record endpoints
@router.get("/records", response_model=PaginatedResponse)
async def get_attendance_records(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of attendance records with pagination and filtering
    """
    query = db.query(AttendanceRecord).join(StudentProfile).join(User)
    
    # Apply filters
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    if session_id:
        query = query.filter(AttendanceRecord.session_id == session_id)
    
    if status:
        query = query.filter(AttendanceRecord.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    records_query = query.offset(offset).limit(size).all()
    
    records = []
    for record in records_query:
        records.append({
            "id": record.id,
            "student": {
                "id": record.student.id,
                "admission_number": record.student.admission_number,
                "user": {
                    "first_name": record.student.user.first_name,
                    "last_name": record.student.user.last_name
                }
            },
            "session": {
                "id": record.session.id,
                "date": record.session.date,
                "classroom": {
                    "name": record.session.classroom.name,
                    "code": record.session.classroom.code
                }
            },
            "status": record.status,
            "notes": record.notes,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=records,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.post("/records", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    record_data: AttendanceRecordCreate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Create a new attendance record
    """
    # Validate student
    student = db.query(StudentProfile).filter(StudentProfile.id == record_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Validate session
    session = db.query(AttendanceSession).filter(AttendanceSession.id == record_data.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance session not found"
        )
    
    # Check if record already exists
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == record_data.student_id,
        AttendanceRecord.session_id == record_data.session_id
    ).first()
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this student and session"
        )
    
    # Create attendance record
    record = AttendanceRecord(
        student_id=record_data.student_id,
        session_id=record_data.session_id,
        status=record_data.status,
        notes=record_data.notes
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return AttendanceRecordResponse(
        id=record.id,
        student={
            "id": record.student.id,
            "admission_number": record.student.admission_number,
            "user": {
                "first_name": record.student.user.first_name,
                "last_name": record.student.user.last_name
            }
        },
        session={
            "id": record.session.id,
            "date": record.session.date,
            "classroom": {
                "name": record.session.classroom.name,
                "code": record.session.classroom.code
            }
        },
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

@router.put("/records/{record_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    record_id: int,
    record_data: AttendanceRecordUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Update an attendance record
    """
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update fields
    update_data = record_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return AttendanceRecordResponse(
        id=record.id,
        student={
            "id": record.student.id,
            "admission_number": record.student.admission_number,
            "user": {
                "first_name": record.student.user.first_name,
                "last_name": record.student.user.last_name
            }
        },
        session={
            "id": record.session.id,
            "date": record.session.date,
            "classroom": {
                "name": record.session.classroom.name,
                "code": record.session.classroom.code
            }
        },
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

@router.delete("/records/{record_id}")
async def delete_attendance_record(
    record_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Delete an attendance record
    """
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    db.delete(record)
    db.commit()
    
    return {"message": "Attendance record deleted successfully"}