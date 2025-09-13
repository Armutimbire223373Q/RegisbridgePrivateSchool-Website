from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from random import randint, choice

from django.contrib.auth import get_user_model
from students.models import GradeLevel, ClassRoom, Dormitory, StudentProfile
from teachers.models import Subject, TeacherProfile
from parents.models import Parent
from grades.models import (
    AcademicYear,
    Term,
    AssessmentType,
    Assessment,
    Grade,
    StudentTermGrade,
)
from core_attendance.models import (
    AttendanceSession,
    AttendanceRecord,
    StudentAttendance,
)
from fees.models import FeeStructure, Invoice, InvoiceLine, Payment
from public.models import NewsPost
from notifications.models import NotificationType, Notification, UserNotification


class Command(BaseCommand):
    help = "Seed demo data across users, academics, attendance, fees, content, notifications"

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        # Subjects
        subjects = [
            ("ENG", "English"),
            ("MAT", "Mathematics"),
            ("SCI", "Science"),
            ("SST", "Social Studies"),
            ("BIO", "Biology"),
            ("CHE", "Chemistry"),
            ("PHY", "Physics"),
        ]
        subject_objs = []
        for code, name in subjects:
            subject_objs.append(
                Subject.objects.get_or_create(code=code, defaults={"name": name})[0]
            )

        # Grade levels
        primary_levels = [f"Primary {i}" for i in range(1, 8)]
        secondary_levels = ["Form 1", "Form 2", "Form 3", "Form 4"]

        grade_objs = []
        for name in primary_levels:
            grade_objs.append(
                GradeLevel.objects.get_or_create(name=name, stage=GradeLevel.PRIMARY)[0]
            )
        for name in secondary_levels:
            grade_objs.append(
                GradeLevel.objects.get_or_create(name=name, stage=GradeLevel.SECONDARY)[
                    0
                ]
            )

        # Classrooms A/B per grade
        for grade in grade_objs:
            for section in ["A", "B"]:
                ClassRoom.objects.get_or_create(name=section, grade_level=grade)

        # Dormitories
        for name, cap in [
            ("St. Michael", 100),
            ("St. Raphael", 100),
            ("St. Gabriel", 120),
        ]:
            Dormitory.objects.get_or_create(name=name, defaults={"capacity": cap})

        # Sample users
        if not User.objects.filter(username="teacher1").exists():
            tuser = User.objects.create_user(
                username="teacher1",
                email="teacher1@example.com",
                password="Teacher123!",
                role=User.Role.TEACHER,
                is_staff=True,
            )
            tprofile = TeacherProfile.objects.create(user=tuser)
            tprofile.subjects.set(list(Subject.objects.filter(code__in=["ENG", "MAT"])))

        if not User.objects.filter(username="student1").exists():
            suser = User.objects.create_user(
                username="student1",
                email="student1@example.com",
                password="Student123!",
                role=User.Role.STUDENT,
            )
            p1 = GradeLevel.objects.get(name="Primary 1")
            cA = ClassRoom.objects.get(name="A", grade_level=p1)
            dorm = Dormitory.objects.first()
            StudentProfile.objects.create(
                user=suser,
                admission_number="RB001",
                grade_level=p1,
                classroom=cA,
                is_boarder=True,
                dormitory=dorm,
            )

        if not User.objects.filter(username="parent1").exists():
            parent_user = User.objects.create_user(
                username="parent1",
                email="parent1@example.com",
                password="Parent123!",
                role=User.Role.PARENT,
            )
            # Create Parent profile and link student1
            try:
                sp = StudentProfile.objects.get(admission_number="RB001")
                parent, _ = Parent.objects.get_or_create(
                    user=parent_user, defaults={"relationship": "Father"}
                )
                parent.students.add(sp)
            except StudentProfile.DoesNotExist:
                pass

        # Extra demo users and students
        for i in range(2, 11):
            uname = f"student{i}"
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(
                    username=uname,
                    email=f"{uname}@example.com",
                    password="Student123!",
                    role=User.Role.STUDENT,
                )
                grade = choice(list(GradeLevel.objects.all()))
                classroom = (
                    ClassRoom.objects.filter(grade_level=grade).order_by("?").first()
                )
                StudentProfile.objects.create(
                    user=u,
                    admission_number=f"RB{100+i:03d}",
                    grade_level=grade,
                    classroom=classroom,
                    is_boarder=bool(randint(0, 1)),
                    dormitory=Dormitory.objects.order_by("?").first(),
                )

        # Academic year and term setup
        ay, _ = AcademicYear.objects.get_or_create(
            name="2025",
            defaults={
                "start_date": timezone.now().date().replace(month=1, day=1),
                "end_date": timezone.now().date().replace(month=12, day=31),
                "is_active": True,
            },
        )
        term1, _ = Term.objects.get_or_create(
            name="Term 1",
            academic_year=ay,
            defaults={
                "start_date": timezone.now().date().replace(month=1, day=1),
                "end_date": timezone.now().date().replace(month=4, day=30),
                "is_active": True,
            },
        )
        cat, _ = AssessmentType.objects.get_or_create(
            name="CAT", defaults={"weight": 30}
        )
        exam, _ = AssessmentType.objects.get_or_create(
            name="Exam", defaults={"weight": 70}
        )

        # Create some assessments and grades
        teacher_profile = TeacherProfile.objects.first()
        for classroom in ClassRoom.objects.all()[:4]:
            for subj in subject_objs[:3]:
                a = Assessment.objects.get_or_create(
                    title=f"{subj.name} Assessment",
                    subject=subj,
                    classroom=classroom,
                    assessment_type=cat,
                    term=term1,
                    defaults={
                        "total_marks": 100,
                        "created_by": teacher_profile.user if teacher_profile else None,
                        "due_date": timezone.now().date() + timezone.timedelta(days=7),
                        "instructions": "Answer all questions.",
                    },
                )[0]
                # Add grades for students in that classroom
                for st in StudentProfile.objects.filter(classroom=classroom):
                    marks = randint(45, 98)
                    Grade.objects.get_or_create(
                        student=st,
                        assessment=a,
                        defaults={
                            "marks_obtained": marks,
                            "graded_by": (
                                teacher_profile.user if teacher_profile else None
                            ),
                        },
                    )

        # Aggregate term grades per subject
        for st in StudentProfile.objects.all()[:20]:
            for subj in subject_objs[:3]:
                total_marks = 100
                obtained = randint(50, 95)
                StudentTermGrade.objects.get_or_create(
                    student=st,
                    subject=subj,
                    term=term1,
                    defaults={"marks_obtained": obtained, "total_marks": total_marks},
                )

        # Attendance: create last 7 days sessions and records
        today = timezone.now().date()
        for delta in range(0, 7):
            session_date = today - timezone.timedelta(days=delta)
            for classroom in ClassRoom.objects.all()[:3]:
                sess, _ = AttendanceSession.objects.get_or_create(
                    date=session_date,
                    classroom=classroom,
                    defaults={
                        "taken_by": teacher_profile.user if teacher_profile else None,
                    },
                )
                for st in StudentProfile.objects.filter(classroom=classroom):
                    status = choice(
                        ["PRESENT", "PRESENT", "PRESENT", "LATE", "ABSENT"]
                    )  # biased towards present
                    AttendanceRecord.objects.get_or_create(
                        session=sess, student=st, defaults={"status": status}
                    )
                    StudentAttendance.objects.get_or_create(
                        date=session_date,
                        student=st,
                        defaults={
                            "status": status,
                            "recorded_by": (
                                teacher_profile.user if teacher_profile else None
                            ),
                        },
                    )

        # Fees: structures, invoices, payments
        for term in [term1]:
            for grade in GradeLevel.objects.all()[:5]:
                FeeStructure.objects.get_or_create(
                    grade_level=grade,
                    fee_type="TUITION",
                    term=term,
                    defaults={"amount": 50000, "active": True},
                )

        for st in StudentProfile.objects.all()[:20]:
            inv = Invoice.objects.create(student=st, term=term1, status="ISSUED")
            InvoiceLine.objects.create(invoice=inv, description="Tuition", amount=40000)
            InvoiceLine.objects.create(
                invoice=inv, description="Boarding", amount=15000
            )
            # Partial payment
            Payment.objects.create(
                invoice=inv, amount=randint(15000, 30000), method="CASH"
            )

        # News posts
        author_user = (
            teacher_profile.user
            if teacher_profile
            else User.objects.filter(is_staff=True).first() or User.objects.first()
        )
        for i in range(1, 4):
            NewsPost.objects.get_or_create(
                slug=f"update-{i}",
                defaults={
                    "title": f"School Update {i}",
                    "content": "Placeholder news content for Regisbridge.",
                    "excerpt": "Short summary of update.",
                    "category": "announcements",
                    "author": author_user,
                    "is_published": True,
                    "published_date": timezone.now(),
                },
            )

        # Notifications
        nt, _ = NotificationType.objects.get_or_create(
            name="General",
            defaults={
                "template_subject": "Notification",
                "template_body": "{{ message }}",
            },
        )
        for u in User.objects.all()[:10]:
            n = Notification.objects.create(
                recipient=u,
                notification_type=nt,
                title="Welcome to Regisbridge",
                message="This is a demo notification.",
                priority="NORMAL",
                status="SENT",
                sent_at=timezone.now(),
            )
            UserNotification.objects.create(
                user=u, notification=n, is_read=bool(randint(0, 1))
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
