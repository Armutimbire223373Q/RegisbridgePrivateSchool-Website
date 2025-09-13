"""
Fee management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from datetime import date

from api.models import (
    FeeStructureCreate, FeeStructureUpdate, FeeStructureResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from fees.models import FeeStructure, Invoice
from students.models import StudentProfile, GradeLevel
from grades.models import Term

router = APIRouter()

@router.get("/structures", response_model=PaginatedResponse)
async def get_fee_structures(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    grade_level_id: Optional[int] = Query(None),
    fee_type: Optional[str] = Query(None),
    term_id: Optional[int] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of fee structures with pagination and filtering
    """
    queryset = FeeStructure.objects.select_related('grade_level', 'term').all()
    
    # Apply filters
    if grade_level_id:
        queryset = queryset.filter(grade_level_id=grade_level_id)
    
    if fee_type:
        queryset = queryset.filter(fee_type__icontains=fee_type)
    
    if term_id:
        queryset = queryset.filter(term_id=term_id)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    structures = []
    for structure in page_obj:
        structures.append({
            "id": structure.id,
            "grade_level": {
                "id": structure.grade_level.id,
                "name": structure.grade_level.name,
                "level": structure.grade_level.level
            },
            "fee_type": structure.fee_type,
            "term": {
                "id": structure.term.id,
                "name": structure.name,
                "start_date": structure.term.start_date,
                "end_date": structure.term.end_date
            },
            "amount": structure.amount,
            "description": structure.description,
            "due_date": structure.due_date,
            "created_at": structure.created_at,
            "updated_at": structure.updated_at
        })
    
    return PaginatedResponse(
        data=structures,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/structures/{structure_id}", response_model=FeeStructureResponse)
async def get_fee_structure(
    structure_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get a specific fee structure by ID
    """
    try:
        structure = FeeStructure.objects.select_related('grade_level', 'term').get(id=structure_id)
    except FeeStructure.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )
    
    return FeeStructureResponse(
        id=structure.id,
        grade_level={
            "id": structure.grade_level.id,
            "name": structure.grade_level.name,
            "level": structure.grade_level.level
        },
        fee_type=structure.fee_type,
        term={
            "id": structure.term.id,
            "name": structure.term.name,
            "start_date": structure.term.start_date,
            "end_date": structure.term.end_date
        },
        amount=structure.amount,
        description=structure.description,
        due_date=structure.due_date,
        created_at=structure.created_at,
        updated_at=structure.updated_at
    )

@router.post("/structures", response_model=FeeStructureResponse)
async def create_fee_structure(
    structure_data: FeeStructureCreate,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Create a new fee structure
    """
    try:
        # Check if grade level exists
        grade_level = GradeLevel.objects.get(id=structure_data.grade_level_id)
        
        # Check if term exists
        term = Term.objects.get(id=structure_data.term_id)
        
        # Create fee structure
        structure = FeeStructure.objects.create(
            grade_level=grade_level,
            fee_type=structure_data.fee_type,
            term=term,
            amount=structure_data.amount,
            description=structure_data.description,
            due_date=structure_data.due_date
        )
        
        return FeeStructureResponse(
            id=structure.id,
            grade_level={
                "id": structure.grade_level.id,
                "name": structure.grade_level.name,
                "level": structure.grade_level.level
            },
            fee_type=structure.fee_type,
            term={
                "id": structure.term.id,
                "name": structure.term.name,
                "start_date": structure.term.start_date,
                "end_date": structure.term.end_date
            },
            amount=structure.amount,
            description=structure.description,
            due_date=structure.due_date,
            created_at=structure.created_at,
            updated_at=structure.updated_at
        )
        
    except GradeLevel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade level not found"
        )
    except Term.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found"
        )

@router.put("/structures/{structure_id}", response_model=FeeStructureResponse)
async def update_fee_structure(
    structure_id: int,
    structure_data: FeeStructureUpdate,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Update a fee structure
    """
    try:
        structure = FeeStructure.objects.get(id=structure_id)
    except FeeStructure.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )
    
    # Update fields
    update_data = structure_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(structure, field, value)
    
    structure.save()
    
    return FeeStructureResponse(
        id=structure.id,
        grade_level={
            "id": structure.grade_level.id,
            "name": structure.grade_level.name,
            "level": structure.grade_level.level
        },
        fee_type=structure.fee_type,
        term={
            "id": structure.term.id,
            "name": structure.term.name,
            "start_date": structure.term.start_date,
            "end_date": structure.term.end_date
        },
        amount=structure.amount,
        description=structure.description,
        due_date=structure.due_date,
        created_at=structure.created_at,
        updated_at=structure.updated_at
    )

@router.delete("/structures/{structure_id}")
async def delete_fee_structure(
    structure_id: int,
    current_user = Depends(require_roles(["ADMIN"]))
):
    """
    Delete a fee structure
    """
    try:
        structure = FeeStructure.objects.get(id=structure_id)
        structure.delete()
        return {"message": "Fee structure deleted successfully"}
    except FeeStructure.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )

@router.get("/invoices", response_model=PaginatedResponse)
async def get_invoices(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of invoices with pagination and filtering
    """
    queryset = Invoice.objects.select_related('student__user').all()
    
    # Apply filters
    if student_id:
        queryset = queryset.filter(student_id=student_id)
    
    if status:
        queryset = queryset.filter(status=status)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    invoices = []
    for invoice in page_obj:
        invoices.append({
            "id": invoice.id,
            "student": {
                "id": invoice.student.id,
                "admission_number": invoice.student.admission_number,
                "user": {
                    "id": invoice.student.user.id,
                    "first_name": invoice.student.user.first_name,
                    "last_name": invoice.student.user.last_name,
                    "email": invoice.student.user.email
                }
            },
            "invoice_number": invoice.invoice_number,
            "amount": invoice.amount,
            "status": invoice.status,
            "due_date": invoice.due_date,
            "paid_date": invoice.paid_date,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        })
    
    return PaginatedResponse(
        data=invoices,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/statistics/overview")
async def get_fee_statistics(
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get fee statistics overview
    """
    # Calculate total fees
    total_fees = FeeStructure.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate paid invoices
    paid_invoices = Invoice.objects.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate pending invoices
    pending_invoices = Invoice.objects.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate overdue invoices
    overdue_invoices = Invoice.objects.filter(
        status='PENDING',
        due_date__lt=date.today()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return {
        "total_fees": total_fees,
        "paid_invoices": paid_invoices,
        "pending_invoices": pending_invoices,
        "overdue_invoices": overdue_invoices,
        "collection_rate": round((paid_invoices / total_fees * 100) if total_fees > 0 else 0, 2)
    }
