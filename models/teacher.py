"""
Teacher-related models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class Subject(BaseModel):
    """Subject model"""
    __tablename__ = "subjects"
    
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    credit_hours = Column(Integer, default=1)
    
    # Relationships
    teacher_subjects = relationship("TeacherSubject", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")
    assessments = relationship("Assessment", back_populates="subject")
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TeacherProfile(BaseModel):
    """Teacher profile model"""
    __tablename__ = "teacher_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Kenya")
    qualification = Column(String(200), nullable=True)
    specialization = Column(String(200), nullable=True)
    experience_years = Column(Integer, default=0)
    salary = Column(Float, nullable=True)
    hire_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    subjects = relationship("TeacherSubject", back_populates="teacher")
    assignments = relationship("Assignment", back_populates="teacher")
    
    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"

class TeacherSubject(BaseModel):
    """Many-to-many relationship between teachers and subjects"""
    __tablename__ = "teacher_subjects"
    
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # Relationships
    teacher = relationship("TeacherProfile", back_populates="subjects")
    subject = relationship("Subject", back_populates="teacher_subjects")
    
    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.subject.name}"
