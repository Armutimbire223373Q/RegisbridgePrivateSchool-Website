from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    # Teacher portal main
    path("", views.teacher_portal, name="portal"),
    # Class management
    path("classes/", views.my_classes, name="my_classes"),
    path("classes/<int:class_id>/", views.class_detail, name="class_detail"),
    path(
        "classes/<int:class_id>/students/", views.class_students, name="class_students"
    ),
    # Grading
    path("grades/", views.grades_overview, name="grades_overview"),
    path(
        "grades/assessment/<int:assessment_id>/",
        views.grade_assessment,
        name="grade_assessment",
    ),
    path(
        "grades/create-assessment/", views.create_assessment, name="create_assessment"
    ),
    path(
        "grades/student/<int:student_id>/", views.student_grades, name="student_grades"
    ),
    # Attendance
    path("attendance/", views.attendance_overview, name="attendance_overview"),
    path(
        "attendance/take/<int:class_id>/", views.take_attendance, name="take_attendance"
    ),
    path(
        "attendance/report/<int:class_id>/",
        views.attendance_report,
        name="attendance_report",
    ),
    # Assignments
    path("assignments/", views.assignments_overview, name="assignments_overview"),
    path("assignments/create/", views.create_assignment, name="create_assignment"),
    path(
        "assignments/<int:assignment_id>/",
        views.assignment_detail,
        name="assignment_detail",
    ),
    path(
        "assignments/<int:assignment_id>/grade/",
        views.grade_assignment,
        name="grade_assignment",
    ),
    # Messaging
    path("messages/", views.teacher_messages, name="messages"),
    path("messages/compose/", views.compose_message, name="compose_message"),
    path("messages/class/<int:class_id>/", views.message_class, name="message_class"),
    # Timetable
    path("timetable/", views.my_timetable, name="my_timetable"),
]
