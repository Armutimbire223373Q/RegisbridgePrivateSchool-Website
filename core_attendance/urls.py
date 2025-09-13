from django.urls import path
from . import views

urlpatterns = [
    path("classes/", views.class_list, name="attendance_classes"),
    path("take/<int:classroom_id>/", views.take_attendance, name="attendance_take"),
    path("report/class/", views.class_report, name="attendance_class_report"),
    path(
        "report/student/<int:student_id>/",
        views.student_report,
        name="attendance_student_report",
    ),
]
