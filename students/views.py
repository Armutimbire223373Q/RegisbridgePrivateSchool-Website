from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import StudentProfile
from grades.models import Grade, StudentTermGrade
from core_attendance.models import StudentAttendance
from assignments.models import Assignment, AssignmentSubmission


@login_required
def student_profile(request):
    """Student profile view"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:student_dashboard")

    context = {
        "student_profile": student_profile,
    }

    return render(request, "students/student_profile.html", context)


@login_required
def student_attendance(request):
    """Student attendance view"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:student_dashboard")

    # Get attendance records for the current academic year
    current_year = timezone.now().year
    attendance_records = StudentAttendance.objects.filter(
        student=student_profile, date__year=current_year
    ).order_by("-date")

    # Calculate attendance statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status="PRESENT").count()
    absent_days = attendance_records.filter(status="ABSENT").count()
    late_days = attendance_records.filter(status="LATE").count()

    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    # Get recent attendance (last 30 days)
    recent_date = timezone.now().date() - timedelta(days=30)
    recent_attendance = attendance_records.filter(date__gte=recent_date)

    context = {
        "student_profile": student_profile,
        "attendance_records": attendance_records[:50],  # Limit for performance
        "recent_attendance": recent_attendance,
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "late_days": late_days,
        "attendance_percentage": attendance_percentage,
    }

    return render(request, "students/student_attendance.html", context)


@login_required
def student_timetable(request):
    """Student timetable view"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:student_dashboard")

    # Get the student's classroom lessons
    if student_profile.classroom:
        lessons = student_profile.classroom.lessons.select_related(
            "subject", "teacher__user", "timeslot"
        ).order_by("timeslot__weekday", "timeslot__start_time")

        # Group lessons by weekday
        lessons_by_day = {}
        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for lesson in lessons:
            day = weekdays[lesson.timeslot.weekday]
            if day not in lessons_by_day:
                lessons_by_day[day] = []
            lessons_by_day[day].append(lesson)
    else:
        lessons = []
        lessons_by_day = {}

    # Get today's lessons
    today = timezone.now().date()
    today_lessons = []
    if student_profile.classroom:
        today_lessons = (
            student_profile.classroom.lessons.filter(timeslot__weekday=today.weekday())
            .select_related("subject", "teacher__user", "timeslot")
            .order_by("timeslot__start_time")
        )

    context = {
        "student_profile": student_profile,
        "lessons": lessons,
        "lessons_by_day": lessons_by_day,
        "today_lessons": today_lessons,
        "weekdays": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    }

    return render(request, "students/student_timetable.html", context)
