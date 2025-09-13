from datetime import date

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from students.models import ClassRoom, StudentProfile
from .models import AttendanceSession, AttendanceRecord
from django.utils.dateparse import parse_date


def class_list(request):
    classes = (
        ClassRoom.objects.select_related("grade_level")
        .all()
        .order_by("grade_level__name", "name")
    )
    return render(request, "attendance/class_list.html", {"classes": classes})


def start_or_get_session(classroom_id: int, target_date: date) -> AttendanceSession:
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    session, _ = AttendanceSession.objects.get_or_create(
        classroom=classroom,
        date=target_date,
        defaults={"taken_by": None},
    )
    return session


@require_http_methods(["GET", "POST"])
def take_attendance(request, classroom_id: int):
    today = date.today()
    session = start_or_get_session(classroom_id, today)
    students = (
        StudentProfile.objects.filter(classroom=session.classroom)
        .select_related("user")
        .order_by("admission_number")
    )

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}", AttendanceRecord.PRESENT)
            remarks = request.POST.get(f"remarks_{student.id}", "")
            AttendanceRecord.objects.update_or_create(
                session=session,
                student=student,
                defaults={"status": status, "remarks": remarks},
            )
        messages.success(request, "Attendance saved.")
        return redirect(reverse("attendance_take", args=[session.classroom.id]))

    existing_records = AttendanceRecord.objects.filter(session=session)
    existing_status = {r.student_id: r.status for r in existing_records}
    existing_remarks = {r.student_id: r.remarks for r in existing_records}
    return render(
        request,
        "attendance/session_take.html",
        {
            "session": session,
            "students": students,
            "existing_status": existing_status,
            "existing_remarks": existing_remarks,
        },
    )


def class_report(request):
    classes = (
        ClassRoom.objects.select_related("grade_level")
        .all()
        .order_by("grade_level__name", "name")
    )
    classroom_id = request.GET.get("classroom")
    start = parse_date(request.GET.get("start")) if request.GET.get("start") else None
    end = parse_date(request.GET.get("end")) if request.GET.get("end") else None

    records = []
    selected_class = None
    if classroom_id and start and end:
        selected_class = get_object_or_404(ClassRoom, id=classroom_id)
        sessions = AttendanceSession.objects.filter(
            classroom=selected_class, date__range=(start, end)
        )
        records = (
            AttendanceRecord.objects.filter(session__in=sessions)
            .select_related("student__user", "session")
            .order_by("session__date", "student__admission_number")
        )

    return render(
        request,
        "attendance/class_report.html",
        {
            "classes": classes,
            "selected_class": selected_class,
            "start": start,
            "end": end,
            "records": records,
        },
    )


def student_report(request, student_id: int):
    student = get_object_or_404(
        StudentProfile.objects.select_related("user", "classroom", "grade_level"),
        id=student_id,
    )
    start = parse_date(request.GET.get("start")) if request.GET.get("start") else None
    end = parse_date(request.GET.get("end")) if request.GET.get("end") else None

    q = (
        AttendanceRecord.objects.filter(student=student)
        .select_related("session")
        .order_by("session__date")
    )
    if start and end:
        q = q.filter(session__date__range=(start, end))

    return render(
        request,
        "attendance/student_report.html",
        {
            "student": student,
            "records": q,
            "start": start,
            "end": end,
        },
    )
