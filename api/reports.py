"""
PDF Report Generation System
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import logging

logger = logging.getLogger(__name__)

from api.database import get_db
from api.auth import require_roles
from models.models import StudentProfile, Grade, AttendanceRecord, Invoice, User

router = APIRouter()

def create_student_report_card(student_id: int, db: Session) -> str:
    """Generate a PDF report card for a student"""
    
    # Get student data
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("REGISBRIDGE COLLEGE", title_style))
    story.append(Paragraph("REPORT CARD", title_style))
    story.append(Spacer(1, 20))
    
    # Student Information
    student_info = [
        ["Student Name:", f"{student.user.first_name} {student.user.last_name}"],
        ["Admission Number:", student.admission_number],
        ["Grade Level:", student.grade_level.name],
        ["Academic Year:", "2024"],
        ["Term:", "Term 1"],
        ["Date Generated:", datetime.now().strftime("%B %d, %Y")]
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 3*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 30))
    
    # Grades Table
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    
    if grades:
        grades_data = [["Subject", "Assessment", "Score", "Grade", "Comments"]]
        
        for grade in grades:
            letter_grade = get_letter_grade(grade.score)
            grades_data.append([
                grade.assessment.subject.name,
                grade.assessment.name,
                f"{grade.score:.1f}",
                letter_grade,
                grade.comments or "Good work"
            ])
        
        grades_table = Table(grades_data, colWidths=[1.5*inch, 2*inch, 0.8*inch, 0.8*inch, 2*inch])
        grades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("ACADEMIC PERFORMANCE", styles['Heading2']))
        story.append(grades_table)
        story.append(Spacer(1, 20))
    
    # Attendance Summary
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id
    ).all()
    
    if attendance_records:
        present_days = len([r for r in attendance_records if r.status == "PRESENT"])
        total_days = len(attendance_records)
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        attendance_data = [
            ["Total Days", "Present Days", "Absent Days", "Attendance Rate"],
            [str(total_days), str(present_days), str(total_days - present_days), f"{attendance_rate:.1f}%"]
        ]
        
        attendance_table = Table(attendance_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        attendance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("ATTENDANCE SUMMARY", styles['Heading2']))
        story.append(attendance_table)
        story.append(Spacer(1, 20))
    
    # Comments
    story.append(Paragraph("TEACHER COMMENTS", styles['Heading2']))
    story.append(Paragraph(
        f"{student.user.first_name} has shown excellent progress this term. "
        f"Keep up the good work and continue to participate actively in class activities.",
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # Signature
    signature_data = [
        ["Class Teacher:", "_________________", "Date:", "_________________"],
        ["Head Teacher:", "_________________", "Date:", "_________________"]
    ]
    
    signature_table = Table(signature_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(signature_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Save to file
    filename = f"report_card_{student.admission_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = f"reports/{filename}"
    
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())
    
    return filepath

def get_letter_grade(score: float) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C+"
    elif score >= 40:
        return "C"
    else:
        return "D"

@router.get("/student/{student_id}/report-card")
async def generate_student_report_card(
    student_id: int,
    current_user = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    db: Session = Depends(get_db)
):
    """Generate and download student report card PDF"""
    
    # Check permissions
    if current_user.role == "STUDENT":
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student_profile or student_profile.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
        elif current_user.role == "PARENT":
            from models.parent import Parent
        parent_profile = db.query(Parent).filter(Parent.user_id == current_user.id).first()
        if not parent_profile:
            raise HTTPException(status_code=403, detail="Parent profile not found")
        
        student_ids = [s.id for s in parent_profile.students]
        if student_id not in student_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
    try:
        filepath = create_student_report_card(student_id, db)
        return FileResponse(
            path=filepath,
            filename=f"report_card_{student_id}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/attendance/class/{classroom_id}")
async def generate_attendance_report(
    classroom_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """Generate attendance report for a classroom"""
    
    try:
        from models.school import ClassRoom
        from models.student import Student
        from models.grades import AttendanceRecord
        from sqlalchemy import and_, func
        from datetime import datetime, timedelta
        
        # Parse date range
        if date_from:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        else:
            start_date = datetime.now().date() - timedelta(days=30)  # Last 30 days
            
        if date_to:
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            end_date = datetime.now().date()
        
        # Get classroom info
        classroom = db.query(ClassRoom).filter(ClassRoom.id == classroom_id).first()
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        
        # Get students in the classroom
        students = db.query(Student).filter(Student.classroom_id == classroom_id).all()
        
        # Get attendance records for the date range
        attendance_records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.student_id.in_([s.id for s in students]),
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date
            )
        ).all()
        
        # Calculate attendance statistics
        attendance_data = []
        for student in students:
            student_attendance = [r for r in attendance_records if r.student_id == student.id]
            
            total_days = len(student_attendance)
            present_days = len([r for r in student_attendance if r.status == "PRESENT"])
            absent_days = len([r for r in student_attendance if r.status == "ABSENT"])
            late_days = len([r for r in student_attendance if r.status == "LATE"])
            
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            attendance_data.append({
                "student_id": student.id,
                "student_name": f"{student.user.first_name} {student.user.last_name}",
                "student_number": student.student_number,
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "late_days": late_days,
                "attendance_percentage": round(attendance_percentage, 2)
            })
        
        # Calculate classroom summary
        total_students = len(students)
        avg_attendance = sum(s["attendance_percentage"] for s in attendance_data) / total_students if total_students > 0 else 0
        
        return {
            "classroom": {
                "id": classroom.id,
                "name": classroom.name,
                "code": classroom.code
            },
            "date_range": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "summary": {
                "total_students": total_students,
                "average_attendance": round(avg_attendance, 2),
                "total_days_covered": (end_date - start_date).days + 1
            },
            "student_attendance": attendance_data
        }
        
    except Exception as e:
        logger.error(f"Error generating attendance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating attendance report")

@router.get("/financial/summary")
async def generate_financial_report(
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Generate financial summary report"""
    
    try:
        from models.payments import Invoice, Payment, FeeStructure
        from models.student import Student
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Get current academic year (assuming we have a way to determine this)
        current_date = datetime.now().date()
        
        # Get all invoices
        all_invoices = db.query(Invoice).all()
        
        # Calculate financial summary
        total_invoices = len(all_invoices)
        total_invoice_amount = sum(invoice.amount for invoice in all_invoices)
        
        # Get paid invoices
        paid_invoices = [inv for inv in all_invoices if inv.status == "PAID"]
        paid_amount = sum(invoice.amount for invoice in paid_invoices)
        
        # Get pending invoices
        pending_invoices = [inv for inv in all_invoices if inv.status == "PENDING"]
        pending_amount = sum(invoice.amount for invoice in pending_invoices)
        
        # Get overdue invoices (assuming due_date is a string, convert to date)
        overdue_invoices = []
        for invoice in pending_invoices:
            try:
                due_date = datetime.strptime(invoice.due_date, "%Y-%m-%d").date()
                if due_date < current_date:
                    overdue_invoices.append(invoice)
            except (ValueError, TypeError):
                continue
        
        overdue_amount = sum(invoice.amount for invoice in overdue_invoices)
        
        # Get payment statistics
        all_payments = db.query(Payment).all()
        total_payments = len(all_payments)
        total_payment_amount = sum(payment.amount for payment in all_payments)
        
        # Payment method breakdown
        payment_methods = {}
        for payment in all_payments:
            method = payment.payment_method
            if method not in payment_methods:
                payment_methods[method] = {"count": 0, "amount": 0}
            payment_methods[method]["count"] += 1
            payment_methods[method]["amount"] += payment.amount
        
        # Recent payments (last 30 days)
        thirty_days_ago = current_date - timedelta(days=30)
        recent_payments = []
        for payment in all_payments:
            try:
                payment_date = datetime.strptime(payment.created_at, "%Y-%m-%dT%H:%M:%S").date()
                if payment_date >= thirty_days_ago:
                    recent_payments.append(payment)
            except (ValueError, TypeError):
                continue
        
        recent_payment_amount = sum(payment.amount for payment in recent_payments)
        
        # Fee structure summary
        fee_structures = db.query(FeeStructure).all()
        fee_breakdown = {}
        for fee in fee_structures:
            fee_breakdown[fee.name] = {
                "amount": fee.amount,
                "grade_level": fee.grade_level,
                "is_active": fee.is_active
            }
        
        return {
            "summary": {
                "total_invoices": total_invoices,
                "total_invoice_amount": round(total_invoice_amount, 2),
                "paid_amount": round(paid_amount, 2),
                "pending_amount": round(pending_amount, 2),
                "overdue_amount": round(overdue_amount, 2),
                "collection_rate": round((paid_amount / total_invoice_amount * 100), 2) if total_invoice_amount > 0 else 0
            },
            "payments": {
                "total_payments": total_payments,
                "total_payment_amount": round(total_payment_amount, 2),
                "recent_payments_30_days": len(recent_payments),
                "recent_payment_amount": round(recent_payment_amount, 2),
                "payment_methods": payment_methods
            },
            "invoices": {
                "paid_count": len(paid_invoices),
                "pending_count": len(pending_invoices),
                "overdue_count": len(overdue_invoices)
            },
            "fee_structures": fee_breakdown,
            "generated_at": current_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating financial report: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating financial report")

