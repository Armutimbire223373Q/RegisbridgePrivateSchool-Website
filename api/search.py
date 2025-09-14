"""
Advanced Search and Filtering System
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from api.database import get_db
from api.auth import require_roles, get_current_user
from models.models import (
    User, StudentProfile, TeacherProfile, Parent, Grade, 
    AttendanceRecord, Invoice, BlogPost, Message
)

router = APIRouter()

@router.get("/global")
async def global_search(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    filters: Optional[str] = Query(None, description="JSON filters"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Global search across all entities
    """
    search_results = {
        "students": [],
        "teachers": [],
        "parents": [],
        "grades": [],
        "attendance": [],
        "invoices": [],
        "blog_posts": [],
        "messages": []
    }
    
    # Search students
    if current_user.role in ["ADMIN", "TEACHER", "BOARDING_STAFF"]:
        students = db.query(StudentProfile).join(User).filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                StudentProfile.admission_number.ilike(f"%{q}%")
            )
        ).limit(5).all()
        
        for student in students:
            search_results["students"].append({
                "id": student.id,
                "name": student.user.full_name,
                "admission_number": student.admission_number,
                "email": student.user.email,
                "grade_level": student.grade_level.name,
                "type": "student"
            })
    
    # Search teachers
    if current_user.role in ["ADMIN", "STUDENT", "PARENT"]:
        teachers = db.query(TeacherProfile).join(User).filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                TeacherProfile.specialization.ilike(f"%{q}%")
            )
        ).limit(5).all()
        
        for teacher in teachers:
            search_results["teachers"].append({
                "id": teacher.id,
                "name": teacher.user.full_name,
                "email": teacher.user.email,
                "specialization": teacher.specialization,
                "type": "teacher"
            })
    
    # Search parents
    if current_user.role in ["ADMIN", "TEACHER"]:
        parents = db.query(Parent).join(User).filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%")
            )
        ).limit(5).all()
        
        for parent in parents:
            search_results["parents"].append({
                "id": parent.id,
                "name": parent.user.full_name,
                "email": parent.user.email,
                "relationship": parent.relationship_type,
                "type": "parent"
            })
    
    # Search grades
    if current_user.role in ["ADMIN", "TEACHER", "STUDENT", "PARENT"]:
        grades = db.query(Grade).join(StudentProfile).join(User).filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%")
            )
        ).limit(5).all()
        
        for grade in grades:
            search_results["grades"].append({
                "id": grade.id,
                "student_name": grade.student.user.full_name,
                "subject": grade.assessment.subject.name,
                "score": grade.score,
                "assessment": grade.assessment.name,
                "type": "grade"
            })
    
    # Search blog posts
    blog_posts = db.query(BlogPost).filter(
        or_(
            BlogPost.title.ilike(f"%{q}%"),
            BlogPost.content.ilike(f"%{q}%"),
            BlogPost.excerpt.ilike(f"%{q}%")
        )
    ).limit(5).all()
    
    for post in blog_posts:
        search_results["blog_posts"].append({
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "author": post.author.full_name if post.author else "Unknown",
            "published_at": post.published_at,
            "type": "blog_post"
        })
    
    return {
        "query": q,
        "results": search_results,
        "total_results": sum(len(results) for results in search_results.values())
    }

@router.get("/students/advanced")
async def advanced_student_search(
    q: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    academic_status: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    is_boarder: Optional[bool] = Query(None),
    enrollment_date_from: Optional[date] = Query(None),
    enrollment_date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"])),
    db: Session = Depends(get_db)
):
    """
    Advanced student search with multiple filters
    """
    query = db.query(StudentProfile).join(User)
    
    # Text search
    if q:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                StudentProfile.admission_number.ilike(f"%{q}%")
            )
        )
    
    # Filters
    if grade_level:
        query = query.filter(StudentProfile.grade_level_id == grade_level)
    
    if academic_status:
        query = query.filter(StudentProfile.academic_status == academic_status)
    
    if gender:
        query = query.filter(StudentProfile.gender == gender)
    
    if is_boarder is not None:
        query = query.filter(StudentProfile.is_boarder == is_boarder)
    
    if enrollment_date_from:
        query = query.filter(StudentProfile.enrollment_date >= enrollment_date_from)
    
    if enrollment_date_to:
        query = query.filter(StudentProfile.enrollment_date <= enrollment_date_to)
    
    # Sorting
    if sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(asc(User.first_name))
        else:
            query = query.order_by(desc(User.first_name))
    elif sort_by == "admission_number":
        if sort_order == "asc":
            query = query.order_by(asc(StudentProfile.admission_number))
        else:
            query = query.order_by(desc(StudentProfile.admission_number))
    elif sort_by == "enrollment_date":
        if sort_order == "asc":
            query = query.order_by(asc(StudentProfile.enrollment_date))
        else:
            query = query.order_by(desc(StudentProfile.enrollment_date))
    else:
        if sort_order == "asc":
            query = query.order_by(asc(StudentProfile.created_at))
        else:
            query = query.order_by(desc(StudentProfile.created_at))
    
    # Pagination
    total = query.count()
    offset = (page - 1) * size
    students = query.offset(offset).limit(size).all()
    
    results = []
    for student in students:
        results.append({
            "id": student.id,
            "name": student.user.full_name,
            "admission_number": student.admission_number,
            "email": student.user.email,
            "grade_level": student.grade_level.name,
            "academic_status": student.academic_status,
            "gender": student.gender,
            "is_boarder": student.is_boarder,
            "enrollment_date": student.enrollment_date,
            "classroom": student.classroom.name if student.classroom else None
        })
    
    return {
        "results": results,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "has_next": page < (total + size - 1) // size,
            "has_previous": page > 1
        }
    }

@router.get("/grades/advanced")
async def advanced_grade_search(
    q: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    assessment_id: Optional[int] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    db: Session = Depends(get_db)
):
    """
    Advanced grade search with multiple filters
    """
    query = db.query(Grade).join(StudentProfile).join(User)
    
    # Text search
    if q:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                Grade.comments.ilike(f"%{q}%")
            )
        )
    
    # Filters
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    
    if subject_id:
        query = query.join(Grade.assessment).filter(Grade.assessment.has(subject_id=subject_id))
    
    if assessment_id:
        query = query.filter(Grade.assessment_id == assessment_id)
    
    if min_score is not None:
        query = query.filter(Grade.score >= min_score)
    
    if max_score is not None:
        query = query.filter(Grade.score <= max_score)
    
    if date_from:
        query = query.filter(Grade.created_at >= date_from)
    
    if date_to:
        query = query.filter(Grade.created_at <= date_to)
    
    # Role-based filtering
    if current_user.role == "STUDENT":
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if student_profile:
            query = query.filter(Grade.student_id == student_profile.id)
    
    elif current_user.role == "PARENT":
        parent_profile = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if parent_profile:
            student_ids = [s.id for s in parent_profile.students]
            query = query.filter(Grade.student_id.in_(student_ids))
    
    # Sorting
    query = query.order_by(desc(Grade.created_at))
    
    # Pagination
    total = query.count()
    offset = (page - 1) * size
    grades = query.offset(offset).limit(size).all()
    
    results = []
    for grade in grades:
        results.append({
            "id": grade.id,
            "student_name": grade.student.user.full_name,
            "subject": grade.assessment.subject.name,
            "assessment": grade.assessment.name,
            "score": grade.score,
            "comments": grade.comments,
            "created_at": grade.created_at,
            "assessment_date": grade.assessment.date
        })
    
    return {
        "results": results,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "has_next": page < (total + size - 1) // size,
            "has_previous": page > 1
        }
    }

@router.get("/attendance/advanced")
async def advanced_attendance_search(
    q: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "BOARDING_STAFF"])),
    db: Session = Depends(get_db)
):
    """
    Advanced attendance search with multiple filters
    """
    query = db.query(AttendanceRecord).join(StudentProfile).join(User)
    
    # Text search
    if q:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%")
            )
        )
    
    # Filters
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    
    if classroom_id:
        query = query.join(StudentProfile.classroom).filter(StudentProfile.classroom_id == classroom_id)
    
    if status:
        query = query.filter(AttendanceRecord.status == status)
    
    if date_from:
        query = query.join(AttendanceRecord.session).filter(AttendanceSession.date >= date_from)
    
    if date_to:
        query = query.join(AttendanceRecord.session).filter(AttendanceSession.date <= date_to)
    
    # Sorting
    query = query.order_by(desc(AttendanceRecord.created_at))
    
    # Pagination
    total = query.count()
    offset = (page - 1) * size
    records = query.offset(offset).limit(size).all()
    
    results = []
    for record in records:
        results.append({
            "id": record.id,
            "student_name": record.student.user.full_name,
            "status": record.status,
            "date": record.session.date,
            "classroom": record.student.classroom.name if record.student.classroom else None,
            "notes": record.notes,
            "created_at": record.created_at
        })
    
    return {
        "results": results,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "has_next": page < (total + size - 1) // size,
            "has_previous": page > 1
        }
    }

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    entity_type: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions as user types
    """
    suggestions = []
    
    if not entity_type or entity_type == "students":
        if current_user.role in ["ADMIN", "TEACHER", "BOARDING_STAFF"]:
            students = db.query(StudentProfile).join(User).filter(
                or_(
                    User.first_name.ilike(f"%{q}%"),
                    User.last_name.ilike(f"%{q}%"),
                    StudentProfile.admission_number.ilike(f"%{q}%")
                )
            ).limit(5).all()
            
            for student in students:
                suggestions.append({
                    "text": f"{student.user.full_name} ({student.admission_number})",
                    "type": "student",
                    "id": student.id
                })
    
    if not entity_type or entity_type == "teachers":
        if current_user.role in ["ADMIN", "STUDENT", "PARENT"]:
            teachers = db.query(TeacherProfile).join(User).filter(
                or_(
                    User.first_name.ilike(f"%{q}%"),
                    User.last_name.ilike(f"%{q}%")
                )
            ).limit(5).all()
            
            for teacher in teachers:
                suggestions.append({
                    "text": f"{teacher.user.full_name} - {teacher.specialization}",
                    "type": "teacher",
                    "id": teacher.id
                })
    
    return {"suggestions": suggestions}

