from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Avg

from students.models import StudentProfile
from .models import Grade, StudentTermGrade, Term
from reports.utils import generate_student_grade_pdf


@login_required
def student_grades(request):
    """Student view of their grades"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:student_dashboard")

    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get individual grades
    grades = (
        Grade.objects.filter(student=student_profile)
        .select_related(
            "assessment__subject", "assessment__assessment_type", "assessment__term"
        )
        .order_by("-graded_at")
    )

    # Get term grades
    term_grades = (
        StudentTermGrade.objects.filter(student=student_profile)
        .select_related("subject", "term")
        .order_by("term__name", "subject__name")
    )

    # Calculate overall statistics
    overall_average = grades.aggregate(avg=Avg("marks_obtained"))["avg"] or 0

    # Group grades by subject
    grades_by_subject = {}
    for grade in grades:
        subject_name = grade.assessment.subject.name
        if subject_name not in grades_by_subject:
            grades_by_subject[subject_name] = []
        grades_by_subject[subject_name].append(grade)

    context = {
        "student_profile": student_profile,
        "grades": grades,
        "term_grades": term_grades,
        "grades_by_subject": grades_by_subject,
        "overall_average": overall_average,
        "active_term": active_term,
    }

    return render(request, "grades/student_grades.html", context)


@login_required
def student_grade_report(request, term_id=None):
    """Detailed grade report for a specific term"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:student_dashboard")

    # Get specified term or current active term
    if term_id:
        term = Term.objects.get(id=term_id)
    else:
        term = Term.objects.filter(is_active=True).first()

    if not term:
        messages.warning(request, "No active academic term found.")
        return redirect("grades:student_grades")

    # Get grades for the term
    grades = Grade.objects.filter(
        student=student_profile, assessment__term=term
    ).select_related("assessment__subject", "assessment__assessment_type")

    # Get term grades
    term_grades = StudentTermGrade.objects.filter(
        student=student_profile, term=term
    ).select_related("subject")

    # Calculate term statistics
    term_average = term_grades.aggregate(avg=Avg("percentage"))["avg"] or 0

    context = {
        "student_profile": student_profile,
        "term": term,
        "grades": grades,
        "term_grades": term_grades,
        "term_average": term_average,
    }

    return render(request, "grades/student_grade_report.html", context)


@login_required
def download_grade_report_pdf(request, student_id, term_id=None):
    """Download student grade report as PDF"""
    if request.user.role not in ["STUDENT", "PARENT", "TEACHER", "ADMIN"]:
        return HttpResponseForbidden("Access denied")
    
    student = get_object_or_404(StudentProfile, id=student_id)
    
    # Permission check
    if request.user.role == "STUDENT" and student.user != request.user:
        return HttpResponseForbidden("Access denied")
    elif request.user.role == "PARENT":
        try:
            parent_profile = request.user.parent_profile
            if not parent_profile.can_access_student(student):
                return HttpResponseForbidden("Access denied")
        except:
            return HttpResponseForbidden("Access denied")
    
    term = None
    if term_id:
        term = get_object_or_404(Term, id=term_id)
    
    return generate_student_grade_pdf(student, term)


@login_required
def teacher_grade_reports(request):
    """Teacher view for generating grade reports"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")
    
    try:
        teacher_profile = request.user.teacher_profile
    except:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:teacher_dashboard")
    
    # Get teacher's classes
    from core_timetable.models import Lesson
    lessons = Lesson.objects.filter(teacher=teacher_profile).select_related('classroom', 'subject')
    classrooms = set(lesson.classroom for lesson in lessons)
    
    context = {
        "teacher_profile": teacher_profile,
        "classrooms": classrooms,
        "terms": Term.objects.all(),
    }
    
    return render(request, "grades/teacher_grade_reports.html", context)
