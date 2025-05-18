from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Avg
from .models import (
    TeacherProfile, Subject, Class, ClassSubject,
    ClassStudent, Assignment, AssignmentSubmission, Schedule, Announcement
)
from .forms import (
    TeacherProfileForm, SubjectForm, ClassForm,
    AssignmentForm, AssignmentSubmissionForm
)
from students.models import Attendance, Grade
from datetime import datetime, timedelta
import json

@login_required
def teacher_dashboard(request):
    """Teacher dashboard showing classes, subjects, and recent activities."""
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Get teacher's classes
    classes = ClassSubject.objects.filter(teacher=teacher).select_related('class_name', 'subject')
    
    # Get recent assignments
    recent_assignments = Assignment.objects.filter(
        class_subject__teacher=teacher
    ).select_related('class_subject__subject', 'class_subject__class_name')[:5]
    
    # Get recent submissions
    recent_submissions = AssignmentSubmission.objects.filter(
        assignment__class_subject__teacher=teacher
    ).select_related('assignment', 'student__user')[:5]
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'recent_assignments': recent_assignments,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'teachers/dashboard.html', context)

@login_required
def teacher_profile(request):
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('teachers:profile')
    else:
        form = TeacherProfileForm(instance=teacher)
    return render(request, 'teachers/profile.html', {'form': form})

@login_required
def class_list(request):
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    classes = ClassSubject.objects.filter(teacher=teacher)
    return render(request, 'teachers/class_list.html', {'classes': classes})

@login_required
def class_detail(request, class_id):
    """View details of a specific class including students and subjects."""
    class_obj = get_object_or_404(Class, id=class_id)
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Get class subjects taught by this teacher
    subjects = ClassSubject.objects.filter(
        class_name=class_obj,
        teacher=teacher
    ).select_related('subject')
    
    # Get students in the class
    students = ClassStudent.objects.filter(
        class_name=class_obj
    ).select_related('student__user')
    
    context = {
        'class': class_obj,
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'teachers/class_detail.html', context)

@login_required
def take_attendance(request, class_id):
    """Take attendance for a class."""
    class_obj = get_object_or_404(Class, id=class_id)
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Get students in the class
    students = ClassStudent.objects.filter(
        class_name=class_obj
    ).select_related('student__user')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'status_{student.student.id}')
            notes = request.POST.get(f'notes_{student.student.id}', '')
            
            Attendance.objects.update_or_create(
                student=student.student,
                date=date,
                defaults={
                    'status': status,
                    'notes': notes
                }
            )
        
        messages.success(request, 'Attendance recorded successfully!')
        return redirect('teachers:class_detail', class_id=class_id)
    
    context = {
        'class': class_obj,
        'students': students,
        'date': timezone.now().date(),
    }
    return render(request, 'teachers/take_attendance.html', context)

@login_required
def grade_students(request, class_id, subject_id):
    """Grade students for a specific subject."""
    class_obj = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Verify teacher teaches this subject in this class
    class_subject = get_object_or_404(ClassSubject, 
        class_name=class_obj,
        subject=subject,
        teacher=teacher
    )
    
    # Get students in the class
    students = ClassStudent.objects.filter(
        class_name=class_obj
    ).select_related('student__user')
    
    if request.method == 'POST':
        term = request.POST.get('term')
        for student in students:
            score = request.POST.get(f'score_{student.student.id}')
            notes = request.POST.get(f'notes_{student.student.id}', '')
            
            if score:
                Grade.objects.update_or_create(
                    student=student.student,
                    subject=subject,
                    term=term,
                    defaults={
                        'score': score,
                        'teacher_notes': notes
                    }
                )
        
        messages.success(request, 'Grades recorded successfully!')
        return redirect('teachers:class_detail', class_id=class_id)
    
    context = {
        'class': class_obj,
        'subject': subject,
        'students': students,
        'terms': [('first', 'First Term'), ('second', 'Second Term'), ('third', 'Third Term')],
    }
    return render(request, 'teachers/grade_students.html', context)

@login_required
def create_assignment(request, class_id, subject_id):
    """Create a new assignment for a class."""
    class_obj = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Verify teacher teaches this subject in this class
    class_subject = get_object_or_404(ClassSubject, 
        class_name=class_obj,
        subject=subject,
        teacher=teacher
    )
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        
        Assignment.objects.create(
            title=title,
            description=description,
            class_subject=class_subject,
            due_date=due_date
        )
        
        messages.success(request, 'Assignment created successfully!')
        return redirect('teachers:class_detail', class_id=class_id)
    
    context = {
        'class': class_obj,
        'subject': subject,
    }
    return render(request, 'teachers/create_assignment.html', context)

@login_required
def grade_submissions(request, assignment_id):
    """Grade student submissions for an assignment."""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    
    # Verify teacher owns this assignment
    if assignment.class_subject.teacher != teacher:
        messages.error(request, 'You do not have permission to grade this assignment.')
        return redirect('teachers:dashboard')
    
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related('student__user')
    
    if request.method == 'POST':
        for submission in submissions:
            grade = request.POST.get(f'grade_{submission.id}')
            feedback = request.POST.get(f'feedback_{submission.id}', '')
            
            if grade:
                submission.grade = grade
                submission.feedback = feedback
                submission.save()
        
        messages.success(request, 'Grades and feedback recorded successfully!')
        return redirect('teachers:class_detail', class_id=assignment.class_subject.class_name.id)
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'teachers/grade_submissions.html', context)

@login_required
@require_POST
def grade_submission(request, submission_pk):
    submission = get_object_or_404(AssignmentSubmission, pk=submission_pk)
    if submission.assignment.class_subject.teacher.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    grade = request.POST.get('grade')
    feedback = request.POST.get('feedback')
    
    if grade:
        submission.grade = grade
    if feedback:
        submission.feedback = feedback
    
    submission.save()
    return JsonResponse({'status': 'success'})

@login_required
def attendance_list(request, class_subject_pk):
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk, teacher__user=request.user)
    students = ClassStudent.objects.filter(class_name=class_subject.class_name)
    return render(request, 'teachers/attendance_list.html', {
        'class_subject': class_subject,
        'students': students
    })

@login_required
@require_POST
def mark_attendance(request):
    if request.method == 'POST':
        class_subject_id = request.POST.get('class_subject')
        date = request.POST.get('date')
        
        try:
            schedule = Schedule.objects.get(id=class_subject_id, teacher=request.user)
            class_group = schedule.class_group
            
            # Get all students in the class
            students = class_group.students.all()
            
            # Process attendance for each student
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                notes = request.POST.get(f'notes_{student.id}', '')
                
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date,
                        defaults={
                            'status': status,
                            'notes': notes,
                            'subject': schedule.subject
                        }
                    )
            
            messages.success(request, 'Attendance marked successfully!')
            return redirect('teachers:mark_attendance')
            
        except Schedule.DoesNotExist:
            messages.error(request, 'Invalid class schedule.')
            return redirect('teachers:mark_attendance')
    
    # Get today's classes for the teacher
    today = timezone.now().date()
    today_schedule = Schedule.objects.filter(
        teacher=request.user,
        day_of_week=today.strftime('%A').lower()
    ).select_related('class_group', 'subject')
    
    context = {
        'today_schedule': today_schedule,
        'today': today,
    }
    return render(request, 'teachers/mark_attendance.html', context)

@login_required
def grade_assignments(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submission_id = data.get('submission_id')
            grade = data.get('grade')
            feedback = data.get('feedback', '')
            
            submission = AssignmentSubmission.objects.get(
                id=submission_id,
                assignment__class_subject__teacher=request.user
            )
            
            submission.grade = grade
            submission.feedback = feedback
            submission.save()
            
            return JsonResponse({'success': True})
            
        except AssignmentSubmission.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Submission not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get pending assignments for the teacher's classes
    pending_assignments = Assignment.objects.filter(
        class_subject__teacher=request.user,
        submissions__grade__isnull=True
    ).distinct().select_related(
        'class_subject__class_group',
        'class_subject__subject'
    ).prefetch_related(
        'submissions__student__user'
    )
    
    context = {
        'pending_assignments': pending_assignments,
    }
    return render(request, 'teachers/grade_assignments.html', context)

@login_required
def view_schedule(request):
    # Get the current week's start date from query params or default to current week
    week_start = request.GET.get('week')
    if week_start:
        week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
    else:
        week_start = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
    
    # Calculate week end date
    week_end = week_start + timedelta(days=6)
    
    # Get all days in the week
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    
    # Get the teacher's schedule for the week
    weekly_schedule = {}
    for day in week_days:
        day_name = day.strftime('%A').lower()
        day_schedule = Schedule.objects.filter(
            teacher=request.user,
            day_of_week=day_name
        ).order_by('start_time')
        weekly_schedule[day] = {schedule.start_time: schedule for schedule in day_schedule}
    
    # Get unique time slots across all days
    time_slots = sorted(set(
        time for day in weekly_schedule.values() 
        for time in day.keys()
    ))
    
    # Calculate previous and next week dates
    previous_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    context = {
        'week_start': week_start,
        'week_end': week_end,
        'week_days': week_days,
        'weekly_schedule': weekly_schedule,
        'time_slots': time_slots,
        'previous_week': previous_week,
        'next_week': next_week,
    }
    return render(request, 'teachers/view_schedule.html', context)

@login_required
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        class_groups = request.POST.getlist('class_groups')
        
        if not title or not content or not class_groups:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('teachers:create_announcement')
        
        try:
            # Create the announcement
            announcement = Announcement.objects.create(
                title=title,
                content=content,
                created_by=request.user
            )
            
            # Add selected class groups
            announcement.class_groups.set(class_groups)
            
            messages.success(request, 'Announcement created successfully!')
            return redirect('teachers:create_announcement')
            
        except Exception as e:
            messages.error(request, f'Error creating announcement: {str(e)}')
            return redirect('teachers:create_announcement')
    
    # Get the teacher's classes
    teacher_classes = Class.objects.filter(
        subjects__teacher=request.user
    ).distinct()
    
    # Get recent announcements
    recent_announcements = Announcement.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'teacher_classes': teacher_classes,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'teachers/create_announcement.html', context)
