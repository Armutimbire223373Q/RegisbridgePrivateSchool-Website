from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="dashboard"),
    path("list/", views.reports_list, name="list"),
    path("generate/<int:template_id>/", views.generate_report_view, name="generate"),
    path("report/<int:report_id>/", views.report_detail, name="detail"),
    path("report/<int:report_id>/download/", views.download_report, name="download"),
    path("student-performance/", views.student_performance_report, name="student_performance"),
    path("attendance/", views.attendance_report, name="attendance"),
    path("financial/", views.financial_report, name="financial"),
    path("scheduled/", views.scheduled_reports, name="scheduled"),
    path("scheduled/create/", views.create_scheduled_report, name="create_scheduled"),
]


