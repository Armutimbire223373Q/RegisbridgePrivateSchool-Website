from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentProfileViewSet, basename='student')
router.register(r'teachers', views.TeacherProfileViewSet, basename='teacher')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'grades', views.GradeViewSet, basename='grade')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'news', views.NewsItemViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
