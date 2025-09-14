"""
Assignment and submission models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel

class Assignment(BaseModel):
    """Assignment model"""
    __tablename__ = "assignments"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    max_score = Column(Float, nullable=False)
    is_published = Column(Boolean, default=True)
    
    # Relationships
    subject = relationship("Subject", back_populates="assignments")
    teacher = relationship("TeacherProfile", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment")
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class AssignmentSubmission(BaseModel):
    """Assignment submission model"""
    __tablename__ = "assignment_submissions"
    
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    is_late = Column(Boolean, default=False)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="assignments")
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.assignment.title}"
