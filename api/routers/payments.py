"""
Payment gateway integration endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime

from api.models import (
    PaymentCreate, PaymentUpdate, PaymentResponse,
    PaymentGatewayCreate, PaymentGatewayResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import Payment, PaymentGateway, Invoice, StudentProfile, User

router = APIRouter()

# InnBucks Integration
@router.post("/innbucks/pay", response_model=BaseResponse)
async def process_innbucks_payment(
    payment_data: dict,
    current_user = Depends(require_roles(["STUDENT", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Process payment through InnBucks
    """
    try:
        # Simulate InnBucks API call
        innbucks_response = {
            "status": "success",
            "transaction_id": f"INN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "amount": payment_data.get("amount"),
            "currency": "USD",
            "reference": payment_data.get("invoice_id")
        }
        
        # Create payment record
        payment = Payment(
            invoice_id=payment_data.get("invoice_id"),
            amount=payment_data.get("amount"),
            payment_method="INNBUCKS",
            gateway="INNBUCKS",
            transaction_id=innbucks_response["transaction_id"],
            status="COMPLETED",
            gateway_response=innbucks_response
        )
        
        db.add(payment)
        db.commit()
        
        return BaseResponse(message="Payment processed successfully via InnBucks")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"InnBucks payment failed: {str(e)}"
        )

# Bank Transfer Integration
@router.post("/bank/pay", response_model=BaseResponse)
async def process_bank_payment(
    payment_data: dict,
    current_user = Depends(require_roles(["STUDENT", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Process payment through Bank Transfer
    """
    try:
        # Simulate bank API call
        bank_response = {
            "status": "success",
            "transaction_id": f"BANK{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "amount": payment_data.get("amount"),
            "currency": "USD",
            "reference": payment_data.get("invoice_id"),
            "bank_reference": payment_data.get("bank_reference")
        }
        
        # Create payment record
        payment = Payment(
            invoice_id=payment_data.get("invoice_id"),
            amount=payment_data.get("amount"),
            payment_method="BANK_TRANSFER",
            gateway="BANK",
            transaction_id=bank_response["transaction_id"],
            status="COMPLETED",
            gateway_response=bank_response
        )
        
        db.add(payment)
        db.commit()
        
        return BaseResponse(message="Payment processed successfully via Bank Transfer")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank payment failed: {str(e)}"
        )

# EcoCash Integration
@router.post("/ecocash/pay", response_model=BaseResponse)
async def process_ecocash_payment(
    payment_data: dict,
    current_user = Depends(require_roles(["STUDENT", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Process payment through EcoCash
    """
    try:
        # Simulate EcoCash API call
        ecocash_response = {
            "status": "success",
            "transaction_id": f"ECO{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "amount": payment_data.get("amount"),
            "currency": "USD",
            "reference": payment_data.get("invoice_id"),
            "ecocash_number": payment_data.get("ecocash_number")
        }
        
        # Create payment record
        payment = Payment(
            invoice_id=payment_data.get("invoice_id"),
            amount=payment_data.get("amount"),
            payment_method="ECOCASH",
            gateway="ECOCASH",
            transaction_id=ecocash_response["transaction_id"],
            status="COMPLETED",
            gateway_response=ecocash_response
        )
        
        db.add(payment)
        db.commit()
        
        return BaseResponse(message="Payment processed successfully via EcoCash")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"EcoCash payment failed: {str(e)}"
        )

# Payment Methods
@router.get("/methods")
async def get_payment_methods():
    """
    Get available payment methods
    """
    return {
        "methods": [
            {
                "id": "innbucks",
                "name": "InnBucks",
                "description": "Pay with InnBucks wallet",
                "icon": "💳",
                "enabled": True
            },
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "description": "Direct bank transfer",
                "icon": "🏦",
                "enabled": True
            },
            {
                "id": "ecocash",
                "name": "EcoCash",
                "description": "Pay with EcoCash mobile money",
                "icon": "📱",
                "enabled": True
            },
            {
                "id": "cash",
                "name": "Cash Payment",
                "description": "Pay at school office",
                "icon": "💵",
                "enabled": True
            }
        ]
    }

# Payment History
@router.get("/history", response_model=PaginatedResponse)
async def get_payment_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    current_user = Depends(require_roles(["STUDENT", "PARENT", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Get payment history
    """
    query = db.query(Payment).join(Invoice)
    
    # Filter by student if specified
    if student_id:
        query = query.filter(Invoice.student_id == student_id)
    
    # Parents can only see their children's payments
    if current_user.role == "PARENT":
        parent_profile = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if parent_profile:
            student_ids = [s.id for s in parent_profile.students]
            query = query.filter(Invoice.student_id.in_(student_ids))
    
    # Students can only see their own payments
    if current_user.role == "STUDENT":
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if student_profile:
            query = query.filter(Invoice.student_id == student_profile.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    payments_query = query.offset(offset).limit(size).all()
    
    payments = []
    for payment in payments_query:
        payments.append({
            "id": payment.id,
            "invoice_id": payment.invoice_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "gateway": payment.gateway,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "created_at": payment.created_at,
            "gateway_response": payment.gateway_response
        })
    
    return PaginatedResponse(
        data=payments,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "has_next": page < (total + size - 1) // size,
            "has_previous": page > 1
        }
    )
