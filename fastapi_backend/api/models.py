"""
Pydantic models for API serialization
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    BOARDING_STAFF = "BOARDING_STAFF"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class AcademicStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    WITHDRAWN = "WITHDRAWN"
    GRADUATED = "GRADUATED"

class RelationshipType(str, Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    GUARDIAN = "GUARDIAN"
    SIBLING = "SIBLING"
    OTHER = "OTHER"

# Base Models
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    search: Optional[str] = Field(None, description="Search query")

class PaginatedResponse(BaseResponse):
    pagination: Dict[str, Any] = Field(..., description="Pagination information")

# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    date_joined: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Authentication Models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# Student Models
class StudentProfileBase(BaseModel):
    admission_number: str = Field(..., max_length=30)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    nationality: str = Field(default="Kenyan", max_length=50)
    enrollment_date: Optional[date] = None
    expected_graduation: Optional[date] = None
    previous_school: Optional[str] = Field(None, max_length=200)
    academic_status: AcademicStatus = AcademicStatus.ACTIVE
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    user_id: int
    grade_level_id: int
    classroom_id: Optional[int] = None
    is_boarder: bool = False
    dormitory_id: Optional[int] = None

class StudentProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    nationality: Optional[str] = Field(None, max_length=50)
    expected_graduation: Optional[date] = None
    previous_school: Optional[str] = Field(None, max_length=200)
    academic_status: Optional[AcademicStatus] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    classroom_id: Optional[int] = None
    is_boarder: Optional[bool] = None
    dormitory_id: Optional[int] = None

class StudentProfileResponse(StudentProfileBase):
    id: int
    user: UserResponse
    grade_level: Dict[str, Any]
    classroom: Optional[Dict[str, Any]] = None
    dormitory: Optional[Dict[str, Any]] = None
    is_boarder: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Teacher Models
class TeacherProfileBase(BaseModel):
    employee_id: str = Field(..., max_length=20)
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Kenya", max_length=100)
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    salary: Optional[float] = Field(None, ge=0)
    hire_date: Optional[date] = None
    is_active: bool = True

class TeacherProfileCreate(TeacherProfileBase):
    user_id: int

class TeacherProfileUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    salary: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class TeacherProfileResponse(TeacherProfileBase):
    id: int
    user: UserResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Parent Models
class ParentProfileBase(BaseModel):
    relationship: RelationshipType = RelationshipType.GUARDIAN
    phone_number: Optional[str] = Field(None, max_length=20)
    alternative_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Kenya", max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    employer: Optional[str] = Field(None, max_length=100)
    is_primary_contact: bool = False

class ParentProfileCreate(ParentProfileBase):
    user_id: int
    student_ids: List[int] = []

class ParentProfileUpdate(BaseModel):
    relationship: Optional[RelationshipType] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    alternative_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    employer: Optional[str] = Field(None, max_length=100)
    is_primary_contact: Optional[bool] = None

class ParentProfileResponse(ParentProfileBase):
    id: int
    user: UserResponse
    students: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Grade Models
class GradeBase(BaseModel):
    score: float = Field(..., ge=0, le=100)
    comments: Optional[str] = None

class GradeCreate(GradeBase):
    student_id: int
    assessment_id: int

class GradeUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    comments: Optional[str] = None

class GradeResponse(GradeBase):
    id: int
    student: Dict[str, Any]
    assessment: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Attendance Models
class AttendanceRecordBase(BaseModel):
    status: str = Field(..., description="PRESENT, ABSENT, LATE, EXCUSED")
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    student_id: int
    session_id: int

class AttendanceRecordUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    student: Dict[str, Any]
    session: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Fee Models
class FeeStructureBase(BaseModel):
    amount: float = Field(..., ge=0)
    description: Optional[str] = None
    due_date: Optional[date] = None

class FeeStructureCreate(FeeStructureBase):
    grade_level_id: int
    fee_type: str
    term_id: int

class FeeStructureUpdate(BaseModel):
    amount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    due_date: Optional[date] = None

class FeeStructureResponse(FeeStructureBase):
    id: int
    grade_level: Dict[str, Any]
    fee_type: str
    term: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard Models
class DashboardStats(BaseModel):
    total_students: int
    total_teachers: int
    total_parents: int
    active_students: int
    total_classes: int
    total_attendance_today: int
    pending_fees: float
    recent_activities: List[Dict[str, Any]] = []
