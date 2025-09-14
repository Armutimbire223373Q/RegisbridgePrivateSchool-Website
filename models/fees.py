"""
Fee and finance models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Float, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class FeeType(str, enum.Enum):
    TUITION = "TUITION"
    BOARDING = "BOARDING"
    TRANSPORT = "TRANSPORT"
    EXAM = "EXAM"
    LIBRARY = "LIBRARY"
    LABORATORY = "LABORATORY"
    SPORTS = "SPORTS"
    OTHER = "OTHER"

class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"

class FeeStructure(BaseModel):
    """Fee structure model"""
    __tablename__ = "fee_structures"
    
    grade_level_id = Column(Integer, ForeignKey("grade_levels.id"), nullable=False)
    fee_type = Column(Enum(FeeType), nullable=False)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    
    # Relationships
    grade_level = relationship("GradeLevel", back_populates="fee_structures")
    term = relationship("Term", back_populates="fee_structures")
    
    def __str__(self):
        return f"{self.grade_level.name} - {self.fee_type.value} - {self.term.name}: {self.amount}"

class Invoice(BaseModel):
    """Invoice model"""
    __tablename__ = "invoices"
    
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)
    due_date = Column(Date, nullable=True)
    paid_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")
    
    def __str__(self):
        return f"{self.invoice_number} - {self.student.user.full_name}: {self.amount}"
