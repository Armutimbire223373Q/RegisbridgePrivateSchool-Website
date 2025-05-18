from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from core.models import HomePageContent, NewsItem, Event
from school.models import (
    Employee, Department, LeaveRequest, PerformanceReview,
    TrainingProgram, EmployeeDocument, LeadershipMember,
    TuitionFee, Scholarship, ImportantDate, HostelFacility,
    StudentService, ParentResource, PaymentMethod
)
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test data for the school management system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create groups
        groups = {
            'Students': Group.objects.get_or_create(name='Students')[0],
            'Parents': Group.objects.get_or_create(name='Parents')[0],
            'Teachers': Group.objects.get_or_create(name='Teachers')[0],
            'Admin': Group.objects.get_or_create(name='Admin')[0],
            'Accountant': Group.objects.get_or_create(name='Accountant')[0],
            'Librarian': Group.objects.get_or_create(name='Librarian')[0],
            'Nurse': Group.objects.get_or_create(name='Nurse')[0],
            'BoardingStaff': Group.objects.get_or_create(name='BoardingStaff')[0],
        }

        # Create test users
        users = {
            'student1': self.create_user('student1', 'Student One', groups['Students']),
            'student2': self.create_user('student2', 'Student Two', groups['Students']),
            'parent1': self.create_user('parent1', 'Parent One', groups['Parents']),
            'teacher1': self.create_user('teacher1', 'Teacher One', groups['Teachers']),
            'teacher2': self.create_user('teacher2', 'Teacher Two', groups['Teachers']),
            'admin1': self.create_user('admin1', 'Admin One', groups['Admin'], is_staff=True),
            'accountant1': self.create_user('accountant1', 'Accountant One', groups['Accountant']),
            'librarian1': self.create_user('librarian1', 'Librarian One', groups['Librarian']),
            'nurse1': self.create_user('nurse1', 'Nurse One', groups['Nurse']),
            'boarding1': self.create_user('boarding1', 'Boarding Staff One', groups['BoardingStaff']),
        }

        # Create departments
        departments = {
            'Academic': Department.objects.get_or_create(name='Academic', code='ACAD')[0],
            'Administration': Department.objects.get_or_create(name='Administration', code='ADMN')[0],
            'Finance': Department.objects.get_or_create(name='Finance', code='FIN')[0],
            'Library': Department.objects.get_or_create(name='Library', code='LIB')[0],
            'Health': Department.objects.get_or_create(name='Health', code='HLTH')[0],
            'Boarding': Department.objects.get_or_create(name='Boarding', code='BRD')[0],
        }

        # Create employees
        employees = {}
        for user in users.values():
            if not user.groups.filter(name='Students').exists() and not user.groups.filter(name='Parents').exists():
                dept = departments['Academic'] if user.groups.filter(name='Teachers').exists() else departments['Administration']
                employee, created = Employee.objects.get_or_create(
                    user=user,
                    defaults={
                        'department': dept,
                        'employee_id': f'EMP{random.randint(1000, 9999)}',
                        'designation': 'Teacher' if user.groups.filter(name='Teachers').exists() else 'Staff',
                        'date_joined': timezone.now() - timedelta(days=random.randint(1, 365)),
                        'status': 'ACTIVE',
                        'contact_number': f'+1234567{random.randint(1000, 9999)}',
                        'emergency_contact': f'+1987654{random.randint(1000, 9999)}',
                        'address': f'{random.randint(1, 999)} Test Street, Test City',
                        'salary': random.randint(30000, 80000)
                    }
                )
                employees[user.username] = employee

        # Create leave requests
        for employee in Employee.objects.all():
            LeaveRequest.objects.get_or_create(
                employee=employee,
                leave_type='ANNUAL',
                start_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(31, 60)),
                reason='Test leave request',
                status='PENDING'
            )

        # Create performance reviews
        for employee in Employee.objects.all():
            PerformanceReview.objects.get_or_create(
                employee=employee,
                reviewer=User.objects.filter(groups__name='Admin').first(),
                review_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                performance_score=random.randint(1, 5),
                strengths='Test strengths',
                areas_for_improvement='Test areas for improvement',
                goals='Test goals',
                comments='Test comments'
            )

        # Create training programs
        teacher = Employee.objects.filter(user__groups__name='Teachers').first()
        if teacher:
            for i in range(5):
                program = TrainingProgram.objects.get_or_create(
                    title=f'Training Program {i+1}',
                    defaults={
                        'description': f'Description for Training Program {i+1}',
                        'start_date': timezone.now() + timedelta(days=random.randint(1, 30)),
                        'end_date': timezone.now() + timedelta(days=random.randint(31, 60)),
                        'max_participants': random.randint(10, 30),
                        'instructor': teacher,
                        'is_active': True
                    }
                )[0]
                program.participants.add(*Employee.objects.all()[:random.randint(1, 5)])

        # Create leadership members
        positions = ['Principal', 'Vice Principal', 'Head of Academics', 'Head of Administration', 'Head of Finance']
        for position in positions:
            LeadershipMember.objects.get_or_create(
                name=f'Dr. {position.replace("Head of ", "")}',
                position=position,
                bio=f'Experienced education leader with over 15 years in {position} role.',
                email=f'{position.lower().replace(" ", ".")}@regisbridge.edu',
                phone=f'+1234567{random.randint(1000, 9999)}',
                is_active=True
            )

        # Create tuition fees
        grades = ['Grade 1-3', 'Grade 4-6', 'Grade 7-9', 'Grade 10-12']
        for grade in grades:
            TuitionFee.objects.get_or_create(
                grade_level=grade,
                amount=random.randint(5000, 15000),
                term='ANNUAL',
                description=f'Tuition fee for {grade}',
                is_active=True
            )

        # Create scholarships
        types = ['Academic Excellence', 'Sports', 'Arts', 'Need-based']
        for type_ in types:
            Scholarship.objects.get_or_create(
                name=f'{type_} Scholarship',
                description=f'Scholarship for students excelling in {type_}',
                amount=random.randint(1000, 5000),
                criteria=f'Must demonstrate exceptional performance in {type_}',
                is_active=True
            )

        # Create important dates
        events = ['First Day of School', 'Parent-Teacher Meeting', 'Sports Day', 'Annual Day', 'Final Exams']
        for event in events:
            ImportantDate.objects.get_or_create(
                title=event,
                date=timezone.now() + timedelta(days=random.randint(1, 180)),
                description=f'Important school event: {event}',
                is_active=True
            )

        # Create hostel facilities
        facilities = ['Boys Hostel A', 'Boys Hostel B', 'Girls Hostel A', 'Girls Hostel B']
        for facility in facilities:
            HostelFacility.objects.get_or_create(
                name=facility,
                capacity=random.randint(50, 100),
                description=f'Modern accommodation facility with all amenities for {facility}',
                fee_per_semester=random.randint(2000, 4000),
                is_available=True
            )

        # Create student services
        services = ['Transportation', 'Cafeteria', 'Sports Complex', 'Computer Lab', 'Science Lab']
        for service in services:
            StudentService.objects.get_or_create(
                name=service,
                description=f'Essential student service: {service}',
                fee=random.randint(100, 500) if service in ['Transportation', 'Cafeteria'] else 0,
                is_active=True
            )

        # Create parent resources
        resources = ['Parent Handbook', 'Academic Calendar', 'Fee Structure', 'School Policies', 'Contact Directory']
        for resource in resources:
            ParentResource.objects.get_or_create(
                title=resource,
                description=f'Important resource for parents: {resource}',
                file_url=f'https://example.com/{resource.lower().replace(" ", "-")}.pdf',
                is_active=True
            )

        # Create payment methods
        methods = ['Credit Card', 'Bank Transfer', 'Cash', 'Check', 'Online Payment']
        for method in methods:
            PaymentMethod.objects.get_or_create(
                name=method,
                description=f'Payment can be made via {method}',
                instructions=f'Instructions for {method} payment...',
                is_active=True
            )

        self.stdout.write(self.style.SUCCESS('Successfully created test data'))

    def create_user(self, username, full_name, group, is_staff=False):
        names = full_name.split(' ')
        first_name = names[0]
        last_name = ' '.join(names[1:]) if len(names) > 1 else ''
        user = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{username}@regisbridge.edu',
                'is_staff': is_staff
            }
        )[0]
        user.set_password('testpass123')
        user.groups.add(group)
        user.save()
        return user 