"""
Email Notification System
"""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from jinja2 import Template

from api.database import get_db
from api.auth import require_roles
from models.models import User, StudentProfile, Parent, Grade, AttendanceRecord, Invoice

router = APIRouter()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@regisbridge.edu")

class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False

email_service = EmailService()

# Email Templates
def get_grade_notification_template():
    return """
    <html>
    <body>
        <h2>New Grade Posted - Regisbridge College</h2>
        <p>Dear {{parent_name}},</p>
        <p>We are pleased to inform you that a new grade has been posted for {{student_name}}.</p>
        
        <h3>Grade Details:</h3>
        <ul>
            <li><strong>Subject:</strong> {{subject}}</li>
            <li><strong>Assessment:</strong> {{assessment}}</li>
            <li><strong>Score:</strong> {{score}}</li>
            <li><strong>Grade:</strong> {{letter_grade}}</li>
            <li><strong>Date:</strong> {{date}}</li>
        </ul>
        
        <p>You can view more details by logging into the parent portal.</p>
        
        <p>Best regards,<br>
        Regisbridge College Administration</p>
    </body>
    </html>
    """

def get_attendance_notification_template():
    return """
    <html>
    <body>
        <h2>Attendance Alert - Regisbridge College</h2>
        <p>Dear {{parent_name}},</p>
        <p>This is to inform you about {{student_name}}'s attendance status.</p>
        
        <h3>Attendance Details:</h3>
        <ul>
            <li><strong>Date:</strong> {{date}}</li>
            <li><strong>Status:</strong> {{status}}</li>
            <li><strong>Class:</strong> {{class_name}}</li>
        </ul>
        
        <p>Please contact the school if you have any questions.</p>
        
        <p>Best regards,<br>
        Regisbridge College Administration</p>
    </body>
    </html>
    """

def get_fee_reminder_template():
    return """
    <html>
    <body>
        <h2>Fee Payment Reminder - Regisbridge College</h2>
        <p>Dear {{parent_name}},</p>
        <p>This is a friendly reminder that there are outstanding fees for {{student_name}}.</p>
        
        <h3>Outstanding Fees:</h3>
        <ul>
            <li><strong>Invoice Number:</strong> {{invoice_number}}</li>
            <li><strong>Amount:</strong> ${{amount}}</li>
            <li><strong>Due Date:</strong> {{due_date}}</li>
            <li><strong>Description:</strong> {{description}}</li>
        </ul>
        
        <p>Please make payment as soon as possible to avoid any late fees.</p>
        <p>You can pay online through the parent portal or visit the school office.</p>
        
        <p>Best regards,<br>
        Regisbridge College Administration</p>
    </body>
    </html>
    """

def get_admission_notification_template():
    return """
    <html>
    <body>
        <h2>Admission Status Update - Regisbridge College</h2>
        <p>Dear {{parent_name}},</p>
        <p>We are pleased to inform you about the admission status for {{student_name}}.</p>
        
        <h3>Admission Details:</h3>
        <ul>
            <li><strong>Application Number:</strong> {{application_number}}</li>
            <li><strong>Status:</strong> {{status}}</li>
            <li><strong>Grade Level:</strong> {{grade_level}}</li>
            <li><strong>Date:</strong> {{date}}</li>
        </ul>
        
        {% if status == "ACCEPTED" %}
        <p>Congratulations! Your child has been accepted to Regisbridge College.</p>
        <p>Please complete the enrollment process by visiting the school office.</p>
        {% elif status == "WAITLISTED" %}
        <p>Your child has been placed on the waitlist. We will contact you if a spot becomes available.</p>
        {% else %}
        <p>Thank you for your interest in Regisbridge College.</p>
        {% endif %}
        
        <p>Best regards,<br>
        Regisbridge College Administration</p>
    </body>
    </html>
    """

# Background task functions
async def send_grade_notification(
    student_id: int, 
    grade_id: int, 
    db: Session
):
    """Send grade notification to parents"""
    try:
        # Get student and grade information
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        grade = db.query(Grade).filter(Grade.id == grade_id).first()
        
        if not student or not grade:
            return
        
        # Get parents
        parents = student.parents
        
        for parent in parents:
            template = Template(get_grade_notification_template())
            body = template.render(
                parent_name=parent.user.first_name,
                student_name=student.user.full_name,
                subject=grade.assessment.subject.name,
                assessment=grade.assessment.name,
                score=grade.score,
                letter_grade=get_letter_grade(grade.score),
                date=grade.created_at.strftime("%B %d, %Y")
            )
            
            email_service.send_email(
                to_email=parent.user.email,
                subject=f"New Grade Posted for {student.user.full_name}",
                body=body
            )
    except Exception as e:
        print(f"Grade notification failed: {str(e)}")

async def send_attendance_notification(
    student_id: int,
    attendance_id: int,
    db: Session
):
    """Send attendance notification to parents"""
    try:
        # Get student and attendance information
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        attendance = db.query(AttendanceRecord).filter(AttendanceRecord.id == attendance_id).first()
        
        if not student or not attendance:
            return
        
        # Get parents
        parents = student.parents
        
        for parent in parents:
            template = Template(get_attendance_notification_template())
            body = template.render(
                parent_name=parent.user.first_name,
                student_name=student.user.full_name,
                date=attendance.session.date.strftime("%B %d, %Y"),
                status=attendance.status,
                class_name=student.classroom.name if student.classroom else "N/A"
            )
            
            email_service.send_email(
                to_email=parent.user.email,
                subject=f"Attendance Update for {student.user.full_name}",
                body=body
            )
    except Exception as e:
        print(f"Attendance notification failed: {str(e)}")

async def send_fee_reminder(
    invoice_id: int,
    db: Session
):
    """Send fee payment reminder"""
    try:
        # Get invoice information
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            return
        
        student = invoice.student
        parents = student.parents
        
        for parent in parents:
            template = Template(get_fee_reminder_template())
            body = template.render(
                parent_name=parent.user.first_name,
                student_name=student.user.full_name,
                invoice_number=invoice.invoice_number,
                amount=invoice.amount,
                due_date=invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "N/A",
                description=invoice.notes or "School Fees"
            )
            
            email_service.send_email(
                to_email=parent.user.email,
                subject=f"Fee Payment Reminder - {invoice.invoice_number}",
                body=body
            )
    except Exception as e:
        print(f"Fee reminder failed: {str(e)}")

async def send_admission_notification(
    admission_id: int,
    db: Session
):
    """Send admission status notification"""
    try:
        # Get admission information
        from models.models import Admission
        admission = db.query(Admission).filter(Admission.id == admission_id).first()
        
        if not admission:
            return
        
        template = Template(get_admission_notification_template())
        body = template.render(
            parent_name=admission.parent_name,
            student_name=admission.student_name,
            application_number=admission.application_number,
            status=admission.status,
            grade_level=admission.grade_level.name if admission.grade_level else "N/A",
            date=admission.updated_at.strftime("%B %d, %Y")
        )
        
        email_service.send_email(
            to_email=admission.email,
            subject=f"Admission Status Update - {admission.application_number}",
            body=body
        )
    except Exception as e:
        print(f"Admission notification failed: {str(e)}")

def send_attendance_alert(parent_email: str, student_name: str, date: datetime.date, db: Session):
    """Send attendance alert to parent"""
    try:
        email_service = EmailService()
        
        subject = f"Attendance Alert - {student_name}"
        body = f"""
        <html>
        <body>
            <h2>Attendance Alert</h2>
            <p>Dear Parent,</p>
            <p>This is to inform you that <strong>{student_name}</strong> was marked absent on <strong>{date.strftime('%B %d, %Y')}</strong>.</p>
            <p>If you believe this is an error or if you have any questions, please contact the school office.</p>
            <p>Thank you for your attention to this matter.</p>
            <br>
            <p>Best regards,<br>Regisbridge College</p>
        </body>
        </html>
        """
        
        email_service.send_email(
            to_email=parent_email,
            subject=subject,
            body=body
        )
    except Exception as e:
        print(f"Attendance alert failed: {str(e)}")

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

# API Endpoints
@router.post("/send-grade-notification")
async def trigger_grade_notification(
    student_id: int,
    grade_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """Trigger grade notification email"""
    background_tasks.add_task(send_grade_notification, student_id, grade_id, db)
    return {"message": "Grade notification queued for sending"}

@router.post("/send-attendance-notification")
async def trigger_attendance_notification(
    student_id: int,
    attendance_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """Trigger attendance notification email"""
    background_tasks.add_task(send_attendance_notification, student_id, attendance_id, db)
    return {"message": "Attendance notification queued for sending"}

@router.post("/send-fee-reminder")
async def trigger_fee_reminder(
    invoice_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Trigger fee reminder email"""
    background_tasks.add_task(send_fee_reminder, invoice_id, db)
    return {"message": "Fee reminder queued for sending"}

@router.post("/send-admission-notification")
async def trigger_admission_notification(
    admission_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Trigger admission notification email"""
    background_tasks.add_task(send_admission_notification, admission_id, db)
    return {"message": "Admission notification queued for sending"}

@router.post("/send-bulk-notifications")
async def send_bulk_notifications(
    notification_type: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Send bulk notifications to all users"""
    
    if notification_type == "fee_reminder":
        # Send fee reminders to all parents with outstanding fees
        invoices = db.query(Invoice).filter(Invoice.status == "PENDING").all()
        for invoice in invoices:
            background_tasks.add_task(send_fee_reminder, invoice.id, db)
    
    elif notification_type == "attendance_alert":
        # Send attendance alerts for absent students
        from models.student import Student
        from models.grades import AttendanceRecord
        from models.parent import Parent
        from datetime import datetime, timedelta
        
        # Get students who were absent today
        today = datetime.now().date()
        absent_students = db.query(Student).join(AttendanceRecord).filter(
            and_(
                AttendanceRecord.date == today,
                AttendanceRecord.status == "ABSENT"
            )
        ).all()
        
        for student in absent_students:
            # Get parent information
            parents = db.query(Parent).filter(Parent.students.any(Student.id == student.id)).all()
            
            for parent in parents:
                if parent.user.email:
                    background_tasks.add_task(
                        send_attendance_alert,
                        parent.user.email,
                        student.user.full_name,
                        today,
                        db
                    )
    
    return {"message": f"Bulk {notification_type} notifications queued for sending"}

