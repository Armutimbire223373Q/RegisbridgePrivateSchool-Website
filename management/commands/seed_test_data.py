from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = "Seeds comprehensive test data (students, teachers, classes, subjects, assessments, attendance, fees)"

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=100, help="Number of students to create")
        parser.add_argument("--teachers", type=int, default=20, help="Number of teachers to create")
        parser.add_argument("--subjects", type=int, default=8, help="Number of subjects to create")
        parser.add_argument("--classes", type=int, default=6, help="Number of classes to create")

    def handle(self, *args, **options):
        User = get_user_model()

        # Import dependent models (best-effort across paths)
        try:
            from regisbridge.students.models import StudentProfile, GradeLevel, ClassRoom
        except Exception:
            from students.models import StudentProfile, GradeLevel, ClassRoom  # type: ignore

        try:
            from regisbridge.teachers.models import TeacherProfile, Subject
        except Exception:
            from teachers.models import TeacherProfile, Subject  # type: ignore

        try:
            from regisbridge.grades.models import AssessmentType, Assessment, Term, AcademicYear, Grade
        except Exception:
            from grades.models import AssessmentType, Assessment, Term, AcademicYear, Grade  # type: ignore

        try:
            from regisbridge.core_attendance.models import StudentAttendance
        except Exception:
            from core_attendance.models import StudentAttendance  # type: ignore

        try:
            from regisbridge.fees.models import Invoice, Payment
        except Exception:
            from fees.models import Invoice, Payment  # type: ignore

        # Grade levels and classes
        primary = GradeLevel.objects.get_or_create(name="Grade 6", stage="SECONDARY")[0]
        secondary = GradeLevel.objects.get_or_create(name="Grade 8", stage="SECONDARY")[0]
        grade_levels = [primary, secondary]

        classes = []
        for i in range(1, options["classes"] + 1):
            gl = random.choice(grade_levels)
            cls, _ = ClassRoom.objects.get_or_create(name=f"{gl.name}-{i}", grade_level=gl)
            classes.append(cls)

        # Subjects
        subjects = []
        for i in range(1, options["subjects"] + 1):
            subj, _ = Subject.objects.get_or_create(name=f"Subject {i}", defaults={"code": f"SUB{i:02d}"})
            subjects.append(subj)

        # Teachers
        teachers = []
        for i in range(1, options["teachers"] + 1):
            username = f"teacher{i:03d}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": "Teacher",
                    "last_name": f"{i:03d}",
                    "email": f"{username}@example.com",
                    "role": "TEACHER",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            # Attach teacher profile if exists
            try:
                tp, _ = TeacherProfile.objects.get_or_create(user=user)
                # Assign random subjects
                if hasattr(tp, "subjects"):
                    tp.subjects.set(random.sample(subjects, k=min(3, len(subjects))))
            except Exception:
                pass
            teachers.append(user)

        # Students
        students = []
        for i in range(1, options["students"] + 1):
            username = f"student{i:03d}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": "Student",
                    "last_name": f"{i:03d}",
                    "email": f"{username}@example.com",
                    "role": "STUDENT",
                },
            )
            if created:
                user.set_password("password123")
                user.save()

            cls = random.choice(classes)
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "admission_number": f"ADM{i:05d}",
                    "grade_level": cls.grade_level,
                    "classroom": cls,
                    "academic_status": "ACTIVE",
                },
            )
            students.append(profile)

        # Academic year/term and assessment type
        year, _ = AcademicYear.objects.get_or_create(
            name=f"{timezone.now().year}-{timezone.now().year+1}",
            defaults={"start_date": timezone.now().date(), "end_date": (timezone.now() + timedelta(days=300)).date(), "is_active": True},
        )
        term, _ = Term.objects.get_or_create(
            name="TERM1",
            academic_year=year,
            defaults={"start_date": timezone.now().date(), "end_date": (timezone.now() + timedelta(days=100)).date(), "is_active": True},
        )
        atype, _ = AssessmentType.objects.get_or_create(name="Assignment", defaults={"weight": 10})

        # Create a few assessments per class/subject
        assessments = []
        for cls in classes:
            for subj in random.sample(subjects, k=min(3, len(subjects))):
                for j in range(1, 4):
                    a, _ = Assessment.objects.get_or_create(
                        title=f"{subj.name} Task {j}",
                        subject=subj,
                        classroom=cls,
                        assessment_type=atype,
                        term=term,
                        defaults={"total_marks": 100, "due_date": (timezone.now() + timedelta(days=7*j)).date()},
                    )
                    assessments.append(a)

        # Random grades for some students
        for profile in students:
            my_assessments = [a for a in assessments if a.classroom_id == (profile.classroom_id or -1)]
            for a in random.sample(my_assessments, k=min(3, len(my_assessments))):
                Grade.objects.get_or_create(
                    student=profile,
                    assessment=a,
                    defaults={"marks_obtained": random.randint(50, 95)},
                )

        # Attendance last 30 days
        statuses = ["PRESENT", "ABSENT", "LATE"]
        for profile in random.sample(students, k=min(len(students), 100)):
            for d in range(0, 30):
                day = (timezone.now().date() - timedelta(days=d))
                if day.weekday() < 5:  # weekdays only
                    StudentAttendance.objects.get_or_create(
                        student=profile,
                        date=day,
                        defaults={"status": random.choices(statuses, weights=[85, 10, 5])[0]},
                    )

        # Fees: issue invoice for some students and random payments
        for profile in random.sample(students, k=min(len(students), 50)):
            inv = Invoice.objects.create(
                student=profile,
                term=f"{term.get_name_display() if hasattr(term, 'get_name_display') else term.name} {year.name}",
                total_amount=10000,
                status="ISSUED",
            )
            if random.random() < 0.6:
                Payment.objects.create(invoice=inv, amount=random.choice([3000, 5000, 10000]), method="CASH")

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {len(students)} students, {len(teachers)} teachers, {len(classes)} classes, {len(subjects)} subjects."
        ))


