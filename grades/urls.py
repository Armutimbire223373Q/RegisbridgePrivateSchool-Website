from django.urls import path
from . import views

app_name = "grades"

urlpatterns = [
    path("", views.student_grades, name="student_grades"),
    path("report/", views.student_grade_report, name="student_grade_report"),
    path(
        "report/<int:term_id>/",
        views.student_grade_report,
        name="student_grade_report_term",
    ),
    path("pdf/<int:student_id>/", views.download_grade_report_pdf, name="download_grade_pdf"),
    path("pdf/<int:student_id>/<int:term_id>/", views.download_grade_report_pdf, name="download_grade_pdf_term"),
    path("teacher/reports/", views.teacher_grade_reports, name="teacher_grade_reports"),
]
