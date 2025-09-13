from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="main"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("parent/", views.parent_dashboard, name="parent_dashboard"),
]
