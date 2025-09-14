"""
Teacher management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.models import (
    TeacherProfileCreate, TeacherProfileUpdate, TeacherProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import TeacherProfile, User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_teachers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of teachers with pagination and filtering
    """
    query = db.query(TeacherProfile).join(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                TeacherProfile.employee_id.contains(search),
                User.email.contains(search)
            )
        )
    
    if specialization:
        query = query.filter(TeacherProfile.specialization.contains(specialization))
    
    if is_active is not None:
        query = query.filter(TeacherProfile.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    teachers_query = query.offset(offset).limit(size).all()
    
    teachers = []
    for teacher in teachers_query:
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
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=teachers,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.get("/{teacher_id}", response_model=TeacherProfileResponse)
async def get_teacher(
    teacher_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get a specific teacher by ID
    """
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
    if not teacher:
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
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Create a new teacher profile
    """
    # Check if user exists
    user = db.query(User).filter(User.id == teacher_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != "TEACHER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have TEACHER role"
        )
    
    # Check if teacher profile already exists
    existing_teacher = db.query(TeacherProfile).filter(TeacherProfile.user_id == user.id).first()
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher profile already exists for this user"
        )
    
    # Check if employee ID is unique
    existing_employee = db.query(TeacherProfile).filter(
        TeacherProfile.employee_id == teacher_data.employee_id
    ).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    
    # Create teacher profile
    teacher = TeacherProfile(
        user_id=teacher_data.user_id,
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
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
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

@router.put("/{teacher_id}", response_model=TeacherProfileResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Update a teacher profile
    """
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Update fields
    update_data = teacher_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    db.commit()
    db.refresh(teacher)
    
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
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Delete a teacher profile
    """
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    db.delete(teacher)
    db.commit()
    
    return {"message": "Teacher deleted successfully"}