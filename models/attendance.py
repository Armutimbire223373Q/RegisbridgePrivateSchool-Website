"""
Attendance-related models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Time, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"

class AttendanceSession(BaseModel):
    """Attendance session model"""
    __tablename__ = "attendance_sessions"
    
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    classroom = relationship("ClassRoom", back_populates="attendance_sessions")
    records = relationship("AttendanceRecord", back_populates="session")
    
    def __str__(self):
        return f"{self.classroom.name} - {self.date}"

class AttendanceRecord(BaseModel):
    """Individual attendance record"""
    __tablename__ = "attendance_records"
    
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="attendance_records")
    session = relationship("AttendanceSession", back_populates="records")
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.session.date}: {self.status.value}"
