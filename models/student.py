"""
Student-related models
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class AcademicStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    WITHDRAWN = "WITHDRAWN"
    GRADUATED = "GRADUATED"

class GradeLevel(BaseModel):
    """Grade levels (Primary, Secondary, etc.)"""
    __tablename__ = "grade_levels"
    
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    students = relationship("StudentProfile", back_populates="grade_level")
    fee_structures = relationship("FeeStructure", back_populates="grade_level")
    
    def __str__(self):
        return self.name

class ClassRoom(BaseModel):
    """Classroom model"""
    __tablename__ = "classrooms"
    
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, default=30)
    description = Column(Text, nullable=True)
    
    # Relationships
    students = relationship("StudentProfile", back_populates="classroom")
    attendance_sessions = relationship("AttendanceSession", back_populates="classroom")
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Dormitory(BaseModel):
    """Dormitory model for boarding students"""
    __tablename__ = "dormitories"
    
    name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    capacity = Column(Integer, default=20)
    description = Column(Text, nullable=True)
    
    # Relationships
    boarders = relationship("StudentProfile", back_populates="dormitory")
    beds = relationship("Bed", back_populates="dormitory")
    
    def __str__(self):
        return self.name

class Bed(BaseModel):
    """Bed model for dormitory management"""
    __tablename__ = "beds"
    
    number = Column(String(10), nullable=False)
    dormitory_id = Column(Integer, ForeignKey("dormitories.id"), nullable=False)
    is_occupied = Column(Boolean, default=False)
    
    # Relationships
    dormitory = relationship("Dormitory", back_populates="beds")
    boarding_student = relationship("BoardingStudent", back_populates="bed", uselist=False)
    
    def __str__(self):
        return f"{self.dormitory.name} - {self.number}"

class StudentProfile(BaseModel):
    """Student profile model"""
    __tablename__ = "student_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    admission_number = Column(String(30), unique=True, nullable=False)
    grade_level_id = Column(Integer, ForeignKey("grade_levels.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    is_boarder = Column(Boolean, default=False)
    dormitory_id = Column(Integer, ForeignKey("dormitories.id"), nullable=True)
    
    # Personal Information
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    blood_group = Column(Enum(BloodGroup), nullable=True)
    nationality = Column(String(50), default="Kenyan")
    
    # Academic Information
    enrollment_date = Column(Date, nullable=False)
    expected_graduation = Column(Date, nullable=True)
    previous_school = Column(String(200), nullable=True)
    academic_status = Column(Enum(AcademicStatus), default=AcademicStatus.ACTIVE)
    
    # Health Information
    medical_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    grade_level = relationship("GradeLevel", back_populates="students")
    classroom = relationship("ClassRoom", back_populates="students")
    dormitory = relationship("Dormitory", back_populates="boarders")
    grades = relationship("Grade", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    assignments = relationship("AssignmentSubmission", back_populates="student")
    invoices = relationship("Invoice", back_populates="student")
    parents = relationship("Parent", secondary="parent_student", back_populates="students")
    
    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"

class BoardingStudent(BaseModel):
    """Boarding student management"""
    __tablename__ = "boarding_students"
    
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, unique=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=True)
    status = Column(String(20), default="ACTIVE")
    
    # Relationships
    student = relationship("StudentProfile")
    bed = relationship("Bed", back_populates="boarding_student")
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.status}"

# Association table for many-to-many relationship between parents and students
parent_student = Table(
    "parent_student",
    BaseModel.metadata,
    Column("parent_id", Integer, ForeignKey("parents.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("student_profiles.id"), primary_key=True)
)
