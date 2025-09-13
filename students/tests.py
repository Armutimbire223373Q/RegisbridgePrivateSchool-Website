from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date

from .models import StudentProfile, GradeLevel, ClassRoom
from core_attendance.models import StudentAttendance

User = get_user_model()


class StudentProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            first_name='Test',
            last_name='Student',
            password='testpass123',
            role='STUDENT'
        )
        
        self.grade_level = GradeLevel.objects.create(
            name='Grade 10',
            description='Tenth Grade'
        )
        
        self.classroom = ClassRoom.objects.create(
            name='10A',
            grade_level=self.grade_level,
            capacity=30
        )

    def test_create_student_profile(self):
        """Test student profile creation"""
        student = StudentProfile.objects.create(
            user=self.user,
            admission_number='STU001',
            grade_level=self.grade_level,
            classroom=self.classroom,
            date_of_birth=date(2005, 1, 1),
            phone_number='+1234567890',
            address='123 Test Street'
        )
        
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.admission_number, 'STU001')
        self.assertEqual(student.grade_level, self.grade_level)
        self.assertEqual(student.classroom, self.classroom)
        self.assertFalse(student.is_boarder)

    def test_student_profile_str_representation(self):
        """Test student profile string representation"""
        student = StudentProfile.objects.create(
            user=self.user,
            admission_number='STU001',
            grade_level=self.grade_level,
            classroom=self.classroom
        )
        expected = f"{student.user.get_full_name()} ({student.admission_number})"
        self.assertEqual(str(student), expected)


class StudentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            role='STUDENT'
        )
        
        # Create grade level and classroom
        self.grade_level = GradeLevel.objects.create(
            name='Grade 10',
            description='Tenth Grade'
        )
        
        self.classroom = ClassRoom.objects.create(
            name='10A',
            grade_level=self.grade_level,
            capacity=30
        )
        
        # Create student profile
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_number='STU001',
            grade_level=self.grade_level,
            classroom=self.classroom
        )

    def test_student_list_view_admin(self):
        """Test student list view for admin"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/students/')
        self.assertEqual(response.status_code, 200)

    def test_student_detail_view(self):
        """Test student detail view"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/students/{self.student_profile.id}/')
        self.assertEqual(response.status_code, 200)