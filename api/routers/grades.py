"""
Grade management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from api.models import (
    GradeCreate, GradeUpdate, GradeResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import Grade, StudentProfile, Assessment, User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_grades(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    assessment_id: Optional[int] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get list of grades with pagination and filtering
    """
    query = db.query(Grade).join(StudentProfile).join(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                StudentProfile.admission_number.contains(search)
            )
        )
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    
    if assessment_id:
        query = query.filter(Grade.assessment_id == assessment_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    grades_query = query.offset(offset).limit(size).all()
    
    grades = []
    for grade in grades_query:
        grades.append({
            "id": grade.id,
            "student": {
                "id": grade.student.id,
                "admission_number": grade.student.admission_number,
                "user": {
                    "first_name": grade.student.user.first_name,
                    "last_name": grade.student.user.last_name
                }
            },
            "assessment": {
                "id": grade.assessment.id,
                "name": grade.assessment.name,
                "max_score": grade.assessment.max_score
            },
            "score": grade.score,
            "comments": grade.comments,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at
        })
    
    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1
    
    return PaginatedResponse(
        data=grades,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Get a specific grade by ID
    """
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    return GradeResponse(
        id=grade.id,
        student={
            "id": grade.student.id,
            "admission_number": grade.student.admission_number,
            "user": {
                "first_name": grade.student.user.first_name,
                "last_name": grade.student.user.last_name
            }
        },
        assessment={
            "id": grade.assessment.id,
            "name": grade.assessment.name,
            "max_score": grade.assessment.max_score
        },
        score=grade.score,
        comments=grade.comments,
        created_at=grade.created_at,
        updated_at=grade.updated_at
    )

@router.post("/", response_model=GradeResponse)
async def create_grade(
    grade_data: GradeCreate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Create a new grade
    """
    # Check if student exists
    student = db.query(StudentProfile).filter(StudentProfile.id == grade_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == grade_data.assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check if grade already exists for this student and assessment
    existing_grade = db.query(Grade).filter(
        Grade.student_id == grade_data.student_id,
        Grade.assessment_id == grade_data.assessment_id
    ).first()
    if existing_grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade already exists for this student and assessment"
        )
    
    # Create grade
    grade = Grade(
        student_id=grade_data.student_id,
        assessment_id=grade_data.assessment_id,
        score=grade_data.score,
        comments=grade_data.comments
    )
    
    db.add(grade)
    db.commit()
    db.refresh(grade)
    
    return GradeResponse(
        id=grade.id,
        student={
            "id": grade.student.id,
            "admission_number": grade.student.admission_number,
            "user": {
                "first_name": grade.student.user.first_name,
                "last_name": grade.student.user.last_name
            }
        },
        assessment={
            "id": grade.assessment.id,
            "name": grade.assessment.name,
            "max_score": grade.assessment.max_score
        },
        score=grade.score,
        comments=grade.comments,
        created_at=grade.created_at,
        updated_at=grade.updated_at
    )

@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Update a grade
    """
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    # Update fields
    update_data = grade_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade, field, value)
    
    db.commit()
    db.refresh(grade)
    
    return GradeResponse(
        id=grade.id,
        student={
            "id": grade.student.id,
            "admission_number": grade.student.admission_number,
            "user": {
                "first_name": grade.student.user.first_name,
                "last_name": grade.student.user.last_name
            }
        },
        assessment={
            "id": grade.assessment.id,
            "name": grade.assessment.name,
            "max_score": grade.assessment.max_score
        },
        score=grade.score,
        comments=grade.comments,
        created_at=grade.created_at,
        updated_at=grade.updated_at
    )

@router.delete("/{grade_id}")
async def delete_grade(
    grade_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Delete a grade
    """
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    db.delete(grade)
    db.commit()
    
    return {"message": "Grade deleted successfully"}