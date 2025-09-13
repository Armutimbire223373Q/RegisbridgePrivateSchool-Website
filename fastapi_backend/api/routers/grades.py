"""
Grade management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count

from api.models import (
    GradeCreate, GradeUpdate, GradeResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from grades.models import Grade, Assessment, Term, AcademicYear
from students.models import StudentProfile

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_grades(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    assessment_id: Optional[int] = Query(None),
    term_id: Optional[int] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get list of grades with pagination and filtering
    """
    queryset = Grade.objects.select_related('student__user', 'assessment').all()
    
    # Apply filters
    if student_id:
        queryset = queryset.filter(student_id=student_id)
    
    if assessment_id:
        queryset = queryset.filter(assessment_id=assessment_id)
    
    if term_id:
        queryset = queryset.filter(assessment__term_id=term_id)
    
    # Pagination
    paginator = Paginator(queryset, size)
    page_obj = paginator.get_page(page)
    
    grades = []
    for grade in page_obj:
        grades.append({
            "id": grade.id,
            "student": {
                "id": grade.student.id,
                "admission_number": grade.student.admission_number,
                "user": {
                    "id": grade.student.user.id,
                    "first_name": grade.student.user.first_name,
                    "last_name": grade.student.user.last_name,
                    "email": grade.student.user.email
                }
            },
            "assessment": {
                "id": grade.assessment.id,
                "name": grade.assessment.name,
                "type": grade.assessment.type,
                "weight": grade.assessment.weight,
                "max_score": grade.assessment.max_score
            },
            "score": grade.score,
            "comments": grade.comments,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at
        })
    
    return PaginatedResponse(
        data=grades,
        pagination={
            "page": page,
            "size": size,
            "total": paginator.count,
            "pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    )

@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Get a specific grade by ID
    """
    try:
        grade = Grade.objects.select_related('student__user', 'assessment').get(id=grade_id)
    except Grade.DoesNotExist:
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
                "id": grade.student.user.id,
                "first_name": grade.student.user.first_name,
                "last_name": grade.student.user.last_name,
                "email": grade.student.user.email
            }
        },
        assessment={
            "id": grade.assessment.id,
            "name": grade.assessment.name,
            "type": grade.assessment.type,
            "weight": grade.assessment.weight,
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
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Create a new grade
    """
    try:
        # Check if student exists
        student = StudentProfile.objects.get(id=grade_data.student_id)
        
        # Check if assessment exists
        assessment = Assessment.objects.get(id=grade_data.assessment_id)
        
        # Check if grade already exists for this student and assessment
        if Grade.objects.filter(student=student, assessment=assessment).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grade already exists for this student and assessment"
            )
        
        # Validate score against assessment max_score
        if grade_data.score > assessment.max_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Score cannot exceed maximum score of {assessment.max_score}"
            )
        
        # Create grade
        grade = Grade.objects.create(
            student=student,
            assessment=assessment,
            score=grade_data.score,
            comments=grade_data.comments
        )
        
        return GradeResponse(
            id=grade.id,
            student={
                "id": grade.student.id,
                "admission_number": grade.student.admission_number,
                "user": {
                    "id": grade.student.user.id,
                    "first_name": grade.student.user.first_name,
                    "last_name": grade.student.user.last_name,
                    "email": grade.student.user.email
                }
            },
            assessment={
                "id": grade.assessment.id,
                "name": grade.assessment.name,
                "type": grade.assessment.type,
                "weight": grade.assessment.weight,
                "max_score": grade.assessment.max_score
            },
            score=grade.score,
            comments=grade.comments,
            created_at=grade.created_at,
            updated_at=grade.updated_at
        )
        
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    except Assessment.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Update a grade
    """
    try:
        grade = Grade.objects.get(id=grade_id)
    except Grade.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    # Validate score against assessment max_score
    if grade_data.score is not None and grade_data.score > grade.assessment.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score cannot exceed maximum score of {grade.assessment.max_score}"
        )
    
    # Update fields
    update_data = grade_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade, field, value)
    
    grade.save()
    
    return GradeResponse(
        id=grade.id,
        student={
            "id": grade.student.id,
            "admission_number": grade.student.admission_number,
            "user": {
                "id": grade.student.user.id,
                "first_name": grade.student.user.first_name,
                "last_name": grade.student.user.last_name,
                "email": grade.student.user.email
            }
        },
        assessment={
            "id": grade.assessment.id,
            "name": grade.assessment.name,
            "type": grade.assessment.type,
            "weight": grade.assessment.weight,
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
    current_user = Depends(require_roles(["ADMIN", "TEACHER"]))
):
    """
    Delete a grade
    """
    try:
        grade = Grade.objects.get(id=grade_id)
        grade.delete()
        return {"message": "Grade deleted successfully"}
    except Grade.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )

@router.get("/statistics/student/{student_id}")
async def get_student_grade_statistics(
    student_id: int,
    term_id: Optional[int] = Query(None),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "PARENT"]))
):
    """
    Get grade statistics for a specific student
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
    except StudentProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    queryset = Grade.objects.filter(student=student)
    
    if term_id:
        queryset = queryset.filter(assessment__term_id=term_id)
    
    # Calculate statistics
    total_grades = queryset.count()
    average_score = queryset.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    highest_score = queryset.aggregate(max_score=Max('score'))['max_score'] or 0
    lowest_score = queryset.aggregate(min_score=Min('score'))['min_score'] or 0
    
    return {
        "student": {
            "id": student.id,
            "admission_number": student.admission_number,
            "user": {
                "id": student.user.id,
                "first_name": student.user.first_name,
                "last_name": student.user.last_name
            }
        },
        "statistics": {
            "total_grades": total_grades,
            "average_score": round(average_score, 2),
            "highest_score": highest_score,
            "lowest_score": lowest_score
        }
    }
