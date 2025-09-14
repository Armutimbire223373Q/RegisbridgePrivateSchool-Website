"""
Payment and financial models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Enum, Float, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_MONEY = "MOBILE_MONEY"
    CHEQUE = "CHEQUE"
    CREDIT_CARD = "CREDIT_CARD"
    ECOCASH = "ECOCASH"
    INNBUCKS = "INNBUCKS"

class FeeType(str, enum.Enum):
    TUITION = "TUITION"
    REGISTRATION = "REGISTRATION"
    EXAM = "EXAM"
    LIBRARY = "LIBRARY"
    LABORATORY = "LABORATORY"
    SPORTS = "SPORTS"
    TRANSPORT = "TRANSPORT"
    BOARDING = "BOARDING"
    UNIFORM = "UNIFORM"
    MISCELLANEOUS = "MISCELLANEOUS"


class Payment(BaseModel):
    """Payment model"""
    __tablename__ = "payments"

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=False)
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    receipt_number = Column(String(50), unique=True, nullable=True)
    bank_reference = Column(String(100), nullable=True)
    mobile_money_reference = Column(String(100), nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    received_by = relationship("User")

    def __str__(self):
        return f"Payment {self.amount} - {self.payment_method} - {self.payment_date}"

class PaymentGateway(BaseModel):
    """Payment gateway configuration model"""
    __tablename__ = "payment_gateways"

    name = Column(String(100), nullable=False)
    gateway_type = Column(String(50), nullable=False)  # bank, mobile_money, card
    is_active = Column(Boolean, default=True)
    configuration = Column(Text, nullable=True)  # JSON configuration
    api_key = Column(String(500), nullable=True)
    api_secret = Column(String(500), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    test_mode = Column(Boolean, default=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

class Scholarship(BaseModel):
    """Scholarship model"""
    __tablename__ = "scholarships"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    percentage = Column(Float, nullable=True)  # If percentage-based
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    criteria = Column(Text, nullable=True)  # JSON criteria
    is_active = Column(Boolean, default=True)
    application_deadline = Column(Date, nullable=True)

    # Relationships
    academic_year = relationship("AcademicYear")
    student_scholarships = relationship("StudentScholarship", back_populates="scholarship")

    def __str__(self):
        return f"{self.name} - {self.amount}"

class StudentScholarship(BaseModel):
    """Student scholarship application model"""
    __tablename__ = "student_scholarships"

    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    scholarship_id = Column(Integer, ForeignKey("scholarships.id"), nullable=False)
    application_date = Column(Date, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    approved_amount = Column(Numeric(10, 2), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    student = relationship("StudentProfile")
    scholarship = relationship("Scholarship", back_populates="student_scholarships")
    approved_by = relationship("User")

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.scholarship.name}"
