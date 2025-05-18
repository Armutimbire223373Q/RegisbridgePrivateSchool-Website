from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('profile/', views.teacher_profile, name='profile'),
    path('classes/', views.class_list, name='class_list'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/attendance/', views.take_attendance, name='take_attendance'),
    path('class/<int:class_id>/subject/<int:subject_id>/grade/', views.grade_students, name='grade_students'),
    path('class/<int:class_id>/subject/<int:subject_id>/assignment/create/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/grade/', views.grade_submissions, name='grade_submissions'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('grade-assignments/', views.grade_assignments, name='grade_assignments'),
    path('view-schedule/', views.view_schedule, name='view_schedule'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
] 