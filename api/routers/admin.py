"""
Admin interface endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import os

from api.auth import get_current_user, require_role
from api.database import get_db
from models.models import (
    User, StudentProfile, TeacherProfile, Parent, GradeLevel, ClassRoom,
    Dormitory, Subject, AcademicYear, Term, Assessment, Grade,
    AttendanceSession, AttendanceRecord, FeeStructure, Invoice
)

router = APIRouter()

# Templates directory
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Admin dashboard"""
    # Get statistics
    stats = {
        "total_students": db.query(StudentProfile).count(),
        "total_teachers": db.query(TeacherProfile).count(),
        "total_parents": db.query(Parent).count(),
        "active_students": db.query(StudentProfile).filter(StudentProfile.academic_status == "ACTIVE").count(),
        "total_classes": db.query(ClassRoom).count(),
        "total_invoices": db.query(Invoice).count(),
        "pending_invoices": db.query(Invoice).filter(Invoice.status == "PENDING").count(),
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": current_user,
        "stats": stats
    })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """User management page"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search)
        )
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "user": current_user,
        "users": users,
        "page": page,
        "total": total,
        "search": search,
        "role": role
    })

@router.get("/students", response_class=HTMLResponse)
async def admin_students(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Student management page"""
    query = db.query(StudentProfile).join(User)
    
    if search:
        query = query.filter(
            User.first_name.contains(search) |
            User.last_name.contains(search) |
            StudentProfile.admission_number.contains(search)
        )
    
    if grade_level:
        query = query.filter(StudentProfile.grade_level_id == grade_level)
    
    if status:
        query = query.filter(StudentProfile.academic_status == status)
    
    students = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    grade_levels = db.query(GradeLevel).all()
    
    return templates.TemplateResponse("admin/students.html", {
        "request": request,
        "user": current_user,
        "students": students,
        "grade_levels": grade_levels,
        "page": page,
        "total": total,
        "search": search,
        "grade_level": grade_level,
        "status": status
    })

@router.get("/teachers", response_class=HTMLResponse)
async def admin_teachers(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Teacher management page"""
    query = db.query(TeacherProfile).join(User)
    
    if search:
        query = query.filter(
            User.first_name.contains(search) |
            User.last_name.contains(search) |
            TeacherProfile.employee_id.contains(search)
        )
    
    teachers = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    
    return templates.TemplateResponse("admin/teachers.html", {
        "request": request,
        "user": current_user,
        "teachers": teachers,
        "page": page,
        "total": total,
        "search": search
    })

@router.get("/grades", response_class=HTMLResponse)
async def admin_grades(
    request: Request,
    page: int = Query(1, ge=1),
    student_id: Optional[int] = Query(None),
    assessment_id: Optional[int] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Grade management page"""
    query = db.query(Grade).join(StudentProfile).join(User)
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    
    if assessment_id:
        query = query.filter(Grade.assessment_id == assessment_id)
    
    grades = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    
    return templates.TemplateResponse("admin/grades.html", {
        "request": request,
        "user": current_user,
        "grades": grades,
        "page": page,
        "total": total,
        "student_id": student_id,
        "assessment_id": assessment_id
    })

@router.get("/attendance", response_class=HTMLResponse)
async def admin_attendance(
    request: Request,
    page: int = Query(1, ge=1),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    classroom_id: Optional[int] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Attendance management page"""
    query = db.query(AttendanceRecord).join(StudentProfile).join(User)
    
    if date_from:
        query = query.filter(AttendanceRecord.created_at >= date_from)
    
    if date_to:
        query = query.filter(AttendanceRecord.created_at <= date_to)
    
    if classroom_id:
        query = query.join(AttendanceSession).filter(AttendanceSession.classroom_id == classroom_id)
    
    records = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    classrooms = db.query(ClassRoom).all()
    
    return templates.TemplateResponse("admin/attendance.html", {
        "request": request,
        "user": current_user,
        "records": records,
        "classrooms": classrooms,
        "page": page,
        "total": total,
        "date_from": date_from,
        "date_to": date_to,
        "classroom_id": classroom_id
    })

@router.get("/fees", response_class=HTMLResponse)
async def admin_fees(
    request: Request,
    page: int = Query(1, ge=1),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Fee management page"""
    query = db.query(Invoice).join(StudentProfile).join(User)
    
    if student_id:
        query = query.filter(Invoice.student_id == student_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.offset((page - 1) * 20).limit(20).all()
    total = query.count()
    
    return templates.TemplateResponse("admin/fees.html", {
        "request": request,
        "user": current_user,
        "invoices": invoices,
        "page": page,
        "total": total,
        "student_id": student_id,
        "status": status
    })

# API endpoints for AJAX operations
@router.post("/users/create")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    from api.auth import get_password_hash
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=get_password_hash(password),
        role=role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully", "user_id": user.id}

@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Toggle user active status"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}
