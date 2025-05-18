from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from .models import StudentProfile, Attendance, Grade
from teachers.models import Subject, Class, ClassStudent

def index(request):
    return HttpResponse("Welcome to the Students app!")

@login_required
def student_dashboard(request):
    """Student dashboard showing attendance, grades, and assignments."""
    student = get_object_or_404(StudentProfile, user=request.user)
    
    # Get current class
    current_class = ClassStudent.objects.filter(student=student).first()
    
    # Get attendance for the last 30 days
    recent_attendance = Attendance.objects.filter(
        student=student,
        date__gte=timezone.now().date() - timezone.timedelta(days=30)
    ).order_by('-date')
    
    # Get grades for current term
    current_term = 'first'  # This should be determined based on the current date
    grades = Grade.objects.filter(
        student=student,
        term=current_term
    ).select_related('subject')
    
    # Calculate average grade
    avg_grade = grades.aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'student': student,
        'current_class': current_class,
        'recent_attendance': recent_attendance,
        'grades': grades,
        'avg_grade': avg_grade,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def attendance_list(request):
    """View attendance history for a student."""
    student = get_object_or_404(StudentProfile, user=request.user)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'students/attendance_list.html', {
        'attendance_records': attendance_records
    })

@login_required
def grade_report(request):
    """View detailed grade report for a student."""
    student = get_object_or_404(StudentProfile, user=request.user)
    
    # Get grades for all terms
    grades = Grade.objects.filter(student=student).select_related('subject')
    
    # Group grades by term
    term_grades = {}
    for grade in grades:
        if grade.term not in term_grades:
            term_grades[grade.term] = []
        term_grades[grade.term].append(grade)
    
    # Calculate averages for each term
    term_averages = {}
    for term, term_grade_list in term_grades.items():
        term_averages[term] = sum(g.score for g in term_grade_list) / len(term_grade_list)
    
    context = {
        'student': student,
        'term_grades': term_grades,
        'term_averages': term_averages,
    }
    return render(request, 'students/grade_report.html', context)

@login_required
def profile_view(request):
    """View and edit student profile."""
    student = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        # Update profile information
        student.address = request.POST.get('address')
        student.parent_name = request.POST.get('parent_name')
        student.parent_phone = request.POST.get('parent_phone')
        student.parent_email = request.POST.get('parent_email')
        student.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('students:profile')
    
    return render(request, 'students/profile.html', {'student': student})
