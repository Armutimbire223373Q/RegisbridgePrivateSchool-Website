from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('attendance/', views.attendance_list, name='attendance'),
    path('grades/', views.grade_report, name='grades'),
    path('profile/', views.profile_view, name='profile'),
]
