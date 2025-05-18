from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .serializers import (
    StudentProfileSerializer, TeacherProfileSerializer, SubjectSerializer,
    ClassSerializer, AttendanceSerializer, GradeSerializer, AssignmentSerializer,
    EventSerializer, NewsItemSerializer
)
from students.models import StudentProfile, Attendance, Grade
from teachers.models import TeacherProfile, Subject, Class, Assignment
from core.models import Event, NewsItem

# Create your views here.

class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return StudentProfile.objects.all()
        return StudentProfile.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        student = self.get_object()
        attendance = Attendance.objects.filter(student=student)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        student = self.get_object()
        grades = Grade.objects.filter(student=student)
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)

class TeacherProfileViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TeacherProfile.objects.all()
        return TeacherProfile.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        teacher = self.get_object()
        classes = Class.objects.filter(subjects__teacher=teacher).distinct()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        class_obj = self.get_object()
        students = StudentProfile.objects.filter(classstudent__class_name=class_obj)
        serializer = StudentProfileSerializer(students, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Attendance.objects.all()
        date = self.request.query_params.get('date', None)
        student = self.request.query_params.get('student', None)
        
        if date:
            queryset = queryset.filter(date=date)
        if student:
            queryset = queryset.filter(student_id=student)
            
        return queryset

class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Grade.objects.all()
        term = self.request.query_params.get('term', None)
        student = self.request.query_params.get('student', None)
        subject = self.request.query_params.get('subject', None)
        
        if term:
            queryset = queryset.filter(term=term)
        if student:
            queryset = queryset.filter(student_id=student)
        if subject:
            queryset = queryset.filter(subject_id=subject)
            
        return queryset

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Assignment.objects.all()
        class_subject = self.request.query_params.get('class_subject', None)
        due_date = self.request.query_params.get('due_date', None)
        
        if class_subject:
            queryset = queryset.filter(class_subject_id=class_subject)
        if due_date:
            queryset = queryset.filter(due_date=due_date)
            
        return queryset

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Event.objects.all()
        is_featured = self.request.query_params.get('featured', None)
        upcoming = self.request.query_params.get('upcoming', None)
        
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        if upcoming:
            queryset = queryset.filter(end_date__gte=timezone.now())
            
        return queryset

class NewsItemViewSet(viewsets.ModelViewSet):
    serializer_class = NewsItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return NewsItem.objects.all()
        return NewsItem.objects.filter(is_published=True)
