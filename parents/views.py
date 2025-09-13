from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Parent
from students.models import StudentProfile
from grades.models import Grade
from core_attendance.models import StudentAttendance
from fees.models import Invoice, Payment
from messaging.models import Message, Thread
from boarding.models import BoardingStudent


@login_required
def children_list(request):
    """List all children for the parent with basic info"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied. Parent privileges required.")
        return redirect("dashboard")

    try:
        parent_profile = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect("dashboard")

    children = parent_profile.students.all().select_related(
        "user", "classroom", "grade_level"
    )

    context = {
        "children": children,
        "parent_profile": parent_profile,
    }

    return render(request, "parents/children_list.html", context)


@login_required
def child_detail(request, student_id):
    """Detailed view of a specific child's progress"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied. Parent privileges required.")
        return redirect("dashboard")

    try:
        parent_profile = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect("dashboard")

    # Get child and verify parent has access
    child = get_object_or_404(StudentProfile, id=student_id)
    if not parent_profile.can_access_student(child):
        messages.error(request, "Access denied to student information.")
        return redirect("children")

    # Get academic data
    recent_grades = (
        Grade.objects.filter(student=child)
        .select_related("assessment__subject")
        .order_by("-graded_at")[:20]
    )

    # Get attendance data
    attendance_records = StudentAttendance.objects.filter(
        student=child, date__gte=timezone.now().date() - timedelta(days=90)
    ).order_by("-date")

    attendance_stats = StudentAttendance.objects.filter(
        student=child, date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(
        present=Count("id", filter=Q(status="PRESENT")),
        absent=Count("id", filter=Q(status="ABSENT")),
        late=Count("id", filter=Q(status="LATE")),
        total=Count("id"),
    )

    # Get fee information
    invoices = Invoice.objects.filter(student=child).order_by("-issue_date")

    # Get boarding status if applicable
    boarding_status = None
    try:
        boarding_status = BoardingStudent.objects.get(student=child)
    except BoardingStudent.DoesNotExist:
        pass

    context = {
        "child": child,
        "parent_profile": parent_profile,
        "recent_grades": recent_grades,
        "attendance_records": attendance_records[:10],
        "attendance_stats": attendance_stats,
        "invoices": invoices,
        "boarding_status": boarding_status,
    }

    return render(request, "parents/child_detail.html", context)


@login_required
def child_attendance(request, student_id):
    """View detailed attendance for a specific child"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied. Parent privileges required.")
        return redirect("dashboard")

    try:
        parent_profile = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect("dashboard")

    child = get_object_or_404(StudentProfile, id=student_id)
    if not parent_profile.can_access_student(child):
        messages.error(request, "Access denied to student information.")
        return redirect("children")

    # Get attendance records
    attendance_records = StudentAttendance.objects.filter(student=child).order_by(
        "-date"
    )

    # Calculate monthly stats
    monthly_stats = {}
    for record in attendance_records[:100]:  # Last 100 records
        month_key = record.date.strftime("%Y-%m")
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                "present": 0,
                "absent": 0,
                "late": 0,
                "total": 0,
            }
        monthly_stats[month_key][record.status.lower()] += 1
        monthly_stats[month_key]["total"] += 1

    context = {
        "child": child,
        "parent_profile": parent_profile,
        "attendance_records": attendance_records[:50],  # Show last 50
        "monthly_stats": monthly_stats,
    }

    return render(request, "parents/child_attendance.html", context)


@login_required
def child_grades(request, student_id):
    """View detailed grades for a specific child"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied. Parent privileges required.")
        return redirect("dashboard")

    try:
        parent_profile = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect("dashboard")

    child = get_object_or_404(StudentProfile, id=student_id)
    if not parent_profile.can_access_student(child):
        messages.error(request, "Access denied to student information.")
        return redirect("children")

    # Get grades by subject
    grades = (
        Grade.objects.filter(student=child)
        .select_related("assessment__subject")
        .order_by("-graded_at")
    )

    # Calculate subject averages
    subject_averages = {}
    for grade in grades:
        subject = grade.assessment.subject.name
        if subject not in subject_averages:
            subject_averages[subject] = []
        subject_averages[subject].append(grade.percentage)

    # Calculate averages
    for subject in subject_averages:
        avg = sum(subject_averages[subject]) / len(subject_averages[subject])
        subject_averages[subject] = round(avg, 2)

    context = {
        "child": child,
        "parent_profile": parent_profile,
        "grades": grades,
        "subject_averages": subject_averages,
    }

    return render(request, "parents/child_grades.html", context)
