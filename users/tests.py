from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'role': 'STUDENT'
        }

    def test_create_user(self):
        """Test user creation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'STUDENT')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.username} ({user.get_role_display()})"
        self.assertEqual(str(user), expected)

    def test_user_full_name(self):
        """Test user full name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_user_short_name(self):
        """Test user short name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), 'Test')

    def test_user_role_choices(self):
        """Test user role choices"""
        valid_roles = ['ADMIN', 'TEACHER', 'STUDENT', 'PARENT', 'BOARDING_STAFF']
        for role in valid_roles:
            user_data = self.user_data.copy()
            user_data['username'] = f'testuser_{role.lower()}'
            user_data['role'] = role
            user = User.objects.create_user(**user_data)
            self.assertEqual(user.role, role)

    def test_user_is_boarder_default(self):
        """Test is_boarder field default value"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_boarder)


class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'role': 'STUDENT'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_login(self):
        """Test user login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_user_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_invalid_login(self):
        """Test invalid login credentials"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Please enter a correct username and password')

    def test_authenticated_user_redirect(self):
        """Test that authenticated users are redirected from login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'STUDENT'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'role': 'STUDENT'
        })
        self.assertEqual(response.status_code, 200)  # Stay on registration page
        self.assertContains(response, 'The two password fields didn&#x27;t match')

    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        response = self.client.post(reverse('users:register'), {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'STUDENT'
        })
        self.assertEqual(response.status_code, 200)  # Stay on registration page
        self.assertContains(response, 'A user with that username already exists')


class UserProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
            role='STUDENT'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_user_profile_view(self):
        """Test user profile view"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

    def test_user_profile_update(self):
        """Test user profile update"""
        response = self.client.post(reverse('users:edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Check if profile was updated
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_password_change(self):
        """Test password change"""
        response = self.client.post(reverse('users:password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after password change
        
        # Check if password was changed
        updated_user = User.objects.get(id=self.user.id)
        self.assertTrue(updated_user.check_password('newpass123'))


class UserPermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacherpass123',
            role='TEACHER'
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            role='STUDENT'
        )

    def test_admin_access(self):
        """Test admin user access"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_access(self):
        """Test teacher user access"""
        self.client.login(username='teacher', password='teacherpass123')
        response = self.client.get('/teachers/')
        self.assertEqual(response.status_code, 200)

    def test_student_access(self):
        """Test student user access"""
        self.client.login(username='student', password='studentpass123')
        response = self.client.get('/students/')
        self.assertEqual(response.status_code, 200)

    def test_role_based_redirect(self):
        """Test role-based redirect after login"""
        # Test admin redirect
        response = self.client.post(reverse('users:login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test teacher redirect
        self.client.logout()
        response = self.client.post(reverse('users:login'), {
            'username': 'teacher',
            'password': 'teacherpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test student redirect
        self.client.logout()
        response = self.client.post(reverse('users:login'), {
            'username': 'student',
            'password': 'studentpass123'
        })
        self.assertEqual(response.status_code, 302)