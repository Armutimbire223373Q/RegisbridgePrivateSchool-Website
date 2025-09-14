"""
Import all models for SQLAlchemy
"""

from .base import Base, BaseModel, TimestampMixin
from .user import User, UserRole
from .student import (
    GradeLevel, ClassRoom, Dormitory, Bed, StudentProfile, BoardingStudent,
    Gender, BloodGroup, AcademicStatus, parent_student
)
from .teacher import Subject, TeacherProfile, TeacherSubject
from .parent import Parent, RelationshipType
from .grades import (
    Term, Assessment, Grade, AssessmentType
)
from .attendance import (
    AttendanceSession, AttendanceRecord, AttendanceStatus
)
from .fees import (
    FeeStructure, Invoice, FeeType, InvoiceStatus
)
from .payments import (
    Payment, PaymentGateway, Scholarship, StudentScholarship, 
    PaymentStatus, PaymentMethod
)
from .assignments import Assignment, AssignmentSubmission
from .messaging import Thread, ThreadParticipant, Message, Notification, Announcement
from .admissions import Admission, AdmissionDocument, ApplicationStatus
from .school import Program, Timetable, AcademicYear
from .inventory import (
    InventoryItem, InventoryTransaction, ItemIssue, Supplier, PurchaseOrder, 
    PurchaseOrderItem, ItemCategory, ItemStatus, TransactionType
)
from .blog import (
    BlogPost, PostComment, Event, EventRegistration, Page, MediaFile,
    PostStatus, PostCategory
)
from .public import NewsPost

# Export all models
__all__ = [
    # Base classes
    "Base",
    "BaseModel", 
    "TimestampMixin",
    
    # User models
    "User",
    "UserRole",
    
    # Student models
    "GradeLevel",
    "ClassRoom", 
    "Dormitory",
    "Bed",
    "StudentProfile",
    "BoardingStudent",
    "Gender",
    "BloodGroup", 
    "AcademicStatus",
    "parent_student",
    
    # Teacher models
    "Subject",
    "TeacherProfile",
    "TeacherSubject",
    
    # Parent models
    "Parent",
    "RelationshipType",
    
    # Grade models
    "AcademicYear",
    "Term",
    "Assessment", 
    "Grade",
    "AssessmentType",
    
    # Attendance models
    "AttendanceSession",
    "AttendanceRecord",
    "AttendanceStatus",
    
    # Fee models
    "FeeStructure",
    "Invoice",
    "FeeType",
    "InvoiceStatus",
    "Payment",
    "PaymentGateway",
    "Scholarship",
    "StudentScholarship",
    "PaymentStatus",
    "PaymentMethod",
    
    # Assignment models
    "Assignment",
    "AssignmentSubmission",
    
    # Messaging models
    "Thread",
    "ThreadParticipant", 
    "Message",
    "Notification",
    "Announcement",
    
    # Admissions models
    "Admission",
    "AdmissionDocument",
    "ApplicationStatus",
    
    # School models
    "Program",
    "Timetable",
    
    # Inventory models
    "InventoryItem",
    "InventoryTransaction",
    "ItemIssue",
    "Supplier",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "ItemCategory",
    "ItemStatus",
    "TransactionType",
    
    # Blog models
    "BlogPost",
    "PostComment",
    "Event",
    "EventRegistration",
    "Page",
    "MediaFile",
    "PostStatus",
    "PostCategory",
    
    # Public models
    "NewsPost",
]
