from rest_framework import serializers
from students.models import StudentProfile
from teachers.models import Subject, TeacherProfile
from public.models import NewsPost
from core_attendance.models import StudentAttendance
from grades.models import Grade, Assessment
from fees.models import Invoice, Payment
from messaging.models import Thread, Message
from parents.models import Parent
from users.models import User


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "code", "name", "description"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "admission_number",
            "user_full_name",
            "user_email",
            "grade_level",
            "classroom",
            "is_boarder",
            "dormitory",
            "date_of_birth",
            "phone_number",
            "address",
        ]


class TeacherProfileSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = [
            "id",
            "employee_id",
            "user_full_name",
            "user_email",
            "subjects",
            "is_head_of_department",
            "phone_number",
            "address",
        ]


class ParentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    students = StudentProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = [
            "id",
            "user_full_name",
            "user_email",
            "relationship",
            "phone_number",
            "address",
            "students",
        ]


class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "featured_image",
            "published_date",
        ]


class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "date",
            "status",
            "remarks",
            "recorded_by",
            "recorded_at",
        ]


class AssessmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "subject",
            "subject_name",
            "classroom",
            "classroom_name",
            "assessment_type",
            "term",
            "total_marks",
            "due_date",
            "instructions",
            "created_at",
        ]


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    percentage = serializers.ReadOnlyField()
    letter_grade = serializers.ReadOnlyField()

    class Meta:
        model = Grade
        fields = [
            "id",
            "student",
            "student_name",
            "assessment",
            "assessment_title",
            "marks_obtained",
            "percentage",
            "letter_grade",
            "remarks",
            "graded_at",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    paid_amount = serializers.SerializerMethodField()
    outstanding_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "student",
            "student_name",
            "term",
            "issue_date",
            "due_date",
            "status",
            "total_amount",
            "paid_amount",
            "outstanding_amount",
        ]

    def get_paid_amount(self, obj):
        return sum(payment.amount for payment in obj.payments.all())

    def get_outstanding_amount(self, obj):
        paid = sum(payment.amount for payment in obj.payments.all())
        return obj.total_amount - paid


class PaymentSerializer(serializers.ModelSerializer):
    invoice_student = serializers.CharField(source="invoice.student.user.get_full_name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_student",
            "date",
            "amount",
            "method",
            "reference",
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "thread",
            "sender",
            "sender_name",
            "content",
            "created_at",
        ]


class ThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants_names = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            "id",
            "title",
            "created_by",
            "participants",
            "participants_names",
            "messages",
            "created_at",
        ]

    def get_participants_names(self, obj):
        return [user.get_full_name() for user in obj.participants.all()]


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active",
            "date_joined",
        ]
