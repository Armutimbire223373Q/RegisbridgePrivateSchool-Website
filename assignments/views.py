from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Assignment, AssignmentSubmission
from teachers.models import TeacherProfile
from students.models import StudentProfile


@login_required
def assignment_list(request):
    """List assignments for current user"""
    user = request.user

    if user.role == "STUDENT":
        try:
            student_profile = StudentProfile.objects.get(user=user)
            assignments = (
                Assignment.objects.filter(
                    status="PUBLISHED",
                    subject__grade_levels=student_profile.grade_level,
                )
                .select_related("subject", "created_by")
                .order_by("-due_date")
            )
        except StudentProfile.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect("dashboard:main")

    elif user.role == "TEACHER":
        assignments = (
            Assignment.objects.filter(created_by=user)
            .select_related("subject", "term")
            .order_by("-created_at")
        )

    else:
        return HttpResponseForbidden("Access denied")

    # Paginate assignments
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get("page")
    assignments_page = paginator.get_page(page_number)

    context = {
        "assignments": assignments_page,
        "user_role": user.role,
    }

    return render(request, "assignments/assignment_list.html", context)


@login_required
def assignment_detail(request, assignment_id):
    """View assignment details"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    user = request.user

    # Check access permissions
    if user.role == "STUDENT":
        try:
            student_profile = StudentProfile.objects.get(user=user)
            if assignment.subject not in student_profile.grade_level.subjects.all():
                return HttpResponseForbidden("You don't have access to this assignment")

            # Get student's submission if exists
            submission = assignment.submissions.filter(student=student_profile).first()

        except StudentProfile.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect("dashboard:main")

    elif user.role == "TEACHER":
        if assignment.created_by != user:
            return HttpResponseForbidden("You don't have access to this assignment")

        # Get all submissions for teacher view
        submissions = assignment.submissions.select_related("student__user").order_by(
            "-submitted_at"
        )
        submission = None

    else:
        return HttpResponseForbidden("Access denied")

    context = {
        "assignment": assignment,
        "submission": submission if user.role == "STUDENT" else None,
        "submissions": submissions if user.role == "TEACHER" else None,
        "user_role": user.role,
    }

    return render(request, "assignments/assignment_detail.html", context)


@login_required
def submit_assignment(request, assignment_id):
    """Submit assignment (student only)"""
    if request.user.role != "STUDENT":
        return HttpResponseForbidden("Access denied")

    assignment = get_object_or_404(Assignment, id=assignment_id, status="PUBLISHED")

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:main")

    # Check if student can access this assignment
    if assignment.subject not in student_profile.grade_level.subjects.all():
        return HttpResponseForbidden("You don't have access to this assignment")

    # Check if assignment is still open
    if assignment.is_overdue and not assignment.allow_late_submission:
        messages.error(
            request, "This assignment is overdue and late submissions are not allowed."
        )
        return redirect("assignments:detail", assignment_id=assignment.id)

    # Get existing submission if any
    existing_submission = assignment.submissions.filter(student=student_profile).first()

    # Check resubmission rules
    if existing_submission and not assignment.allow_resubmission:
        messages.error(
            request,
            "You have already submitted this assignment and resubmission is not allowed.",
        )
        return redirect("assignments:detail", assignment_id=assignment.id)

    if request.method == "POST":
        content = request.POST.get("content", "")
        attachment = request.FILES.get("attachment")

        if content or attachment:
            # Calculate submission number
            submission_number = 1
            if existing_submission and assignment.allow_resubmission:
                submission_number = existing_submission.submission_number + 1

            # Create new submission
            submission = AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student_profile,
                content=content,
                attachment=attachment,
                submission_number=submission_number,
            )

            messages.success(request, "Assignment submitted successfully.")
            return redirect("assignments:detail", assignment_id=assignment.id)
        else:
            messages.error(request, "Please provide either content or attachment.")

    context = {
        "assignment": assignment,
        "existing_submission": existing_submission,
        "student_profile": student_profile,
    }

    return render(request, "assignments/submit_assignment.html", context)


@login_required
def grade_submission(request, submission_id):
    """Grade a submission (teacher only)"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    submission = get_object_or_404(AssignmentSubmission, id=submission_id)

    # Check if teacher created this assignment
    if submission.assignment.created_by != request.user:
        return HttpResponseForbidden(
            "You don't have permission to grade this submission"
        )

    if request.method == "POST":
        marks = request.POST.get("marks")
        feedback = request.POST.get("feedback", "")

        if marks:
            try:
                marks_value = float(marks)
                if 0 <= marks_value <= submission.assignment.max_marks:
                    submission.grade_submission(marks_value, feedback, request.user)
                    messages.success(
                        request,
                        f"Submission graded successfully. Marks: {marks_value}/{submission.assignment.max_marks}",
                    )
                    return redirect(
                        "assignments:detail", assignment_id=submission.assignment.id
                    )
                else:
                    messages.error(
                        request,
                        f"Marks must be between 0 and {submission.assignment.max_marks}",
                    )
            except ValueError:
                messages.error(request, "Invalid marks format")
        else:
            messages.error(request, "Please enter marks")

    context = {
        "submission": submission,
        "assignment": submission.assignment,
    }

    return render(request, "assignments/grade_submission.html", context)
