"""
Admissions and application models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WAITLISTED = "WAITLISTED"

class Admission(BaseModel):
    """Admission application model"""
    __tablename__ = "admissions"

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    nationality = Column(String(100), default="Kenyan")
    
    # Contact Information
    email = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Academic Information
    previous_school = Column(String(200), nullable=True)
    previous_grade = Column(String(50), nullable=True)
    intended_grade = Column(String(50), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    
    # Application Details
    application_number = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    application_date = Column(Date, nullable=False)
    review_date = Column(Date, nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Parent/Guardian Information
    parent_name = Column(String(200), nullable=True)
    parent_phone = Column(String(20), nullable=True)
    parent_email = Column(String(200), nullable=True)
    parent_relationship = Column(String(50), nullable=True)
    
    # Additional Information
    special_needs = Column(Text, nullable=True)
    medical_conditions = Column(Text, nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    # Documents
    documents_submitted = Column(Text, nullable=True)  # JSON string of document names
    interview_notes = Column(Text, nullable=True)
    test_scores = Column(Text, nullable=True)  # JSON string of test results
    
    # Financial Information
    scholarship_requested = Column(Boolean, default=False)
    scholarship_amount = Column(Float, nullable=True)
    financial_aid_notes = Column(Text, nullable=True)

    # Relationships
    academic_year = relationship("AcademicYear", back_populates="admissions")
    reviewed_by = relationship("User")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.application_number}"

class AdmissionDocument(BaseModel):
    """Admission document model"""
    __tablename__ = "admission_documents"

    admission_id = Column(Integer, ForeignKey("admissions.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    document_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    uploaded_at = Column(Date, nullable=False)

    # Relationships
    admission = relationship("Admission")

    def __str__(self):
        return f"{self.document_name} - {self.admission.application_number}"
