"""
Teacher management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q

from api.models import (
    TeacherProfileCreate, TeacherProfileUpdate, TeacherProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from teachers.models import TeacherProfile
from users.models import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_teachers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of teachers with pagination and filtering
    """
    queryset = TeacherProfile.objects.select_related('user').all()
    
    # Apply filters
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if specialization:
        queryset = queryset.filter(specialization__icontains=specialization)
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    teachers = []
    for teacher in page_obj:
        teachers.append({
            "id": teacher.id,
            "user": {
                "id": teacher.user.id,
                "username": teacher.user.username,
                "email": teacher.user.email,
                "first_name": teacher.user.first_name,
                "last_name": teacher.user.last_name,
                "is_active": teacher.user.is_active
            },
            "employee_id": teacher.employee_id,
            "phone_number": teacher.phone_number,
            "address": teacher.address,
            "city": teacher.city,
            "postal_code": teacher.postal_code,
            "country": teacher.country,
            "qualification": teacher.qualification,
            "specialization": teacher.specialization,
            "experience_years": teacher.experience_years,
            "salary": teacher.salary,
            "hire_date": teacher.hire_date,
            "is_active": teacher.is_active,
            "created_at": teacher.created_at,
            "updated_at": teacher.updated_at
        })
    
    return PaginatedResponse(
        data=teachers,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/{teacher_id}", response_model=TeacherProfileResponse)
async def get_teacher(
    teacher_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get a specific teacher by ID
    """
    try:
        teacher = TeacherProfile.objects.select_related('user').get(id=teacher_id)
    except TeacherProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return TeacherProfileResponse(
        id=teacher.id,
        user={
            "id": teacher.user.id,
            "username": teacher.user.username,
            "email": teacher.user.email,
            "first_name": teacher.user.first_name,
            "last_name": teacher.user.last_name,
            "role": teacher.user.role,
            "is_active": teacher.user.is_active,
            "date_joined": teacher.user.date_joined,
            "last_login": teacher.user.last_login
        },
        employee_id=teacher.employee_id,
        phone_number=teacher.phone_number,
        address=teacher.address,
        city=teacher.city,
        postal_code=teacher.postal_code,
        country=teacher.country,
        qualification=teacher.qualification,
        specialization=teacher.specialization,
        experience_years=teacher.experience_years,
        salary=teacher.salary,
        hire_date=teacher.hire_date,
        is_active=teacher.is_active,
        created_at=teacher.created_at,
        updated_at=teacher.updated_at
    )

@router.post("/", response_model=TeacherProfileResponse)
async def create_teacher(
    teacher_data: TeacherProfileCreate,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Create a new teacher profile
    """
    try:
        # Check if user exists
        user = User.objects.get(id=teacher_data.user_id)
        if user.role != "TEACHER":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have TEACHER role"
            )
        
        # Check if teacher profile already exists
        if TeacherProfile.objects.filter(user=user).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher profile already exists for this user"
            )
        
        # Check if employee ID is unique
        if TeacherProfile.objects.filter(employee_id=teacher_data.employee_id).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists"
            )
        
        # Create teacher profile
        teacher = TeacherProfile.objects.create(
            user=user,
            employee_id=teacher_data.employee_id,
            phone_number=teacher_data.phone_number,
            address=teacher_data.address,
            city=teacher_data.city,
            postal_code=teacher_data.postal_code,
            country=teacher_data.country,
            qualification=teacher_data.qualification,
            specialization=teacher_data.specialization,
            experience_years=teacher_data.experience_years,
            salary=teacher_data.salary,
            hire_date=teacher_data.hire_date,
            is_active=teacher_data.is_active
        )
        
        return TeacherProfileResponse(
            id=teacher.id,
            user={
                "id": teacher.user.id,
                "username": teacher.user.username,
                "email": teacher.user.email,
                "first_name": teacher.user.first_name,
                "last_name": teacher.user.last_name,
                "role": teacher.user.role,
                "is_active": teacher.user.is_active,
                "date_joined": teacher.user.date_joined,
                "last_login": teacher.user.last_login
            },
            employee_id=teacher.employee_id,
            phone_number=teacher.phone_number,
            address=teacher.address,
            city=teacher.city,
            postal_code=teacher.postal_code,
            country=teacher.country,
            qualification=teacher.qualification,
            specialization=teacher.specialization,
            experience_years=teacher.experience_years,
            salary=teacher.salary,
            hire_date=teacher.hire_date,
            is_active=teacher.is_active,
            created_at=teacher.created_at,
            updated_at=teacher.updated_at
        )
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/{teacher_id}", response_model=TeacherProfileResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Update a teacher profile
    """
    try:
        teacher = TeacherProfile.objects.get(id=teacher_id)
    except TeacherProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Update fields
    update_data = teacher_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    teacher.save()
    
    return TeacherProfileResponse(
        id=teacher.id,
        user={
            "id": teacher.user.id,
            "username": teacher.user.username,
            "email": teacher.user.email,
            "first_name": teacher.user.first_name,
            "last_name": teacher.user.last_name,
            "role": teacher.user.role,
            "is_active": teacher.user.is_active,
            "date_joined": teacher.user.date_joined,
            "last_login": teacher.user.last_login
        },
        employee_id=teacher.employee_id,
        phone_number=teacher.phone_number,
        address=teacher.address,
        city=teacher.city,
        postal_code=teacher.postal_code,
        country=teacher.country,
        qualification=teacher.qualification,
        specialization=teacher.specialization,
        experience_years=teacher.experience_years,
        salary=teacher.salary,
        hire_date=teacher.hire_date,
        is_active=teacher.is_active,
        created_at=teacher.created_at,
        updated_at=teacher.updated_at
    )

@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Delete a teacher profile
    """
    try:
        teacher = TeacherProfile.objects.get(id=teacher_id)
        teacher.delete()
        return {"message": "Teacher deleted successfully"}
    except TeacherProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
