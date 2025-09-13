from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from datetime import datetime, timedelta

from .models import TeacherProfile, Subject
from students.models import StudentProfile, ClassRoom
from grades.models import (
    Assessment,
    Grade,
    AcademicYear,
    Term,
    AssessmentType,
    StudentTermGrade,
)
from assignments.models import Assignment, AssignmentSubmission
from core_attendance.models import (
    AttendanceSession,
    AttendanceRecord,
    StudentAttendance,
)
from messaging.models import Thread, Message
from core_timetable.models import Lesson, TimeSlot


@login_required
def teacher_portal(request):
    """Main teacher portal dashboard"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    # Get teacher's classes and subjects
    teacher_classes = ClassRoom.objects.filter(
        lessons__teacher=teacher_profile
    ).distinct()
    subjects = teacher_profile.subjects.all()

    # Get today's schedule
    today = timezone.now().date()
    today_lessons = (
        Lesson.objects.filter(
            teacher=teacher_profile, timeslot__weekday=today.weekday()
        )
        .select_related("subject", "classroom", "timeslot")
        .order_by("timeslot__start_time")
    )

    # Statistics
    total_students = StudentProfile.objects.filter(
        classroom__in=teacher_classes
    ).count()
    pending_assignments = (
        Assignment.objects.filter(created_by=request.user, submissions__is_graded=False)
        .distinct()
        .count()
    )

    recent_submissions = (
        AssignmentSubmission.objects.filter(assignment__created_by=request.user)
        .select_related("student", "assignment")
        .order_by("-submitted_at")[:5]
    )

    context = {
        "teacher_profile": teacher_profile,
        "teacher_classes": teacher_classes,
        "subjects": subjects,
        "today_lessons": today_lessons,
        "total_students": total_students,
        "pending_assignments": pending_assignments,
        "recent_submissions": recent_submissions,
    }

    return render(request, "teachers/portal.html", context)


@login_required
def my_classes(request):
    """View all teacher's classes"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    # Get classes with student count
    classes = (
        ClassRoom.objects.filter(lessons__teacher=teacher_profile)
        .distinct()
        .annotate(
            student_count=Count("students"),
            lesson_count=Count("lessons", filter=Q(lessons__teacher=teacher_profile)),
        )
        .order_by("name")
    )

    context = {
        "teacher_profile": teacher_profile,
        "classes": classes,
    }

    return render(request, "teachers/my_classes.html", context)


@login_required
def class_detail(request, class_id):
    """View detailed class information"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Check if teacher teaches this class
    if not classroom.lessons.filter(teacher=teacher_profile).exists():
        return HttpResponseForbidden("You don't teach this class")

    students = classroom.students.select_related("user").order_by("user__first_name")

    # Get recent attendance for this class
    recent_attendance = (
        AttendanceSession.objects.filter(classroom=classroom)
        .select_related("taken_by")
        .order_by("-date")[:10]
    )

    # Get recent assessments
    teacher_subjects = teacher_profile.subjects.all()
    recent_assessments = (
        Assessment.objects.filter(classroom=classroom, subject__in=teacher_subjects)
        .select_related("subject", "assessment_type")
        .order_by("-due_date")[:10]
    )

    context = {
        "classroom": classroom,
        "students": students,
        "recent_attendance": recent_attendance,
        "recent_assessments": recent_assessments,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/class_detail.html", context)


@login_required
def class_students(request, class_id):
    """View students in a specific class"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Check if teacher teaches this class
    if not classroom.lessons.filter(teacher=teacher_profile).exists():
        return HttpResponseForbidden("You don't teach this class")

    students = classroom.students.select_related("user", "grade_level").order_by(
        "user__first_name"
    )

    # Get grades summary for each student
    teacher_subjects = teacher_profile.subjects.all()
    for student in students:
        student.recent_grades = (
            Grade.objects.filter(
                student=student, assessment__subject__in=teacher_subjects
            )
            .select_related("assessment__subject")
            .order_by("-graded_at")[:3]
        )

    context = {
        "classroom": classroom,
        "students": students,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/class_students.html", context)


@login_required
def grades_overview(request):
    """Overview of grading tasks"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    subjects = teacher_profile.subjects.all()

    # Pending assessments to grade
    pending_assessments = (
        Assessment.objects.filter(subject__in=subjects, grades__isnull=True)
        .distinct()
        .select_related("subject", "classroom", "assessment_type")
    )

    # Recent grades entered
    recent_grades = (
        Grade.objects.filter(graded_by=request.user, assessment__subject__in=subjects)
        .select_related("student__user", "assessment__subject", "assessment__classroom")
        .order_by("-graded_at")[:20]
    )

    # My assessments
    my_assessments = (
        Assessment.objects.filter(subject__in=subjects)
        .select_related("subject", "classroom", "assessment_type")
        .order_by("-due_date")[:20]
    )

    context = {
        "teacher_profile": teacher_profile,
        "subjects": subjects,
        "pending_assessments": pending_assessments,
        "recent_grades": recent_grades,
        "my_assessments": my_assessments,
    }

    return render(request, "teachers/grades_overview.html", context)


@login_required
def create_assessment(request):
    """Create a new assessment"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    if request.method == "POST":
        title = request.POST.get("title")
        subject_id = request.POST.get("subject")
        classroom_id = request.POST.get("classroom")
        assessment_type_id = request.POST.get("assessment_type")
        term_id = request.POST.get("term")
        total_marks = request.POST.get("total_marks")
        due_date = request.POST.get("due_date")
        instructions = request.POST.get("instructions", "")

        if (
            title
            and subject_id
            and classroom_id
            and assessment_type_id
            and term_id
            and total_marks
            and due_date
        ):
            subject = get_object_or_404(
                Subject, id=subject_id, teachers=teacher_profile
            )
            classroom = get_object_or_404(ClassRoom, id=classroom_id)
            assessment_type = get_object_or_404(AssessmentType, id=assessment_type_id)
            term = get_object_or_404(Term, id=term_id)

            assessment = Assessment.objects.create(
                title=title,
                subject=subject,
                classroom=classroom,
                assessment_type=assessment_type,
                term=term,
                total_marks=int(total_marks),
                due_date=due_date,
                instructions=instructions,
                created_by=request.user,
            )

            messages.success(request, f"Assessment '{title}' created successfully.")
            return redirect("teachers:grade_assessment", assessment_id=assessment.id)
        else:
            messages.error(request, "Please fill in all required fields.")

    # Get form data
    subjects = teacher_profile.subjects.all()
    classrooms = ClassRoom.objects.filter(lessons__teacher=teacher_profile).distinct()
    assessment_types = AssessmentType.objects.all()
    terms = Term.objects.filter(academic_year__is_active=True)

    context = {
        "teacher_profile": teacher_profile,
        "subjects": subjects,
        "classrooms": classrooms,
        "assessment_types": assessment_types,
        "terms": terms,
    }

    return render(request, "teachers/create_assessment.html", context)


@login_required
def grade_assessment(request, assessment_id):
    """Grade students for a specific assessment"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    assessment = get_object_or_404(Assessment, id=assessment_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Check if teacher can grade this assessment
    if assessment.subject not in teacher_profile.subjects.all():
        return HttpResponseForbidden("You can't grade this assessment")

    students = assessment.classroom.students.select_related("user").order_by(
        "user__first_name"
    )

    # Get existing grades
    existing_grades = {
        grade.student_id: grade
        for grade in Grade.objects.filter(assessment=assessment).select_related(
            "student"
        )
    }

    if request.method == "POST":
        grades_updated = 0
        for student in students:
            marks_key = f"marks_{student.id}"
            remarks_key = f"remarks_{student.id}"

            marks = request.POST.get(marks_key)
            remarks = request.POST.get(remarks_key, "")

            if marks and marks.strip():
                try:
                    marks_value = float(marks)
                    if 0 <= marks_value <= assessment.total_marks:
                        grade, created = Grade.objects.get_or_create(
                            student=student,
                            assessment=assessment,
                            defaults={
                                "marks_obtained": marks_value,
                                "remarks": remarks,
                                "graded_by": request.user,
                            },
                        )

                        if not created:
                            grade.marks_obtained = marks_value
                            grade.remarks = remarks
                            grade.graded_by = request.user
                            grade.save()

                        grades_updated += 1
                    else:
                        messages.error(
                            request,
                            f"Invalid marks for {student.user.get_full_name()}. Must be between 0 and {assessment.total_marks}.",
                        )
                except ValueError:
                    messages.error(
                        request,
                        f"Invalid marks format for {student.user.get_full_name()}.",
                    )

        if grades_updated > 0:
            messages.success(request, f"Updated grades for {grades_updated} students.")
            return redirect("teachers:grades_overview")

    context = {
        "assessment": assessment,
        "students": students,
        "existing_grades": existing_grades,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/grade_assessment.html", context)


@login_required
def attendance_overview(request):
    """Overview of attendance tasks"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    # Get teacher's classes
    teacher_classes = ClassRoom.objects.filter(
        lessons__teacher=teacher_profile
    ).distinct()

    # Get today's attendance sessions
    today = timezone.now().date()
    today_sessions = AttendanceSession.objects.filter(
        classroom__in=teacher_classes, date=today
    ).select_related("classroom")

    # Get recent attendance sessions
    recent_sessions = (
        AttendanceSession.objects.filter(classroom__in=teacher_classes)
        .select_related("classroom")
        .order_by("-date")[:10]
    )

    context = {
        "teacher_profile": teacher_profile,
        "teacher_classes": teacher_classes,
        "today_sessions": today_sessions,
        "recent_sessions": recent_sessions,
    }

    return render(request, "teachers/attendance_overview.html", context)


@login_required
def take_attendance(request, class_id):
    """Take attendance for a specific class"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Check if teacher teaches this class
    if not classroom.lessons.filter(teacher=teacher_profile).exists():
        return HttpResponseForbidden("You don't teach this class")

    today = timezone.now().date()
    attendance_date = request.GET.get("date", today.strftime("%Y-%m-%d"))

    try:
        attendance_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = today

    # Get or create attendance session
    session, created = AttendanceSession.objects.get_or_create(
        date=attendance_date, classroom=classroom, defaults={"taken_by": request.user}
    )

    students = classroom.students.select_related("user").order_by("user__first_name")

    # Get existing attendance records
    existing_records = {
        record.student_id: record
        for record in AttendanceRecord.objects.filter(session=session).select_related(
            "student"
        )
    }

    if request.method == "POST":
        records_updated = 0
        for student in students:
            status_key = f"status_{student.id}"
            remarks_key = f"remarks_{student.id}"

            status = request.POST.get(status_key, "PRESENT")
            remarks = request.POST.get(remarks_key, "")

            record, created = AttendanceRecord.objects.get_or_create(
                session=session,
                student=student,
                defaults={"status": status, "remarks": remarks},
            )

            if not created:
                record.status = status
                record.remarks = remarks
                record.save()

            records_updated += 1

        messages.success(
            request, f"Attendance recorded for {records_updated} students."
        )
        return redirect("teachers:attendance_overview")

    context = {
        "session": session,
        "classroom": classroom,
        "students": students,
        "existing_records": existing_records,
        "attendance_date": attendance_date,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/take_attendance.html", context)


@login_required
def assignments_overview(request):
    """Overview of assignments"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    # Get teacher's assignments
    assignments = (
        Assignment.objects.filter(created_by=request.user)
        .select_related("subject", "term")
        .order_by("-created_at")
    )

    # Paginate assignments
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get("page")
    assignments_page = paginator.get_page(page_number)

    # Get pending submissions to grade
    pending_submissions = (
        AssignmentSubmission.objects.filter(
            assignment__created_by=request.user, marks_obtained__isnull=True
        )
        .select_related("student__user", "assignment")
        .order_by("-submitted_at")[:20]
    )

    context = {
        "teacher_profile": teacher_profile,
        "assignments": assignments_page,
        "pending_submissions": pending_submissions,
    }

    return render(request, "teachers/assignments_overview.html", context)


@login_required
def create_assignment(request):
    """Create a new assignment"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        subject_id = request.POST.get("subject")
        term_id = request.POST.get("term")
        due_date = request.POST.get("due_date")
        max_marks = request.POST.get("max_marks")
        instructions = request.POST.get("instructions", "")
        allow_late_submission = request.POST.get("allow_late_submission") == "on"

        if title and description and subject_id and term_id and due_date and max_marks:
            subject = get_object_or_404(
                Subject, id=subject_id, teachers=teacher_profile
            )
            term = get_object_or_404(Term, id=term_id)

            assignment = Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                term=term,
                due_date=due_date,
                max_marks=int(max_marks),
                instructions=instructions,
                allow_late_submission=allow_late_submission,
                created_by=request.user,
                status="PUBLISHED",
            )

            messages.success(request, f"Assignment '{title}' created successfully.")
            return redirect("teachers:assignment_detail", assignment_id=assignment.id)
        else:
            messages.error(request, "Please fill in all required fields.")

    # Get form data
    subjects = teacher_profile.subjects.all()
    terms = Term.objects.filter(academic_year__is_active=True)

    context = {
        "teacher_profile": teacher_profile,
        "subjects": subjects,
        "terms": terms,
    }

    return render(request, "teachers/create_assignment.html", context)


@login_required
def assignment_detail(request, assignment_id):
    """View assignment details and submissions"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    assignment = get_object_or_404(
        Assignment, id=assignment_id, created_by=request.user
    )

    # Get submissions
    submissions = (
        AssignmentSubmission.objects.filter(assignment=assignment)
        .select_related("student__user")
        .order_by("-submitted_at")
    )

    # Calculate statistics
    total_submissions = submissions.count()
    graded_count = submissions.filter(marks_obtained__isnull=False).count()
    average_score = submissions.filter(marks_obtained__isnull=False).aggregate(
        avg=Avg("marks_obtained")
    )["avg"]

    context = {
        "assignment": assignment,
        "submissions": submissions,
        "total_submissions": total_submissions,
        "graded_count": graded_count,
        "average_score": average_score,
    }

    return render(request, "teachers/assignment_detail.html", context)


@login_required
def grade_assignment(request, assignment_id):
    """Grade submissions for an assignment"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    assignment = get_object_or_404(
        Assignment, id=assignment_id, created_by=request.user
    )
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related("student__user")

    if request.method == "POST":
        updated = 0
        for sub in submissions:
            marks_key = f"marks_{sub.id}"
            feedback_key = f"feedback_{sub.id}"
            marks = request.POST.get(marks_key)
            feedback = request.POST.get(feedback_key, "")
            if marks and marks.strip():
                try:
                    mval = float(marks)
                    if 0 <= mval <= assignment.max_marks:
                        sub.marks_obtained = mval
                        sub.feedback = feedback
                        sub.is_graded = True
                        sub.graded_at = timezone.now()
                        sub.save()
                        updated += 1
                except ValueError:
                    continue
        if updated:
            messages.success(request, f"Updated grades for {updated} submissions.")
        else:
            messages.info(request, "No grades updated.")
        return redirect("teachers:assignment_detail", assignment_id=assignment.id)

    context = {
        "assignment": assignment,
        "submissions": submissions,
    }
    return render(request, "teachers/grade_assignment.html", context)


@login_required
def my_timetable(request):
    """View teacher's timetable"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard:main")

    # Get all lessons for this teacher
    lessons = (
        Lesson.objects.filter(teacher=teacher_profile)
        .select_related("subject", "classroom", "timeslot")
        .order_by("timeslot__weekday", "timeslot__start_time")
    )

    # Organize lessons by weekday
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    timetable = {}

    for i, day in enumerate(weekdays):
        timetable[day] = lessons.filter(timeslot__weekday=i)

    context = {
        "teacher_profile": teacher_profile,
        "timetable": timetable,
        "weekdays": weekdays,
    }

    return render(request, "teachers/timetable.html", context)


@login_required
def teacher_messages(request):
    """View teacher's messages"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    # Get threads where teacher is a participant
    threads = (
        Thread.objects.filter(participants=request.user)
        .prefetch_related("messages", "participants")
        .order_by("-created_at")
    )

    context = {
        "threads": threads,
    }

    return render(request, "teachers/messages.html", context)


@login_required
def compose_message(request):
    """Compose a new message"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        recipient_ids = request.POST.getlist("recipients")

        if title and content and recipient_ids:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            recipients = User.objects.filter(id__in=recipient_ids)

            if recipients.exists():
                thread = Thread.objects.create(title=title, created_by=request.user)
                thread.participants.set([request.user] + list(recipients))

                Message.objects.create(
                    thread=thread, sender=request.user, content=content
                )

                messages.success(request, "Message sent successfully.")
                return redirect("teachers:messages")
            else:
                messages.error(request, "Invalid recipients selected.")
        else:
            messages.error(request, "Please fill in all fields.")

    # Get potential recipients (students and parents)
    from django.contrib.auth import get_user_model

    User = get_user_model()

    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    teacher_classes = ClassRoom.objects.filter(
        lessons__teacher=teacher_profile
    ).distinct()

    students = (
        User.objects.filter(
            role="STUDENT", student_profile__classroom__in=teacher_classes
        )
        .select_related("student_profile")
        .order_by("first_name")
    )

    parents = (
        User.objects.filter(
            role="PARENT", parent_profile__students__classroom__in=teacher_classes
        )
        .distinct()
        .select_related("parent_profile")
        .order_by("first_name")
    )

    context = {
        "students": students,
        "parents": parents,
    }

    return render(request, "teachers/compose_message.html", context)


@login_required
def message_class(request, class_id):
    """Send a message to an entire class"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Ensure teacher teaches this class
    if not classroom.lessons.filter(teacher=teacher_profile).exists():
        return HttpResponseForbidden("You don't teach this class")

    if request.method == "POST":
        title = request.POST.get("title") or f"Message to {classroom.name}"
        content = request.POST.get("content")
        include_parents = request.POST.get("include_parents") == "on"

        if content:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            student_users = User.objects.filter(
                role="STUDENT", student_profile__classroom=classroom
            )

            recipients = list(student_users)
            if include_parents:
                parent_users = User.objects.filter(
                    role="PARENT", parent_profile__students__classroom=classroom
                ).distinct()
                recipients += list(parent_users)

            thread = Thread.objects.create(title=title, created_by=request.user)
            thread.participants.set([request.user] + recipients)
            Message.objects.create(thread=thread, sender=request.user, content=content)
            messages.success(request, "Message sent to class participants.")
            return redirect("teachers:messages")
        else:
            messages.error(request, "Please provide message content.")

    context = {
        "classroom": classroom,
    }
    return render(request, "teachers/message_class.html", context)


@login_required
def student_grades(request, student_id):
    """View grades for a specific student (teacher view)"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    student = get_object_or_404(StudentProfile, id=student_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Check if teacher teaches this student
    teacher_classes = ClassRoom.objects.filter(lessons__teacher=teacher_profile)
    if student.classroom not in teacher_classes:
        return HttpResponseForbidden("You don't teach this student")

    # Get grades for teacher's subjects
    teacher_subjects = teacher_profile.subjects.all()
    grades = (
        Grade.objects.filter(student=student, assessment__subject__in=teacher_subjects)
        .select_related("assessment__subject", "assessment__assessment_type")
        .order_by("-graded_at")
    )

    context = {
        "student": student,
        "grades": grades,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/student_grades.html", context)


@login_required
def attendance_report(request, class_id):
    """Attendance report for a class over a date range"""
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Access denied")

    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Ensure teacher teaches this class
    if not classroom.lessons.filter(teacher=teacher_profile).exists():
        return HttpResponseForbidden("You don't teach this class")

    # Parse date range
    today = timezone.now().date()
    default_start = today - timedelta(days=30)
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    try:
        start_date = (
            datetime.strptime(start_str, "%Y-%m-%d").date()
            if start_str
            else default_start
        )
    except ValueError:
        start_date = default_start
    try:
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else today
    except ValueError:
        end_date = today

    sessions = AttendanceSession.objects.filter(
        classroom=classroom, date__range=(start_date, end_date)
    ).order_by("date")

    records = AttendanceRecord.objects.filter(session__in=sessions).select_related(
        "student", "session"
    )

    # Initialize summary per student
    students = list(classroom.students.select_related("user").all())
    summary = {
        s.id: {"student": s, "PRESENT": 0, "ABSENT": 0, "LATE": 0, "EXCUSED": 0}
        for s in students
    }

    for rec in records:
        if rec.student_id in summary:
            status = getattr(rec, "status", "PRESENT")
            if status not in summary[rec.student_id]:
                summary[rec.student_id][status] = 0
            summary[rec.student_id][status] += 1

    context = {
        "classroom": classroom,
        "sessions": sessions,
        "summary": summary,
        "start_date": start_date,
        "end_date": end_date,
        "teacher_profile": teacher_profile,
    }

    return render(request, "teachers/attendance_report.html", context)
