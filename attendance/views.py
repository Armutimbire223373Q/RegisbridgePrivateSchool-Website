from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Attendance
from students.models import StudentProfile
from datetime import datetime, timedelta
import json

@login_required
def attendance_dashboard(request):
    today = datetime.now().date()
    students = StudentProfile.objects.all()
    attendance_records = Attendance.objects.filter(date=today)
    
    context = {
        'students': students,
        'attendance_records': attendance_records,
        'today': today
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
@require_POST
def mark_attendance(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        status = data.get('status')
        notes = data.get('notes', '')
        date = data.get('date', datetime.now().date())
        
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        student = get_object_or_404(StudentProfile, id=student_id)
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            date=date,
            defaults={
                'status': status,
                'remarks': notes
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Attendance marked successfully',
            'attendance': {
                'id': attendance.id,
                'status': attendance.status,
                'remarks': attendance.remarks
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def get_student_attendance(request, student_id):
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        student = get_object_or_404(StudentProfile, id=student_id)
        attendance_records = Attendance.objects.filter(
            student=student,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        data = [{
            'date': record.date.strftime('%Y-%m-%d'),
            'status': record.status,
            'remarks': record.remarks
        } for record in attendance_records]
        
        return JsonResponse({
            'success': True,
            'attendance_records': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400) 