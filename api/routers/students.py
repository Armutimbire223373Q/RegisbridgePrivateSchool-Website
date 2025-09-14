"""
Student management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.models import (
    StudentProfileCreate, StudentProfileUpdate, StudentProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import StudentProfile, GradeLevel, ClassRoom, Dormitory, User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_students(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    academic_status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"])),
    db: Session = Depends(get_db)
):
    """
    Get list of students with pagination and filtering
    """
    query = db.query(StudentProfile).join(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                StudentProfile.admission_number.contains(search),
                User.email.contains(search)
            )
        )
    
    if grade_level:
        query = query.filter(StudentProfile.grade_level_id == grade_level)
    
    if academic_status:
        query = query.filter(StudentProfile.academic_status == academic_status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    students_query = query.offset(offset).limit(size).all()
    
    students = []
    for student in students_query:
        students.append({
            "id": student.id,
            "user": {
                "id": student.user.id,
                "username": student.user.username,
                "email": student.user.email,
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
                "is_active": student.user.is_active
            },
            "admission_number": student.admission_number,
            "grade_level": {
                "id": student.grade_level.id,
                "name": student.grade_level.name,
                "level": student.grade_level.level
            },
            "classroom": {
                "id": student.classroom.id,
                "name": student.classroom.name,
                "code": student.classroom.code
            } if student.classroom else None,
            "dormitory": {
                "id": student.dormitory.id,
                "name": student.dormitory.name
            } if student.dormitory else None,
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "blood_group": student.blood_group,
            "nationality": student.nationality,
            "enrollment_date": student.enrollment_date,
            "expected_graduation": student.expected_graduation,
            "previous_school": student.previous_school,
            "academic_status": student.academic_status,
            "medical_conditions": student.medical_conditions,
            "allergies": student.allergies,
            "is_boarder": student.is_boarder,
            "created_at": student.created_at,
            "updated_at": student.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=students,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.get("/{student_id}", response_model=StudentProfileResponse)
async def get_student(
    student_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"])),
    db: Session = Depends(get_db)
):
    """
    Get a specific student by ID
    """
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return StudentProfileResponse(
        id=student.id,
        user={
            "id": student.user.id,
            "username": student.user.username,
            "email": student.user.email,
            "first_name": student.user.first_name,
            "last_name": student.user.last_name,
            "role": student.user.role,
            "is_active": student.user.is_active,
            "date_joined": student.user.date_joined,
            "last_login": student.user.last_login
        },
        admission_number=student.admission_number,
        grade_level={
            "id": student.grade_level.id,
            "name": student.grade_level.name,
            "level": student.grade_level.level
        },
        classroom={
            "id": student.classroom.id,
            "name": student.classroom.name,
            "code": student.classroom.code
        } if student.classroom else None,
        dormitory={
            "id": student.dormitory.id,
            "name": student.dormitory.name
        } if student.dormitory else None,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        blood_group=student.blood_group,
        nationality=student.nationality,
        enrollment_date=student.enrollment_date,
        expected_graduation=student.expected_graduation,
        previous_school=student.previous_school,
        academic_status=student.academic_status,
        medical_conditions=student.medical_conditions,
        allergies=student.allergies,
        is_boarder=student.is_boarder,
        created_at=student.created_at,
        updated_at=student.updated_at
    )

@router.post("/", response_model=StudentProfileResponse)
async def create_student(
    student_data: StudentProfileCreate,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Create a new student profile
    """
    # Check if user exists
    user = db.query(User).filter(User.id == student_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have STUDENT role"
        )
    
    # Check if student profile already exists
    existing_student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user"
        )
    
    # Check if admission number is unique
    existing_admission = db.query(StudentProfile).filter(
        StudentProfile.admission_number == student_data.admission_number
    ).first()
    if existing_admission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admission number already exists"
        )
    
    # Validate grade level
    grade_level = db.query(GradeLevel).filter(GradeLevel.id == student_data.grade_level_id).first()
    if not grade_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade level not found"
        )
    
    # Validate classroom if provided
    classroom = None
    if student_data.classroom_id:
        classroom = db.query(ClassRoom).filter(ClassRoom.id == student_data.classroom_id).first()
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found"
            )
    
    # Validate dormitory if provided
    dormitory = None
    if student_data.dormitory_id:
        dormitory = db.query(Dormitory).filter(Dormitory.id == student_data.dormitory_id).first()
        if not dormitory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dormitory not found"
            )
    
    # Create student profile
    student = StudentProfile(
        user_id=student_data.user_id,
        admission_number=student_data.admission_number,
        grade_level_id=student_data.grade_level_id,
        classroom_id=student_data.classroom_id,
        dormitory_id=student_data.dormitory_id,
        date_of_birth=student_data.date_of_birth,
        gender=student_data.gender,
        blood_group=student_data.blood_group,
        nationality=student_data.nationality,
        enrollment_date=student_data.enrollment_date,
        expected_graduation=student_data.expected_graduation,
        previous_school=student_data.previous_school,
        academic_status=student_data.academic_status,
        medical_conditions=student_data.medical_conditions,
        allergies=student_data.allergies,
        is_boarder=student_data.is_boarder
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return StudentProfileResponse(
        id=student.id,
        user={
            "id": student.user.id,
            "username": student.user.username,
            "email": student.user.email,
            "first_name": student.user.first_name,
            "last_name": student.user.last_name,
            "role": student.user.role,
            "is_active": student.user.is_active,
            "date_joined": student.user.date_joined,
            "last_login": student.user.last_login
        },
        admission_number=student.admission_number,
        grade_level={
            "id": student.grade_level.id,
            "name": student.grade_level.name,
            "level": student.grade_level.level
        },
        classroom={
            "id": student.classroom.id,
            "name": student.classroom.name,
            "code": student.classroom.code
        } if student.classroom else None,
        dormitory={
            "id": student.dormitory.id,
            "name": student.dormitory.name
        } if student.dormitory else None,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        blood_group=student.blood_group,
        nationality=student.nationality,
        enrollment_date=student.enrollment_date,
        expected_graduation=student.expected_graduation,
        previous_school=student.previous_school,
        academic_status=student.academic_status,
        medical_conditions=student.medical_conditions,
        allergies=student.allergies,
        is_boarder=student.is_boarder,
        created_at=student.created_at,
        updated_at=student.updated_at
    )

@router.put("/{student_id}", response_model=StudentProfileResponse)
async def update_student(
    student_id: int,
    student_data: StudentProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Update a student profile
    """
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    update_data = student_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    
    return StudentProfileResponse(
        id=student.id,
        user={
            "id": student.user.id,
            "username": student.user.username,
            "email": student.user.email,
            "first_name": student.user.first_name,
            "last_name": student.user.last_name,
            "role": student.user.role,
            "is_active": student.user.is_active,
            "date_joined": student.user.date_joined,
            "last_login": student.user.last_login
        },
        admission_number=student.admission_number,
        grade_level={
            "id": student.grade_level.id,
            "name": student.grade_level.name,
            "level": student.grade_level.level
        },
        classroom={
            "id": student.classroom.id,
            "name": student.classroom.name,
            "code": student.classroom.code
        } if student.classroom else None,
        dormitory={
            "id": student.dormitory.id,
            "name": student.dormitory.name
        } if student.dormitory else None,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        blood_group=student.blood_group,
        nationality=student.nationality,
        enrollment_date=student.enrollment_date,
        expected_graduation=student.expected_graduation,
        previous_school=student.previous_school,
        academic_status=student.academic_status,
        medical_conditions=student.medical_conditions,
        allergies=student.allergies,
        is_boarder=student.is_boarder,
        created_at=student.created_at,
        updated_at=student.updated_at
    )

@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Delete a student profile
    """
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    db.delete(student)
    db.commit()
    
    return {"message": "Student deleted successfully"}