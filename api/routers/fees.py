"""
Fee management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from api.models import (
    FeeStructureCreate, FeeStructureUpdate, FeeStructureResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import FeeStructure, Invoice, StudentProfile, GradeLevel, Term, User

router = APIRouter()

# Fee Structure endpoints
@router.get("/structures", response_model=PaginatedResponse)
async def get_fee_structures(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    grade_level_id: Optional[int] = Query(None),
    fee_type: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of fee structures with pagination and filtering
    """
    query = db.query(FeeStructure)
    
    # Apply filters
    if grade_level_id:
        query = query.filter(FeeStructure.grade_level_id == grade_level_id)
    
    if fee_type:
        query = query.filter(FeeStructure.fee_type == fee_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    fee_structures_query = query.offset(offset).limit(size).all()
    
    fee_structures = []
    for fee_structure in fee_structures_query:
        fee_structures.append({
            "id": fee_structure.id,
            "grade_level": {
                "id": fee_structure.grade_level.id,
                "name": fee_structure.grade_level.name
            },
            "fee_type": fee_structure.fee_type,
            "term": {
                "id": fee_structure.term.id,
                "name": fee_structure.term.name
            },
            "amount": fee_structure.amount,
            "description": fee_structure.description,
            "due_date": fee_structure.due_date,
            "created_at": fee_structure.created_at,
            "updated_at": fee_structure.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=fee_structures,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.post("/structures", response_model=FeeStructureResponse)
async def create_fee_structure(
    fee_structure_data: FeeStructureCreate,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Create a new fee structure
    """
    # Validate grade level
    grade_level = db.query(GradeLevel).filter(GradeLevel.id == fee_structure_data.grade_level_id).first()
    if not grade_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade level not found"
        )
    
    # Validate term
    term = db.query(Term).filter(Term.id == fee_structure_data.term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found"
        )
    
    # Create fee structure
    fee_structure = FeeStructure(
        grade_level_id=fee_structure_data.grade_level_id,
        fee_type=fee_structure_data.fee_type,
        term_id=fee_structure_data.term_id,
        amount=fee_structure_data.amount,
        description=fee_structure_data.description,
        due_date=fee_structure_data.due_date
    )
    
    db.add(fee_structure)
    db.commit()
    db.refresh(fee_structure)
    
    return FeeStructureResponse(
        id=fee_structure.id,
        grade_level={
            "id": fee_structure.grade_level.id,
            "name": fee_structure.grade_level.name
        },
        fee_type=fee_structure.fee_type,
        term={
            "id": fee_structure.term.id,
            "name": fee_structure.term.name
        },
        amount=fee_structure.amount,
        description=fee_structure.description,
        due_date=fee_structure.due_date,
        created_at=fee_structure.created_at,
        updated_at=fee_structure.updated_at
    )

# Invoice endpoints
@router.get("/invoices", response_model=PaginatedResponse)
async def get_invoices(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Get list of invoices with pagination and filtering
    """
    query = db.query(Invoice).join(StudentProfile).join(User)
    
    # Apply filters
    if student_id:
        query = query.filter(Invoice.student_id == student_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    invoices_query = query.offset(offset).limit(size).all()
    
    invoices = []
    for invoice in invoices_query:
        invoices.append({
            "id": invoice.id,
            "student": {
                "id": invoice.student.id,
                "admission_number": invoice.student.admission_number,
                "user": {
                    "first_name": invoice.student.user.first_name,
                    "last_name": invoice.student.user.last_name
                }
            },
            "invoice_number": invoice.invoice_number,
            "amount": invoice.amount,
            "status": invoice.status,
            "due_date": invoice.due_date,
            "paid_date": invoice.paid_date,
            "payment_method": invoice.payment_method,
            "notes": invoice.notes,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=invoices,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Create a new invoice
    """
    # Validate student
    student = db.query(StudentProfile).filter(StudentProfile.id == invoice_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Generate invoice number
    invoice_count = db.query(Invoice).count()
    invoice_number = f"INV-{invoice_count + 1:06d}"
    
    # Create invoice
    invoice = Invoice(
        student_id=invoice_data.student_id,
        invoice_number=invoice_number,
        amount=invoice_data.amount,
        status=invoice_data.status,
        due_date=invoice_data.due_date,
        notes=invoice_data.notes
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return InvoiceResponse(
        id=invoice.id,
        student={
            "id": invoice.student.id,
            "admission_number": invoice.student.admission_number,
            "user": {
                "first_name": invoice.student.user.first_name,
                "last_name": invoice.student.user.last_name
            }
        },
        invoice_number=invoice.invoice_number,
        amount=invoice.amount,
        status=invoice.status,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        payment_method=invoice.payment_method,
        notes=invoice.notes,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at
    )

@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Update an invoice
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Update fields
    update_data = invoice_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    
    return InvoiceResponse(
        id=invoice.id,
        student={
            "id": invoice.student.id,
            "admission_number": invoice.student.admission_number,
            "user": {
                "first_name": invoice.student.user.first_name,
                "last_name": invoice.student.user.last_name
            }
        },
        invoice_number=invoice.invoice_number,
        amount=invoice.amount,
        status=invoice.status,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        payment_method=invoice.payment_method,
        notes=invoice.notes,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at
    )

@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Delete an invoice
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    db.delete(invoice)
    db.commit()
    
    return {"message": "Invoice deleted successfully"}