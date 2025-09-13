from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import ReportTemplate, Report, ScheduledReport, ReportAccess
from .utils import generate_report
from students.models import StudentProfile
from teachers.models import TeacherProfile
from core_attendance.models import StudentAttendance
from grades.models import Grade, Assessment
from fees.models import Invoice, Payment


@login_required
def reports_dashboard(request):
    """Main reports dashboard"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    # Get recent reports
    recent_reports = Report.objects.filter(
        generated_by=request.user
    ).order_by('-created_at')[:10]

    # Get available templates
    available_templates = ReportTemplate.objects.filter(is_active=True)

    # Get scheduled reports
    scheduled_reports = ScheduledReport.objects.filter(
        created_by=request.user,
        is_active=True
    ).order_by('next_run')

    context = {
        'recent_reports': recent_reports,
        'available_templates': available_templates,
        'scheduled_reports': scheduled_reports,
    }

    return render(request, 'reports/dashboard.html', context)


@login_required
def reports_list(request):
    """List all reports with filtering"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')

    # Filtering
    status_filter = request.GET.get('status')
    template_filter = request.GET.get('template')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if template_filter:
        reports = reports.filter(template_id=template_filter)
    if date_from:
        reports = reports.filter(created_at__date__gte=date_from)
    if date_to:
        reports = reports.filter(created_at__date__lte=date_to)

    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    templates = ReportTemplate.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'templates': templates,
        'status_filter': status_filter,
        'template_filter': template_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'reports/list.html', context)


@login_required
def generate_report_view(request, template_id):
    """Generate a new report"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    template = get_object_or_404(ReportTemplate, id=template_id, is_active=True)

    if request.method == 'POST':
        # Get parameters from form
        parameters = {}
        for key, value in request.POST.items():
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                parameters[param_name] = value

        # Create report record
        report = Report.objects.create(
            template=template,
            generated_by=request.user,
            title=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            parameters=parameters,
            status='PENDING'
        )

        # Start generation (in a real app, this would be done asynchronously)
        try:
            report.start_generation()
            file_path, file_size = generate_report(template, parameters, request.user)
            report.complete_generation(file_path, file_size)
            messages.success(request, f"Report '{report.title}' generated successfully.")
        except Exception as e:
            report.fail_generation(str(e))
            messages.error(request, f"Failed to generate report: {str(e)}")

        return redirect('reports:list')

    # Get template parameters
    template_params = template.get_parameters()
    template_filters = template.get_filters()

    context = {
        'template': template,
        'template_params': template_params,
        'template_filters': template_filters,
    }

    return render(request, 'reports/generate.html', context)


@login_required
def report_detail(request, report_id):
    """View report details and download"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    report = get_object_or_404(Report, id=report_id, generated_by=request.user)

    context = {
        'report': report,
    }

    return render(request, 'reports/detail.html', context)


@login_required
def download_report(request, report_id):
    """Download report file"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    report = get_object_or_404(Report, id=report_id, generated_by=request.user)

    if report.status != 'COMPLETED' or not report.file:
        messages.error(request, "Report not available for download.")
        return redirect('reports:detail', report_id=report_id)

    # Track download
    try:
        access = ReportAccess.objects.get(user=request.user, report=report)
        access.increment_download()
    except ReportAccess.DoesNotExist:
        ReportAccess.objects.create(
            user=request.user,
            report=report,
            granted_by=request.user
        )

    response = HttpResponse(report.file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{report.title}.{report.template.format.lower()}"'
    return response


@login_required
def student_performance_report(request):
    """Generate student performance analytics report"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    # Get filter parameters
    grade_level = request.GET.get('grade_level')
    classroom = request.GET.get('classroom')
    subject = request.GET.get('subject')
    term = request.GET.get('term')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Build queryset
    grades = Grade.objects.select_related(
        'student__user', 'assessment__subject', 'assessment__classroom'
    ).all()

    if grade_level:
        grades = grades.filter(student__grade_level_id=grade_level)
    if classroom:
        grades = grades.filter(assessment__classroom_id=classroom)
    if subject:
        grades = grades.filter(assessment__subject_id=subject)
    if term:
        grades = grades.filter(assessment__term_id=term)
    if date_from:
        grades = grades.filter(graded_at__date__gte=date_from)
    if date_to:
        grades = grades.filter(graded_at__date__lte=date_to)

    # Calculate statistics
    total_students = grades.values('student').distinct().count()
    total_assessments = grades.values('assessment').distinct().count()
    average_percentage = grades.aggregate(avg=Avg('marks_obtained'))['avg'] or 0

    # Top performers
    top_performers = grades.values(
        'student__user__first_name',
        'student__user__last_name',
        'student__admission_number'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_assessments=Count('assessment')
    ).order_by('-avg_marks')[:10]

    # Subject-wise performance
    subject_performance = grades.values(
        'assessment__subject__name'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_students=Count('student', distinct=True),
        total_assessments=Count('assessment', distinct=True)
    ).order_by('-avg_marks')

    # Grade distribution
    grade_distribution = grades.extra(
        select={
            'letter_grade': """
                CASE 
                    WHEN (marks_obtained / assessment.total_marks * 100) >= 80 THEN 'A'
                    WHEN (marks_obtained / assessment.total_marks * 100) >= 70 THEN 'B'
                    WHEN (marks_obtained / assessment.total_marks * 100) >= 60 THEN 'C'
                    WHEN (marks_obtained / assessment.total_marks * 100) >= 50 THEN 'D'
                    ELSE 'F'
                END
            """
        }
    ).values('letter_grade').annotate(count=Count('id')).order_by('letter_grade')

    context = {
        'total_students': total_students,
        'total_assessments': total_assessments,
        'average_percentage': round(average_percentage, 2),
        'top_performers': top_performers,
        'subject_performance': subject_performance,
        'grade_distribution': grade_distribution,
        'filters': {
            'grade_level': grade_level,
            'classroom': classroom,
            'subject': subject,
            'term': term,
            'date_from': date_from,
            'date_to': date_to,
        }
    }

    return render(request, 'reports/student_performance.html', context)


@login_required
def attendance_report(request):
    """Generate attendance analytics report"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    # Get filter parameters
    grade_level = request.GET.get('grade_level')
    classroom = request.GET.get('classroom')
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=30)).date().isoformat())
    date_to = request.GET.get('date_to', timezone.now().date().isoformat())

    # Build queryset
    attendance = StudentAttendance.objects.select_related(
        'student__user', 'student__grade_level', 'student__classroom'
    ).filter(
        date__gte=date_from,
        date__lte=date_to
    )

    if grade_level:
        attendance = attendance.filter(student__grade_level_id=grade_level)
    if classroom:
        attendance = attendance.filter(student__classroom_id=classroom)

    # Calculate statistics
    total_records = attendance.count()
    present_count = attendance.filter(status='PRESENT').count()
    absent_count = attendance.filter(status='ABSENT').count()
    late_count = attendance.filter(status='LATE').count()

    attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

    # Student-wise attendance
    student_attendance = attendance.values(
        'student__user__first_name',
        'student__user__last_name',
        'student__admission_number'
    ).annotate(
        present=Count('id', filter=Q(status='PRESENT')),
        absent=Count('id', filter=Q(status='ABSENT')),
        late=Count('id', filter=Q(status='LATE')),
        total=Count('id')
    ).order_by('-present')

    # Daily attendance trend
    daily_trend = attendance.values('date').annotate(
        present=Count('id', filter=Q(status='PRESENT')),
        absent=Count('id', filter=Q(status='ABSENT')),
        late=Count('id', filter=Q(status='LATE')),
        total=Count('id')
    ).order_by('date')

    context = {
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_rate': round(attendance_rate, 2),
        'student_attendance': student_attendance,
        'daily_trend': daily_trend,
        'filters': {
            'grade_level': grade_level,
            'classroom': classroom,
            'date_from': date_from,
            'date_to': date_to,
        }
    }

    return render(request, 'reports/attendance.html', context)


@login_required
def financial_report(request):
    """Generate financial analytics report"""
    if request.user.role not in ["ADMIN"]:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("dashboard")

    # Get filter parameters
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=30)).date().isoformat())
    date_to = request.GET.get('date_to', timezone.now().date().isoformat())
    payment_method = request.GET.get('payment_method')

    # Build querysets
    payments = Payment.objects.filter(
        date__gte=date_from,
        date__lte=date_to
    )

    invoices = Invoice.objects.filter(
        issue_date__gte=date_from,
        issue_date__lte=date_to
    )

    if payment_method:
        payments = payments.filter(method=payment_method)

    # Calculate statistics
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_invoices = invoices.count()
    paid_invoices = invoices.filter(status='PAID').count()
    outstanding_amount = invoices.exclude(status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Payment method breakdown
    payment_methods = payments.values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Monthly revenue trend
    monthly_revenue = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=i * 30)
        month_end = month_start + timedelta(days=30)
        revenue = payments.filter(
            date__gte=month_start,
            date__lt=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_revenue.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': revenue
        })

    context = {
        'total_revenue': total_revenue,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'outstanding_amount': outstanding_amount,
        'payment_methods': payment_methods,
        'monthly_revenue': reversed(monthly_revenue),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'payment_method': payment_method,
        }
    }

    return render(request, 'reports/financial.html', context)


@login_required
def scheduled_reports(request):
    """Manage scheduled reports"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    scheduled_reports = ScheduledReport.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    context = {
        'scheduled_reports': scheduled_reports,
    }

    return render(request, 'reports/scheduled.html', context)


@login_required
def create_scheduled_report(request):
    """Create a new scheduled report"""
    if request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied. Admin or Teacher privileges required.")
        return redirect("dashboard")

    if request.method == 'POST':
        template_id = request.POST.get('template')
        name = request.POST.get('name')
        frequency = request.POST.get('frequency')
        start_date = request.POST.get('start_date')
        recipients = request.POST.getlist('recipients')

        template = get_object_or_404(ReportTemplate, id=template_id)

        scheduled_report = ScheduledReport.objects.create(
            name=name,
            template=template,
            created_by=request.user,
            frequency=frequency,
            start_date=start_date,
            next_run=timezone.now() + timedelta(days=1)
        )

        # Add recipients
        for recipient_id in recipients:
            scheduled_report.recipients.add(recipient_id)

        messages.success(request, f"Scheduled report '{name}' created successfully.")
        return redirect('reports:scheduled')

    templates = ReportTemplate.objects.filter(is_active=True)
    users = request.user.__class__.objects.filter(is_active=True)

    context = {
        'templates': templates,
        'users': users,
    }

    return render(request, 'reports/create_scheduled.html', context)


