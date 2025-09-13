from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet,
    NewsPostViewSet,
    StudentProfileViewSet,
    TeacherProfileViewSet,
    ParentViewSet,
    StudentAttendanceViewSet,
    AssessmentViewSet,
    GradeViewSet,
    InvoiceViewSet,
    PaymentViewSet,
    ThreadViewSet,
    MessageViewSet,
    UserViewSet,
    me,
    dashboard_stats,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"news", NewsPostViewSet, basename="news")
router.register(r"students", StudentProfileViewSet, basename="student")
router.register(r"teachers", TeacherProfileViewSet, basename="teacher")
router.register(r"parents", ParentViewSet, basename="parent")
router.register(r"attendance", StudentAttendanceViewSet, basename="attendance")
router.register(r"assessments", AssessmentViewSet, basename="assessment")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"threads", ThreadViewSet, basename="thread")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    path("me/", me, name="me"),
    path("dashboard-stats/", dashboard_stats, name="dashboard_stats"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
