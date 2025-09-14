"""
Grade and assessment models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class Term(BaseModel):
    """Term model (Term 1, 2, 3)"""
    __tablename__ = "terms"
    
    name = Column(String(50), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    
    # Relationships
    academic_year = relationship("AcademicYear", back_populates="terms")
    assessments = relationship("Assessment", back_populates="term")
    fee_structures = relationship("FeeStructure", back_populates="term")
    
    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

class AssessmentType(str, enum.Enum):
    EXAM = "EXAM"
    QUIZ = "QUIZ"
    ASSIGNMENT = "ASSIGNMENT"
    PROJECT = "PROJECT"
    PRACTICAL = "PRACTICAL"
    CONTINUOUS_ASSESSMENT = "CONTINUOUS_ASSESSMENT"

class Assessment(BaseModel):
    """Assessment model"""
    __tablename__ = "assessments"
    
    name = Column(String(200), nullable=False)
    type = Column(Enum(AssessmentType), nullable=False)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    max_score = Column(Float, nullable=False)
    weight = Column(Float, default=1.0)
    date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    term = relationship("Term", back_populates="assessments")
    subject = relationship("Subject", back_populates="assessments")
    grades = relationship("Grade", back_populates="assessment")
    
    def __str__(self):
        return f"{self.name} - {self.subject.name}"

class Grade(BaseModel):
    """Grade model"""
    __tablename__ = "grades"
    
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, nullable=False)
    comments = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="grades")
    assessment = relationship("Assessment", back_populates="grades")
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.assessment.name}: {self.score}"
