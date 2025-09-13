"""
Student management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q

from api.models import (
    StudentProfileCreate, StudentProfileUpdate, StudentProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from students.models import StudentProfile, GradeLevel, ClassRoom, Dormitory
from users.models import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_students(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    academic_status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"]))
):
    """
    Get list of students with pagination and filtering
    """
    queryset = StudentProfile.objects.select_related('user', 'grade_level', 'classroom', 'dormitory').all()
    
    # Apply filters
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(admission_number__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if grade_level:
        queryset = queryset.filter(grade_level_id=grade_level)
    
    if academic_status:
        queryset = queryset.filter(academic_status=academic_status)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    students = []
    for student in page_obj:
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
    
    return PaginatedResponse(
        data=students,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/{student_id}", response_model=StudentProfileResponse)
async def get_student(
    student_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"]))
):
    """
    Get a specific student by ID
    """
    try:
        student = StudentProfile.objects.select_related(
            'user', 'grade_level', 'classroom', 'dormitory'
        ).get(id=student_id)
    except StudentProfile.DoesNotExist:
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
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Create a new student profile
    """
    try:
        # Check if user exists
        user = User.objects.get(id=student_data.user_id)
        if user.role != "STUDENT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have STUDENT role"
            )
        
        # Check if student profile already exists
        if StudentProfile.objects.filter(user=user).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student profile already exists for this user"
            )
        
        # Check if admission number is unique
        if StudentProfile.objects.filter(admission_number=student_data.admission_number).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admission number already exists"
            )
        
        # Validate grade level
        grade_level = GradeLevel.objects.get(id=student_data.grade_level_id)
        
        # Validate classroom if provided
        classroom = None
        if student_data.classroom_id:
            classroom = ClassRoom.objects.get(id=student_data.classroom_id)
        
        # Validate dormitory if provided
        dormitory = None
        if student_data.dormitory_id:
            dormitory = Dormitory.objects.get(id=student_data.dormitory_id)
        
        # Create student profile
        student = StudentProfile.objects.create(
            user=user,
            admission_number=student_data.admission_number,
            grade_level=grade_level,
            classroom=classroom,
            dormitory=dormitory,
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
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except GradeLevel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade level not found"
        )
    except ClassRoom.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    except Dormitory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dormitory not found"
        )

@router.put("/{student_id}", response_model=StudentProfileResponse)
async def update_student(
    student_id: int,
    student_data: StudentProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Update a student profile
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    update_data = student_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    student.save()
    
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
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Delete a student profile
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
        student.delete()
        return {"message": "Student deleted successfully"}
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
