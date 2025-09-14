"""
User models for authentication and user management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    BOARDING_STAFF = "BOARDING_STAFF"

class User(BaseModel):
    """User model for authentication"""
    __tablename__ = "users"
    
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_boarder = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)
    parent_profile = relationship("Parent", back_populates="user", uselist=False)
    
    def __str__(self):
        return f"{self.username} ({self.role.value})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
