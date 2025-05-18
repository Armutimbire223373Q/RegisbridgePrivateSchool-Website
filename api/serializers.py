from rest_framework import serializers
from students.models import StudentProfile, Attendance, Grade
from teachers.models import TeacherProfile, Subject, Class, Assignment
from core.models import Event, NewsItem

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'student_id', 'user', 'date_of_birth', 'gender', 'address', 
                 'parent_name', 'parent_phone', 'parent_email', 'admission_date']
        read_only_fields = ['student_id']

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ['id', 'teacher_id', 'user', 'qualification', 'specialization', 
                 'joining_date', 'phone', 'address']
        read_only_fields = ['teacher_id']

class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'teacher', 'teacher_name']

class ClassSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'grade_level', 'section', 'academic_year', 'subjects']

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'date', 'status', 'notes']

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Grade
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 
                 'term', 'score', 'date', 'teacher_notes']

class AssignmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_subject.class_name.name', read_only=True)
    subject_name = serializers.CharField(source='class_subject.subject.name', read_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'class_subject', 'class_name', 
                 'subject_name', 'due_date', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 
                 'location', 'is_featured', 'created_by', 'created_by_name']

class NewsItemSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = NewsItem
        fields = ['id', 'title', 'content', 'image', 'date_posted', 
                 'author', 'author_name', 'is_published']
