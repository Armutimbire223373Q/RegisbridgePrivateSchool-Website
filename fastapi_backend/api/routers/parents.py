"""
Parent management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q

from api.models import (
    ParentProfileCreate, ParentProfileUpdate, ParentProfileResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from parents.models import Parent
from students.models import StudentProfile
from users.models import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_parents(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    relationship: Optional[str] = Query(None),
    is_primary_contact: Optional[bool] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of parents with pagination and filtering
    """
    queryset = Parent.objects.select_related('user').prefetch_related('students').all()
    
    # Apply filters
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    if relationship:
        queryset = queryset.filter(relationship=relationship)
    
    if is_primary_contact is not None:
        queryset = queryset.filter(is_primary_contact=is_primary_contact)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    parents = []
    for parent in page_obj:
        students = []
        for student in parent.students.all():
            students.append({
                "id": student.id,
                "admission_number": student.admission_number,
                "user": {
                    "id": student.user.id,
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name,
                    "email": student.user.email
                }
            })
        
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
            "students": students,
            "created_at": parent.created_at,
            "updated_at": parent.updated_at
        })
    
    return PaginatedResponse(
        data=parents,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/{parent_id}", response_model=ParentProfileResponse)
async def get_parent(
    parent_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get a specific parent by ID
    """
    try:
        parent = Parent.objects.select_related('user').prefetch_related('students').get(id=parent_id)
    except Parent.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    students = []
    for student in parent.students.all():
        students.append({
            "id": student.id,
            "admission_number": student.admission_number,
            "user": {
                "id": student.user.id,
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
                "email": student.user.email
            }
        })
    
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
        students=students,
        created_at=parent.created_at,
        updated_at=parent.updated_at
    )

@router.post("/", response_model=ParentProfileResponse)
async def create_parent(
    parent_data: ParentProfileCreate,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Create a new parent profile
    """
    try:
        # Check if user exists
        user = User.objects.get(id=parent_data.user_id)
        if user.role != "PARENT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have PARENT role"
            )
        
        # Check if parent profile already exists
        if Parent.objects.filter(user=user).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent profile already exists for this user"
            )
        
        # Validate students if provided
        students = []
        if parent_data.student_ids:
            for student_id in parent_data.student_ids:
                try:
                    student = StudentProfile.objects.get(id=student_id)
                    students.append(student)
                except StudentProfile.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Student with ID {student_id} not found"
                    )
        
        # Create parent profile
        parent = Parent.objects.create(
            user=user,
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
        
        # Add students to parent
        if students:
            parent.students.set(students)
        
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
            students=[{
                "id": student.id,
                "admission_number": student.admission_number,
                "user": {
                    "id": student.user.id,
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name,
                    "email": student.user.email
                }
            } for student in parent.students.all()],
            created_at=parent.created_at,
            updated_at=parent.updated_at
        )
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/{parent_id}", response_model=ParentProfileResponse)
async def update_parent(
    parent_id: int,
    parent_data: ParentProfileUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Update a parent profile
    """
    try:
        parent = Parent.objects.get(id=parent_id)
    except Parent.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
    
    # Update fields
    update_data = parent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parent, field, value)
    
    parent.save()
    
    students = []
    for student in parent.students.all():
        students.append({
            "id": student.id,
            "admission_number": student.admission_number,
            "user": {
                "id": student.user.id,
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
                "email": student.user.email
            }
        })
    
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
        students=students,
        created_at=parent.created_at,
        updated_at=parent.updated_at
    )

@router.delete("/{parent_id}")
async def delete_parent(
    parent_id: int,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Delete a parent profile
    """
    try:
        parent = Parent.objects.get(id=parent_id)
        parent.delete()
        return {"message": "Parent deleted successfully"}
    except Parent.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )
