"""
Mobile App API Endpoints
Enhanced API endpoints optimized for mobile applications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json

from api.database import get_db
from api.auth import require_roles, get_current_user
from models.models import (
    User, StudentProfile, TeacherProfile, Parent, Grade, 
    AttendanceRecord, Invoice, Message, Notification, BlogPost
)

router = APIRouter()

@router.get("/dashboard/summary")
async def get_mobile_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mobile-optimized dashboard data
    """
    dashboard_data = {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "role": current_user.role,
            "email": current_user.email,
            "avatar": f"https://ui-avatars.com/api/?name={current_user.first_name}+{current_user.last_name}&background=0D8ABC&color=fff"
        },
        "notifications": [],
        "quick_actions": [],
        "recent_activities": [],
        "stats": {}
    }
    
    # Get notifications
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    for notification in notifications:
        dashboard_data["notifications"].append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "created_at": notification.created_at.isoformat(),
            "is_read": notification.is_read
        })
    
    # Role-specific data
    if current_user.role == "STUDENT":
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if student_profile:
            # Recent grades
            recent_grades = db.query(Grade).filter(
                Grade.student_id == student_profile.id
            ).order_by(Grade.created_at.desc()).limit(5).all()
            
            for grade in recent_grades:
                dashboard_data["recent_activities"].append({
                    "type": "grade",
                    "title": f"New Grade: {grade.assessment.subject.name}",
                    "description": f"Score: {grade.score}",
                    "date": grade.created_at.isoformat()
                })
            
            # Attendance summary
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_profile.id
            ).all()
            
            present_days = len([r for r in attendance_records if r.status == "PRESENT"])
            total_days = len(attendance_records)
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            dashboard_data["stats"] = {
                "attendance_rate": round(attendance_rate, 1),
                "total_grades": len(recent_grades),
                "pending_assignments": 0  # Would be calculated from assignments
            }
            
            dashboard_data["quick_actions"] = [
                {"title": "View Grades", "icon": "book", "action": "grades"},
                {"title": "Attendance", "icon": "calendar", "action": "attendance"},
                {"title": "Assignments", "icon": "file-text", "action": "assignments"},
                {"title": "Messages", "icon": "message-circle", "action": "messages"}
            ]
    
    elif current_user.role == "TEACHER":
        teacher_profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()
        if teacher_profile:
            # Today's classes
            today = date.today()
            today_attendance = db.query(AttendanceRecord).join(AttendanceRecord.session).filter(
                AttendanceSession.date == today
            ).count()
            
            dashboard_data["stats"] = {
                "today_attendance": today_attendance,
                "total_students": len(teacher_profile.subjects) * 30,  # Approximate
                "pending_grades": 0  # Would be calculated
            }
            
            dashboard_data["quick_actions"] = [
                {"title": "Mark Attendance", "icon": "calendar", "action": "attendance"},
                {"title": "Enter Grades", "icon": "book", "action": "grades"},
                {"title": "Students", "icon": "users", "action": "students"},
                {"title": "Messages", "icon": "message-circle", "action": "messages"}
            ]
    
    elif current_user.role == "PARENT":
        parent_profile = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if parent_profile:
            children_count = len(parent_profile.students)
            
            dashboard_data["stats"] = {
                "children_count": children_count,
                "unread_messages": 0,  # Would be calculated
                "pending_fees": 0  # Would be calculated
            }
            
            dashboard_data["quick_actions"] = [
                {"title": "Children", "icon": "users", "action": "children"},
                {"title": "Grades", "icon": "book", "action": "grades"},
                {"title": "Attendance", "icon": "calendar", "action": "attendance"},
                {"title": "Payments", "icon": "credit-card", "action": "payments"}
            ]
    
    elif current_user.role == "ADMIN":
        total_students = db.query(StudentProfile).count()
        total_teachers = db.query(TeacherProfile).count()
        total_parents = db.query(Parent).count()
        
        dashboard_data["stats"] = {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_parents": total_parents,
            "pending_applications": 0  # Would be calculated
        }
        
        dashboard_data["quick_actions"] = [
            {"title": "Students", "icon": "users", "action": "students"},
            {"title": "Teachers", "icon": "graduation-cap", "action": "teachers"},
            {"title": "Reports", "icon": "bar-chart", "action": "reports"},
            {"title": "Settings", "icon": "settings", "action": "settings"}
        ]
    
    return dashboard_data

@router.get("/notifications")
async def get_mobile_notifications(
    page: int = 1,
    size: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mobile notifications with pagination
    """
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    results = []
    for notification in notifications:
        results.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "data": notification.data
        })
    
    return {
        "notifications": results,
        "page": page,
        "size": size,
        "has_more": len(results) == size
    }

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}

@router.get("/students/{student_id}/mobile-profile")
async def get_mobile_student_profile(
    student_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mobile-optimized student profile
    """
    # Check permissions
    if current_user.role == "STUDENT":
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student_profile or student_profile.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    elif current_user.role == "PARENT":
        parent_profile = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if not parent_profile:
            raise HTTPException(status_code=403, detail="Parent profile not found")
        
        student_ids = [s.id for s in parent_profile.students]
        if student_id not in student_ids:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get recent grades
    recent_grades = db.query(Grade).filter(
        Grade.student_id == student_id
    ).order_by(Grade.created_at.desc()).limit(10).all()
    
    grades_data = []
    for grade in recent_grades:
        grades_data.append({
            "subject": grade.assessment.subject.name,
            "assessment": grade.assessment.name,
            "score": grade.score,
            "date": grade.created_at.isoformat(),
            "comments": grade.comments
        })
    
    # Get attendance summary
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id
    ).all()
    
    present_days = len([r for r in attendance_records if r.status == "PRESENT"])
    total_days = len(attendance_records)
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
    
    return {
        "student": {
            "id": student.id,
            "name": student.user.full_name,
            "admission_number": student.admission_number,
            "grade_level": student.grade_level.name,
            "classroom": student.classroom.name if student.classroom else None,
            "academic_status": student.academic_status,
            "is_boarder": student.is_boarder
        },
        "grades": grades_data,
        "attendance": {
            "rate": round(attendance_rate, 1),
            "present_days": present_days,
            "total_days": total_days
        }
    }

@router.get("/messages/mobile")
async def get_mobile_messages(
    page: int = 1,
    size: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mobile-optimized messages
    """
    # Get threads where user is a participant
    threads = db.query(Thread).join(ThreadParticipant).filter(
        ThreadParticipant.user_id == current_user.id
    ).order_by(Thread.updated_at.desc()).offset((page - 1) * size).limit(size).all()
    
    results = []
    for thread in threads:
        # Get latest message
        latest_message = db.query(Message).filter(
            Message.thread_id == thread.id
        ).order_by(Message.created_at.desc()).first()
        
        # Get unread count
        unread_count = db.query(Message).filter(
            Message.thread_id == thread.id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        ).count()
        
        results.append({
            "id": thread.id,
            "title": thread.title,
            "latest_message": {
                "content": latest_message.content if latest_message else "",
                "sender": latest_message.sender.full_name if latest_message else "",
                "created_at": latest_message.created_at.isoformat() if latest_message else ""
            },
            "unread_count": unread_count,
            "updated_at": thread.updated_at.isoformat()
        })
    
    return {
        "threads": results,
        "page": page,
        "size": size,
        "has_more": len(results) == size
    }

@router.get("/blog/mobile")
async def get_mobile_blog_posts(
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get mobile-optimized blog posts
    """
    query = db.query(BlogPost).filter(BlogPost.status == "PUBLISHED")
    
    if category:
        query = query.filter(BlogPost.category == category)
    
    posts = query.order_by(BlogPost.published_at.desc()).offset((page - 1) * size).limit(size).all()
    
    results = []
    for post in posts:
        results.append({
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "author": post.author.full_name if post.author else "Admin",
            "category": post.category,
            "published_at": post.published_at.isoformat(),
            "image_url": post.featured_image_url,
            "read_time": len(post.content.split()) // 200 + 1  # Approximate read time
        })
    
    return {
        "posts": results,
        "page": page,
        "size": size,
        "has_more": len(results) == size
    }

@router.get("/offline/sync")
async def get_offline_sync_data(
    last_sync: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data for offline sync
    """
    if not last_sync:
        last_sync = datetime.now() - timedelta(days=30)
    
    sync_data = {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "role": current_user.role,
            "email": current_user.email
        },
        "notifications": [],
        "messages": [],
        "blog_posts": []
    }
    
    # Get notifications since last sync
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.created_at >= last_sync
    ).all()
    
    for notification in notifications:
        sync_data["notifications"].append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        })
    
    # Get blog posts since last sync
    blog_posts = db.query(BlogPost).filter(
        BlogPost.status == "PUBLISHED",
        BlogPost.published_at >= last_sync
    ).all()
    
    for post in blog_posts:
        sync_data["blog_posts"].append({
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "category": post.category,
            "published_at": post.published_at.isoformat()
        })
    
    return sync_data

