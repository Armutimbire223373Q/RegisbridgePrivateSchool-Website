from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from students.models import StudentProfile
from teachers.models import Subject, TeacherProfile
from public.models import NewsPost
from core_attendance.models import StudentAttendance
from grades.models import Grade, Assessment
from fees.models import Invoice, Payment
from messaging.models import Thread, Message
from parents.models import Parent
from users.models import User

from .serializers import (
    SubjectSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentSerializer,
    NewsPostSerializer,
    StudentAttendanceSerializer,
    AssessmentSerializer,
    GradeSerializer,
    InvoiceSerializer,
    PaymentSerializer,
    MessageSerializer,
    ThreadSerializer,
    UserSerializer,
)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']


class NewsPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.filter(is_published=True)
    serializer_class = NewsPostSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content', 'excerpt']
    filterset_fields = ['category']
    ordering_fields = ['published_date', 'title']


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentProfile.objects.select_related(
        "user", "grade_level", "classroom", "dormitory"
    )
    serializer_class = StudentProfileSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__first_name', 'user__last_name', 'admission_number']
    filterset_fields = ['grade_level', 'classroom', 'is_boarder']
    ordering_fields = ['user__last_name', 'admission_number']


class TeacherProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeacherProfile.objects.select_related("user").prefetch_related("subjects")
    serializer_class = TeacherProfileSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    filterset_fields = ['is_head_of_department']
    ordering_fields = ['user__last_name', 'employee_id']


class ParentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parent.objects.select_related("user").prefetch_related("students")
    serializer_class = ParentSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__first_name', 'user__last_name', 'phone_number']
    filterset_fields = ['relationship', 'is_primary_contact']
    ordering_fields = ['user__last_name']


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.select_related("student", "recorded_by")
    serializer_class = StudentAttendanceSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['student__user__first_name', 'student__user__last_name']
    filterset_fields = ['status', 'date']
    ordering_fields = ['date', 'student__user__last_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.role == "STUDENT":
            try:
                student_profile = user.student_profile
                queryset = queryset.filter(student=student_profile)
            except:
                queryset = queryset.none()
        elif user.role == "PARENT":
            try:
                parent_profile = user.parent_profile
                student_ids = parent_profile.students.values_list('id', flat=True)
                queryset = queryset.filter(student_id__in=student_ids)
            except:
                queryset = queryset.none()
        
        return queryset


class AssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Assessment.objects.select_related("subject", "classroom", "term")
    serializer_class = AssessmentSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'instructions']
    filterset_fields = ['subject', 'classroom', 'term', 'assessment_type']
    ordering_fields = ['due_date', 'title']


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.select_related("student", "assessment", "graded_by")
    serializer_class = GradeSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'assessment__title']
    filterset_fields = ['student', 'assessment', 'graded_at']
    ordering_fields = ['graded_at', 'marks_obtained']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.role == "STUDENT":
            try:
                student_profile = user.student_profile
                queryset = queryset.filter(student=student_profile)
            except:
                queryset = queryset.none()
        elif user.role == "PARENT":
            try:
                parent_profile = user.parent_profile
                student_ids = parent_profile.students.values_list('id', flat=True)
                queryset = queryset.filter(student_id__in=student_ids)
            except:
                queryset = queryset.none()
        
        return queryset


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.select_related("student__user").prefetch_related("lines", "payments")
    serializer_class = InvoiceSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'term']
    filterset_fields = ['status', 'term', 'issue_date']
    ordering_fields = ['issue_date', 'total_amount']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.role == "STUDENT":
            try:
                student_profile = user.student_profile
                queryset = queryset.filter(student=student_profile)
            except:
                queryset = queryset.none()
        elif user.role == "PARENT":
            try:
                parent_profile = user.parent_profile
                student_ids = parent_profile.students.values_list('id', flat=True)
                queryset = queryset.filter(student_id__in=student_ids)
            except:
                queryset = queryset.none()
        
        return queryset


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("invoice__student__user")
    serializer_class = PaymentSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['invoice__student__user__first_name', 'invoice__student__user__last_name', 'reference']
    filterset_fields = ['method', 'date']
    ordering_fields = ['date', 'amount']


class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user).prefetch_related(
            'messages', 'participants'
        ).distinct()

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        thread = self.get_object()
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = Message.objects.create(
            thread=thread,
            sender=request.user,
            content=content
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Message.objects.filter(
            thread__participants=self.request.user
        ).select_related('sender', 'thread')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'username', 'email']
    filterset_fields = ['role']
    ordering_fields = ['last_name', 'username', 'date_joined']


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    user = request.user
    profile_summary = {"role": user.role}

    try:
        if user.role == "STUDENT" and hasattr(user, "student_profile"):
            student = user.student_profile
            profile_summary.update(
                {
                    "admission_number": student.admission_number,
                    "grade_level": student.grade_level_id,
                    "classroom": student.classroom_id,
                    "is_boarder": student.is_boarder,
                }
            )
        elif user.role == "TEACHER" and hasattr(user, "teacher_profile"):
            teacher = user.teacher_profile
            profile_summary.update(
                {
                    "employee_id": teacher.employee_id,
                    "subjects": list(teacher.subjects.values_list("id", flat=True)),
                    "is_head_of_department": teacher.is_head_of_department,
                }
            )
        elif user.role == "PARENT" and hasattr(user, "parent_profile"):
            parent = user.parent_profile
            profile_summary.update(
                {
                    "relationship": parent.relationship,
                    "students": list(parent.students.values_list("id", flat=True)),
                    "is_primary_contact": parent.is_primary_contact,
                }
            )
    except Exception:
        pass

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.get_full_name(),
            "email": user.email,
            "role": user.role,
            "profile": profile_summary,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the authenticated user"""
    user = request.user
    stats = {}

    if user.role == "STUDENT":
        try:
            student = user.student_profile
            stats = {
                "recent_grades": Grade.objects.filter(student=student).count(),
                "attendance_rate": _calculate_attendance_rate(student),
                "outstanding_fees": Invoice.objects.filter(
                    student=student
                ).exclude(status="PAID").count(),
                "unread_messages": Message.objects.filter(
                    thread__participants=user
                ).exclude(read_by=user).count(),
            }
        except:
            stats = {"error": "Student profile not found"}

    elif user.role == "TEACHER":
        try:
            teacher = user.teacher_profile
            stats = {
                "total_students": StudentProfile.objects.filter(
                    classroom__teachers=teacher
                ).count(),
                "pending_grades": Grade.objects.filter(
                    assessment__subject__in=teacher.subjects.all()
                ).count(),
                "unread_messages": Message.objects.filter(
                    thread__participants=user
                ).exclude(read_by=user).count(),
            }
        except:
            stats = {"error": "Teacher profile not found"}

    elif user.role == "PARENT":
        try:
            parent = user.parent_profile
            student_ids = parent.students.values_list('id', flat=True)
            stats = {
                "children_count": parent.students.count(),
                "outstanding_fees": Invoice.objects.filter(
                    student_id__in=student_ids
                ).exclude(status="PAID").count(),
                "unread_messages": Message.objects.filter(
                    thread__participants=user
                ).exclude(read_by=user).count(),
            }
        except:
            stats = {"error": "Parent profile not found"}

    elif user.role == "ADMIN":
        stats = {
            "total_students": StudentProfile.objects.count(),
            "total_teachers": TeacherProfile.objects.count(),
            "total_parents": Parent.objects.count(),
            "pending_invoices": Invoice.objects.exclude(status="PAID").count(),
        }

    return Response(stats)


def _calculate_attendance_rate(student):
    """Calculate attendance rate for a student"""
    from datetime import timedelta
    from django.utils import timezone
    
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_records = StudentAttendance.objects.filter(
        student=student,
        date__gte=thirty_days_ago
    )
    
    if not attendance_records.exists():
        return 0
    
    present_count = attendance_records.filter(status="PRESENT").count()
    total_count = attendance_records.count()
    
    return round((present_count / total_count) * 100, 2) if total_count > 0 else 0
