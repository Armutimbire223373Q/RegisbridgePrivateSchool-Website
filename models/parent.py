"""
Parent-related models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class RelationshipType(str, enum.Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    GUARDIAN = "GUARDIAN"
    SIBLING = "SIBLING"
    OTHER = "OTHER"

class Parent(BaseModel):
    """Parent model"""
    __tablename__ = "parents"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    relationship_type = Column(Enum(RelationshipType), default=RelationshipType.GUARDIAN)
    
    # Contact Information
    phone_number = Column(String(20), nullable=True)
    alternative_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Kenya")
    
    # Emergency Contact
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    # Additional Information
    occupation = Column(String(100), nullable=True)
    employer = Column(String(100), nullable=True)
    is_primary_contact = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="parent_profile")
    students = relationship("StudentProfile", secondary="parent_student", back_populates="parents")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.relationship_type.value}"
    
    def get_primary_student(self):
        """Get the primary student if this parent is the primary contact"""
        if self.is_primary_contact and self.students:
            return self.students[0]
        return None
