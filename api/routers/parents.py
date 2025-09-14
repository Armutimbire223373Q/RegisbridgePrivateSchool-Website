"""
Parent management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.models import (
    ParentProfileCreate, ParentProfileUpdate, ParentProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import Parent, StudentProfile, User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_parents(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    relationship: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of parents with pagination and filtering
    """
    query = db.query(Parent).join(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search),
                Parent.phone_number.contains(search)
            )
        )
    
    if relationship:
        query = query.filter(Parent.relationship == relationship)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    parents_query = query.offset(offset).limit(size).all()
    
    parents = []
    for parent in parents_query:
        parents.append({
            "id": parent.id,
            "user": {
                "id": parent.user.id,
                "username": parent.user.username,
                "email": parent.user.email,
                "first_name": parent.user.first_name,
                "last_name": parent.user.last_name,
                "is_active": parent.user.is_active
            },
            "relationship": parent.relationship,
            "phone_number": parent.phone_number,
            "alternative_phone": parent.alternative_phone,
            "address": parent.address,
            "city": parent.city,
            "postal_code": parent.postal_code,
            "country": parent.country,
            "emergency_contact_name": parent.emergency_contact_name,
            "emergency_contact_phone": parent.emergency_contact_phone,
            "emergency_contact_relationship": parent.emergency_contact_relationship,
            "occupation": parent.occupation,
            "employer": parent.employer,
            "is_primary_contact": parent.is_primary_contact,
            "students": [
                {
                    "id": student.id,
                    "admission_number": student.admission_number,
                    "user": {
                        "first_name": student.user.first_name,
                        "last_name": student.user.last_name
                    }
                } for student in parent.students
            ],
            "created_at": parent.created_at,
            "updated_at": parent.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=parents,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.get("/{parent_id}", response_model=ParentProfileResponse)
async def get_parent(
    parent_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Get a specific parent by ID
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    return ParentProfileResponse(
        id=parent.id,
        user={
            "id": parent.user.id,
            "username": parent.user.username,
            "email": parent.user.email,
            "first_name": parent.user.first_name,
            "last_name": parent.user.last_name,
            "role": parent.user.role,
            "is_active": parent.user.is_active,
            "date_joined": parent.user.date_joined,
            "last_login": parent.user.last_login
        },
        relationship=parent.relationship,
        phone_number=parent.phone_number,
        alternative_phone=parent.alternative_phone,
        address=parent.address,
        city=parent.city,
        postal_code=parent.postal_code,
        country=parent.country,
        emergency_contact_name=parent.emergency_contact_name,
        emergency_contact_phone=parent.emergency_contact_phone,
        emergency_contact_relationship=parent.emergency_contact_relationship,
        occupation=parent.occupation,
        employer=parent.employer,
        is_primary_contact=parent.is_primary_contact,
        students=[
            {
                "id": student.id,
                "admission_number": student.admission_number,
                "user": {
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name
                }
            } for student in parent.students
        ],
        created_at=parent.created_at,
        updated_at=parent.updated_at
    )

@router.post("/", response_model=ParentProfileResponse)
async def create_parent(
    parent_data: ParentProfileCreate,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Create a new parent profile
    """
    # Check if user exists
    user = db.query(User).filter(User.id == parent_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != "PARENT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have PARENT role"
        )
    
    # Check if parent profile already exists
    existing_parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if existing_parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent profile already exists for this user"
        )
    
    # Create parent profile
    parent = Parent(
        user_id=parent_data.user_id,
        relationship=parent_data.relationship,
        phone_number=parent_data.phone_number,
        alternative_phone=parent_data.alternative_phone,
        address=parent_data.address,
        city=parent_data.city,
        postal_code=parent_data.postal_code,
        country=parent_data.country,
        emergency_contact_name=parent_data.emergency_contact_name,
        emergency_contact_phone=parent_data.emergency_contact_phone,
        emergency_contact_relationship=parent_data.emergency_contact_relationship,
        occupation=parent_data.occupation,
        employer=parent_data.employer,
        is_primary_contact=parent_data.is_primary_contact
    )
    
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    return ParentProfileResponse(
        id=parent.id,
        user={
            "id": parent.user.id,
            "username": parent.user.username,
            "email": parent.user.email,
            "first_name": parent.user.first_name,
            "last_name": parent.user.last_name,
            "role": parent.user.role,
            "is_active": parent.user.is_active,
            "date_joined": parent.user.date_joined,
            "last_login": parent.user.last_login
        },
        relationship=parent.relationship,
        phone_number=parent.phone_number,
        alternative_phone=parent.alternative_phone,
        address=parent.address,
        city=parent.city,
        postal_code=parent.postal_code,
        country=parent.country,
        emergency_contact_name=parent.emergency_contact_name,
        emergency_contact_phone=parent.emergency_contact_phone,
        emergency_contact_relationship=parent.emergency_contact_relationship,
        occupation=parent.occupation,
        employer=parent.employer,
        is_primary_contact=parent.is_primary_contact,
        students=[],
        created_at=parent.created_at,
        updated_at=parent.updated_at
    )

@router.put("/{parent_id}", response_model=ParentProfileResponse)
async def update_parent(
    parent_id: int,
    parent_data: ParentProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Update a parent profile
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    # Update fields
    update_data = parent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parent, field, value)
    
    db.commit()
    db.refresh(parent)
    
    return ParentProfileResponse(
        id=parent.id,
        user={
            "id": parent.user.id,
            "username": parent.user.username,
            "email": parent.user.email,
            "first_name": parent.user.first_name,
            "last_name": parent.user.last_name,
            "role": parent.user.role,
            "is_active": parent.user.is_active,
            "date_joined": parent.user.date_joined,
            "last_login": parent.user.last_login
        },
        relationship=parent.relationship,
        phone_number=parent.phone_number,
        alternative_phone=parent.alternative_phone,
        address=parent.address,
        city=parent.city,
        postal_code=parent.postal_code,
        country=parent.country,
        emergency_contact_name=parent.emergency_contact_name,
        emergency_contact_phone=parent.emergency_contact_phone,
        emergency_contact_relationship=parent.emergency_contact_relationship,
        occupation=parent.occupation,
        employer=parent.employer,
        is_primary_contact=parent.is_primary_contact,
        students=[
            {
                "id": student.id,
                "admission_number": student.admission_number,
                "user": {
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name
                }
            } for student in parent.students
        ],
        created_at=parent.created_at,
        updated_at=parent.updated_at
    )

@router.delete("/{parent_id}")
async def delete_parent(
    parent_id: int,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Delete a parent profile
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    db.delete(parent)
    db.commit()
    
    return {"message": "Parent deleted successfully"}

@router.post("/{parent_id}/students/{student_id}")
async def add_student_to_parent(
    parent_id: int,
    student_id: int,
    current_user = Depends(require_roles(["ADMIN", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Add a student to a parent
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Add student to parent
    if student not in parent.students:
        parent.students.append(student)
        db.commit()
    
    return {"message": "Student added to parent successfully"}

@router.delete("/{parent_id}/students/{student_id}")
async def remove_student_from_parent(
    parent_id: int,
    student_id: int,
    current_user = Depends(require_roles(["ADMIN", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Remove a student from a parent
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Remove student from parent
    if student in parent.students:
        parent.students.remove(student)
        db.commit()
    
    return {"message": "Student removed from parent successfully"}