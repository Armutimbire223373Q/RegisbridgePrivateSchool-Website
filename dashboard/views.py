from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta

from students.models import StudentProfile, ClassRoom
from teachers.models import TeacherProfile, Subject
from core_attendance.models import StudentAttendance, AttendanceSession
from grades.models import Assessment, Grade, StudentTermGrade, Term
from fees.models import Invoice, Payment
from messaging.models import Thread, Message
from parents.models import Parent


@login_required
def dashboard(request):
    """Main dashboard - redirects to role-specific dashboard"""
    user = request.user

    if user.role == "ADMIN":
        return redirect("dashboard:admin_dashboard")
    elif user.role == "TEACHER":
        return redirect("dashboard:teacher_dashboard")
    elif user.role == "STUDENT":
        return redirect("dashboard:student_dashboard")
    elif user.role == "PARENT":
        return redirect("dashboard:parent_dashboard")
    else:
        messages.warning(request, "No dashboard available for your role.")
        return redirect("/")


@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    if request.user.role != "ADMIN":
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("/")

    # System statistics
    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_parents = Parent.objects.count()

    # Recent activities
    recent_attendance = AttendanceSession.objects.select_related("classroom").order_by(
        "-date"
    )[:5]
    recent_grades = Grade.objects.select_related(
        "student__user", "assessment"
    ).order_by("-graded_at")[:5]
    recent_payments = Payment.objects.select_related("invoice__student__user").order_by(
        "-date"
    )[:5]

    # Financial overview
    total_fees = (
        Invoice.objects.filter(status="ISSUED").aggregate(total=Sum("total_amount"))[
            "total"
        ]
        or 0
    )
    total_paid = Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
    outstanding_fees = total_fees - total_paid

    context = {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_parents": total_parents,
        "recent_attendance": recent_attendance,
        "recent_grades": recent_grades,
        "recent_payments": recent_payments,
        "total_fees": total_fees,
        "total_paid": total_paid,
        "outstanding_fees": outstanding_fees,
    }

    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard with class and student information"""
    if request.user.role != "TEACHER":
        messages.error(request, "Access denied. Teacher privileges required.")
        return redirect("/")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("/")

    # Get teacher's classes
    teacher_classes = ClassRoom.objects.filter(
        lessons__teacher=teacher_profile
    ).distinct()

    # Get today's lessons
    today = timezone.now().date()
    today_lessons = teacher_profile.lessons.filter(timeslot__weekday=today.weekday())

    # Get recent assessments
    recent_assessments = Assessment.objects.filter(
        subject__in=teacher_profile.subjects.all()
    ).order_by("-due_date")[:5]

    # Get pending grades to enter
    pending_grades = Assessment.objects.filter(
        subject__in=teacher_profile.subjects.all(), grades__isnull=True
    ).distinct()

    context = {
        "teacher_profile": teacher_profile,
        "teacher_classes": teacher_classes,
        "today_lessons": today_lessons,
        "recent_assessments": recent_assessments,
        "pending_grades": pending_grades,
    }

    return render(request, "dashboard/teacher_dashboard.html", context)


@login_required
def student_dashboard(request):
    """Student dashboard with academic and attendance information"""
    if request.user.role != "STUDENT":
        messages.error(request, "Access denied. Student privileges required.")
        return redirect("/")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("/")

    # Get today's timetable
    today = timezone.now().date()
    today_lessons = (
        student_profile.classroom.lessons.filter(timeslot__weekday=today.weekday())
        .select_related("subject", "teacher__user", "timeslot")
        .order_by("timeslot__start_time")
    )

    # Get recent grades
    recent_grades = (
        Grade.objects.filter(student=student_profile)
        .select_related("assessment__subject", "assessment__assessment_type")
        .order_by("-graded_at")[:5]
    )

    # Get upcoming assessments (used as recent assignments on dashboard)
    upcoming_assessments = (
        Assessment.objects.filter(
            classroom=student_profile.classroom, due_date__gte=today
        )
        .select_related("subject", "assessment_type")
        .order_by("due_date")[:5]
    )

    # Pending assignments count = upcoming assessments without a grade for this student
    pending_assignments = (
        Assessment.objects.filter(
            classroom=student_profile.classroom, due_date__gte=today
        )
        .exclude(grades__student=student_profile)
        .count()
    )

    # Get attendance summary
    attendance_summary = StudentAttendance.objects.filter(
        student=student_profile, date__gte=today - timedelta(days=30)
    ).aggregate(
        present=Count("id", filter=Q(status="PRESENT")),
        absent=Count("id", filter=Q(status="ABSENT")),
        late=Count("id", filter=Q(status="LATE")),
    )

    # Attendance rate percentage
    present_count = attendance_summary.get("present") or 0
    total_attendance = (
        (attendance_summary.get("present") or 0)
        + (attendance_summary.get("absent") or 0)
        + (attendance_summary.get("late") or 0)
    )
    attendance_rate = round((present_count / total_attendance) * 100, 1) if total_attendance else 0

    # Get term grades
    current_term_grades = (
        StudentTermGrade.objects.filter(student=student_profile)
        .select_related("subject", "term")
        .order_by("subject__name")
    )

    # Average grade across terms
    average_grade = 0
    try:
        avg = student_profile.get_grade_average()
        average_grade = round(float(avg), 1) if avg is not None else 0
    except Exception:
        average_grade = 0

    context = {
        "student_profile": student_profile,
        "today_lessons": today_lessons,
        "recent_grades": recent_grades,
        "recent_assignments": upcoming_assessments,
        "attendance_summary": attendance_summary,
        "attendance_rate": attendance_rate,
        "current_term_grades": current_term_grades,
        "current_grade": getattr(student_profile.grade_level, "name", "N/A"),
        "pending_assignments": pending_assignments,
        "average_grade": average_grade,
        "terms": Term.objects.all().order_by("start_date"),
    }

    return render(request, "dashboard/student_dashboard.html", context)


@login_required
def parent_dashboard(request):
    """Parent dashboard with children's information"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied. Parent privileges required.")
        return redirect("/")

    try:
        parent_profile = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect("/")

    # Get children's information
    children = parent_profile.students.all().select_related(
        "user", "classroom", "grade_level"
    )

    # Get recent grades for all children
    recent_grades = (
        Grade.objects.filter(student__in=children)
        .select_related("student__user", "assessment__subject")
        .order_by("-graded_at")[:10]
    )

    # Get attendance summary for all children
    attendance_summary = {}
    for child in children:
        child_attendance = StudentAttendance.objects.filter(
            student=child, date__gte=timezone.now().date() - timedelta(days=30)
        ).aggregate(
            present=Count("id", filter=Q(status="PRESENT")),
            absent=Count("id", filter=Q(status="ABSENT")),
            late=Count("id", filter=Q(status="LATE")),
        )
        attendance_summary[child.id] = child_attendance

    # Get fee information
    fee_invoices = (
        Invoice.objects.filter(student__in=children)
        .select_related("student__user")
        .order_by("-issue_date")[:5]
    )

    # Get recent messages
    recent_messages = (
        Message.objects.filter(thread__participants=request.user)
        .select_related("thread", "sender")
        .order_by("-created_at")[:5]
    )

    context = {
        "parent_profile": parent_profile,
        "children": children,
        "recent_grades": recent_grades,
        "attendance_summary": attendance_summary,
        "fee_invoices": fee_invoices,
        "recent_messages": recent_messages,
        "terms": Term.objects.all().order_by("start_date"),
    }

    return render(request, "dashboard/parent_dashboard.html", context)
