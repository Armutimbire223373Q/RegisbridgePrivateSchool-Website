"""
School and academic structure models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Time, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class AcademicYear(BaseModel):
    """Academic year model"""
    __tablename__ = "academic_years"

    name = Column(String(100), nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

    # Relationships
    terms = relationship("Term", back_populates="academic_year")
    admissions = relationship("Admission", back_populates="academic_year")

    def __str__(self):
        return self.name




class Timetable(BaseModel):
    """Class timetable model"""
    __tablename__ = "timetables"

    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    classroom = relationship("ClassRoom", back_populates="timetables")
    subject = relationship("Subject")
    teacher = relationship("TeacherProfile")

    def __str__(self):
        return f"{self.classroom.name} - {self.subject.name} - {self.day_of_week}"

class Program(BaseModel):
    """Academic program model"""
    __tablename__ = "programs"

    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    duration_years = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)

    # Relationships
    students = relationship("StudentProfile", back_populates="program")

    def __str__(self):
        return f"{self.name} ({self.code})"
