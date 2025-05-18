from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('dashboard/', views.attendance_dashboard, name='dashboard'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('student/<int:student_id>/attendance/', views.get_student_attendance, name='get_student_attendance'),
] 