"""
Data migration script from Django to FastAPI
"""

import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

# Add parent directory to path for Django access
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regisbridge.settings.base')

import django
django.setup()

from api.database import SessionLocal, create_tables
from models.models import (
    User, StudentProfile, TeacherProfile, Parent, GradeLevel, ClassRoom,
    Dormitory, Subject, AcademicYear, Term, Assessment, Grade,
    AttendanceSession, AttendanceRecord, FeeStructure, Invoice,
    UserRole, Gender, BloodGroup, AcademicStatus, RelationshipType,
    AssessmentType, AttendanceStatus, FeeType, InvoiceStatus
)

def migrate_users():
    """Migrate users from Django to FastAPI"""
    print("Migrating users...")
    
    from django.contrib.auth.models import User as DjangoUser
    from api.auth import get_password_hash
    
    db = SessionLocal()
    try:
        django_users = DjangoUser.objects.all()
        
        for django_user in django_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == django_user.username).first()
            if existing_user:
                continue
            
            # Create new user
            user = User(
                username=django_user.username,
                email=django_user.email,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                password_hash=django_user.password,  # Django already hashes passwords
                is_active=django_user.is_active,
                is_staff=django_user.is_staff,
                is_superuser=django_user.is_superuser,
                role=getattr(django_user, 'role', UserRole.STUDENT),
                is_boarder=getattr(django_user, 'is_boarder', False),
                last_login=django_user.last_login,
                date_joined=django_user.date_joined
            )
            
            db.add(user)
        
        db.commit()
        print(f"✅ Migrated {len(django_users)} users")
        
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_grade_levels():
    """Migrate grade levels"""
    print("Migrating grade levels...")
    
    try:
        from students.models import GradeLevel as DjangoGradeLevel
        
        db = SessionLocal()
        django_grade_levels = DjangoGradeLevel.objects.all()
        
        for django_gl in django_grade_levels:
            existing = db.query(GradeLevel).filter(GradeLevel.name == django_gl.name).first()
            if existing:
                continue
            
            grade_level = GradeLevel(
                name=django_gl.name,
                level=django_gl.level,
                description=getattr(django_gl, 'description', None)
            )
            
            db.add(grade_level)
        
        db.commit()
        print(f"✅ Migrated {len(django_grade_levels)} grade levels")
        
    except Exception as e:
        print(f"❌ Error migrating grade levels: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_classrooms():
    """Migrate classrooms"""
    print("Migrating classrooms...")
    
    try:
        from classes.models import Classroom as DjangoClassroom
        
        db = SessionLocal()
        django_classrooms = DjangoClassroom.objects.all()
        
        for django_classroom in django_classrooms:
            existing = db.query(ClassRoom).filter(ClassRoom.code == django_classroom.code).first()
            if existing:
                continue
            
            classroom = ClassRoom(
                name=django_classroom.name,
                code=django_classroom.code,
                capacity=getattr(django_classroom, 'capacity', 30),
                description=getattr(django_classroom, 'description', None)
            )
            
            db.add(classroom)
        
        db.commit()
        print(f"✅ Migrated {len(django_classrooms)} classrooms")
        
    except Exception as e:
        print(f"❌ Error migrating classrooms: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_dormitories():
    """Migrate dormitories"""
    print("Migrating dormitories...")
    
    try:
        from students.models import Dormitory as DjangoDormitory
        
        db = SessionLocal()
        django_dormitories = DjangoDormitory.objects.all()
        
        for django_dorm in django_dormitories:
            existing = db.query(Dormitory).filter(Dormitory.name == django_dorm.name).first()
            if existing:
                continue
            
            dormitory = Dormitory(
                name=django_dorm.name,
                gender=Gender.MALE if django_dorm.gender == 'MALE' else Gender.FEMALE,
                capacity=getattr(django_dorm, 'capacity', 20),
                description=getattr(django_dorm, 'description', None)
            )
            
            db.add(dormitory)
        
        db.commit()
        print(f"✅ Migrated {len(django_dormitories)} dormitories")
        
    except Exception as e:
        print(f"❌ Error migrating dormitories: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_students():
    """Migrate student profiles"""
    print("Migrating student profiles...")
    
    try:
        from students.models import StudentProfile as DjangoStudentProfile
        
        db = SessionLocal()
        django_students = DjangoStudentProfile.objects.all()
        
        for django_student in django_students:
            # Get the corresponding user
            user = db.query(User).filter(User.username == django_student.user.username).first()
            if not user:
                continue
            
            # Get grade level
            grade_level = db.query(GradeLevel).filter(GradeLevel.name == django_student.grade_level.name).first()
            if not grade_level:
                continue
            
            # Get classroom
            classroom = None
            if django_student.classroom:
                classroom = db.query(ClassRoom).filter(ClassRoom.code == django_student.classroom.code).first()
            
            # Get dormitory
            dormitory = None
            if django_student.dormitory:
                dormitory = db.query(Dormitory).filter(Dormitory.name == django_student.dormitory.name).first()
            
            existing = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
            if existing:
                continue
            
            student = StudentProfile(
                user_id=user.id,
                admission_number=django_student.admission_number,
                grade_level_id=grade_level.id,
                classroom_id=classroom.id if classroom else None,
                is_boarder=django_student.is_boarder,
                dormitory_id=dormitory.id if dormitory else None,
                date_of_birth=django_student.date_of_birth,
                gender=Gender(django_student.gender) if django_student.gender else None,
                blood_group=BloodGroup(django_student.blood_group) if django_student.blood_group else None,
                nationality=django_student.nationality,
                enrollment_date=django_student.enrollment_date,
                expected_graduation=django_student.expected_graduation,
                previous_school=django_student.previous_school,
                academic_status=AcademicStatus(django_student.academic_status),
                medical_conditions=django_student.medical_conditions,
                allergies=django_student.allergies
            )
            
            db.add(student)
        
        db.commit()
        print(f"✅ Migrated {len(django_students)} student profiles")
        
    except Exception as e:
        print(f"❌ Error migrating students: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_teachers():
    """Migrate teacher profiles"""
    print("Migrating teacher profiles...")
    
    try:
        from teachers.models import TeacherProfile as DjangoTeacherProfile
        
        db = SessionLocal()
        django_teachers = DjangoTeacherProfile.objects.all()
        
        for django_teacher in django_teachers:
            # Get the corresponding user
            user = db.query(User).filter(User.username == django_teacher.user.username).first()
            if not user:
                continue
            
            existing = db.query(TeacherProfile).filter(TeacherProfile.user_id == user.id).first()
            if existing:
                continue
            
            teacher = TeacherProfile(
                user_id=user.id,
                employee_id=django_teacher.employee_id,
                phone_number=django_teacher.phone_number,
                address=django_teacher.address,
                city=django_teacher.city,
                postal_code=django_teacher.postal_code,
                country=django_teacher.country,
                qualification=django_teacher.qualification,
                specialization=django_teacher.specialization,
                experience_years=django_teacher.experience_years,
                salary=django_teacher.salary,
                hire_date=django_teacher.hire_date,
                is_active=django_teacher.is_active
            )
            
            db.add(teacher)
        
        db.commit()
        print(f"✅ Migrated {len(django_teachers)} teacher profiles")
        
    except Exception as e:
        print(f"❌ Error migrating teachers: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_parents():
    """Migrate parent profiles"""
    print("Migrating parent profiles...")
    
    try:
        from parents.models import Parent as DjangoParent
        
        db = SessionLocal()
        django_parents = DjangoParent.objects.all()
        
        for django_parent in django_parents:
            # Get the corresponding user
            user = db.query(User).filter(User.username == django_parent.user.username).first()
            if not user:
                continue
            
            existing = db.query(Parent).filter(Parent.user_id == user.id).first()
            if existing:
                continue
            
            parent = Parent(
                user_id=user.id,
                relationship=RelationshipType(django_parent.relationship),
                phone_number=django_parent.phone_number,
                alternative_phone=django_parent.alternative_phone,
                address=django_parent.address,
                city=django_parent.city,
                postal_code=django_parent.postal_code,
                country=django_parent.country,
                emergency_contact_name=django_parent.emergency_contact_name,
                emergency_contact_phone=django_parent.emergency_contact_phone,
                emergency_contact_relationship=django_parent.emergency_contact_relationship,
                occupation=django_parent.occupation,
                employer=django_parent.employer,
                is_primary_contact=django_parent.is_primary_contact
            )
            
            db.add(parent)
            db.flush()  # Get the parent ID
            
            # Migrate student relationships
            for django_student in django_parent.students.all():
                student = db.query(StudentProfile).filter(
                    StudentProfile.admission_number == django_student.admission_number
                ).first()
                if student:
                    parent.students.append(student)
        
        db.commit()
        print(f"✅ Migrated {len(django_parents)} parent profiles")
        
    except Exception as e:
        print(f"❌ Error migrating parents: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main migration function"""
    print("🚀 Starting data migration from Django to FastAPI...")
    
    # Create tables
    print("Creating database tables...")
    create_tables()
    print("✅ Database tables created")
    
    # Migrate data
    migrate_users()
    migrate_grade_levels()
    migrate_classrooms()
    migrate_dormitories()
    migrate_students()
    migrate_teachers()
    migrate_parents()
    
    print("🎉 Data migration completed successfully!")

if __name__ == "__main__":
    main()
