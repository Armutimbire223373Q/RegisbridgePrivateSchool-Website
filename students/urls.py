from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("profile/", views.student_profile, name="student_profile"),
    path("attendance/", views.student_attendance, name="student_attendance"),
    path("timetable/", views.student_timetable, name="student_timetable"),
]
