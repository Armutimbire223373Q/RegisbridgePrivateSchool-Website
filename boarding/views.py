from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Dormitory, Bed, BoardingStudent, MealPlan, MealRecord, WellBeingCheck
from students.models import StudentProfile


@login_required
def boarding_dashboard(request):
    """Main boarding dashboard with overview statistics"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    # Get boarding statistics
    total_boarders = BoardingStudent.objects.filter(status="BOARDER").count()
    total_dormitories = Dormitory.objects.count()
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    
    # Recent meal records
    recent_meals = MealRecord.objects.select_related('student__user').order_by('-date')[:10]
    
    # Recent wellbeing checks
    recent_checks = WellBeingCheck.objects.select_related('student__user').order_by('-date')[:10]
    
    # Dormitory occupancy
    dormitories = Dormitory.objects.annotate(
        occupied_count=Count('beds', filter=Q(beds__is_occupied=True))
    ).order_by('name')
    
    context = {
        'total_boarders': total_boarders,
        'total_dormitories': total_dormitories,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'recent_meals': recent_meals,
        'recent_checks': recent_checks,
        'dormitories': dormitories,
    }
    
    return render(request, 'boarding/dashboard.html', context)


@login_required
def dormitories_list(request):
    """List all dormitories with occupancy information"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    dormitories = Dormitory.objects.annotate(
        occupied_count=Count('beds', filter=Q(beds__is_occupied=True))
    ).order_by('name')
    
    context = {
        'dormitories': dormitories,
    }
    
    return render(request, 'boarding/dormitories.html', context)


@login_required
def dormitory_detail(request, dormitory_id):
    """Detailed view of a dormitory with beds and occupants"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    dormitory = get_object_or_404(Dormitory, id=dormitory_id)
    beds = Bed.objects.filter(dormitory=dormitory).order_by('number')
    
    # Get current occupants
    occupants = BoardingStudent.objects.filter(
        dormitory=dormitory,
        status="BOARDER"
    ).select_related('student__user', 'bed')
    
    context = {
        'dormitory': dormitory,
        'beds': beds,
        'occupants': occupants,
    }
    
    return render(request, 'boarding/dormitory_detail.html', context)


@login_required
def boarders_list(request):
    """List all boarding students with their status"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    boarders = BoardingStudent.objects.select_related(
        'student__user', 'dormitory', 'bed'
    ).order_by('student__user__last_name', 'student__user__first_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        boarders = boarders.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__admission_number__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        boarders = boarders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(boarders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'boarding/boarders.html', context)


@login_required
def boarder_detail(request, boarder_id):
    """Detailed view of a boarding student"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    boarder = get_object_or_404(BoardingStudent, id=boarder_id)
    
    # Get recent meal records
    recent_meals = MealRecord.objects.filter(
        student=boarder.student
    ).order_by('-date')[:20]
    
    # Get wellbeing checks
    wellbeing_checks = WellBeingCheck.objects.filter(
        student=boarder.student
    ).order_by('-date')[:10]
    
    context = {
        'boarder': boarder,
        'recent_meals': recent_meals,
        'wellbeing_checks': wellbeing_checks,
    }
    
    return render(request, 'boarding/boarder_detail.html', context)


@login_required
@require_http_methods(["POST"])
def assign_bed(request, boarder_id):
    """Assign a bed to a boarding student"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        return JsonResponse({'error': 'Access denied'}, status=403)

    boarder = get_object_or_404(BoardingStudent, id=boarder_id)
    bed_id = request.POST.get('bed_id')
    
    try:
        bed = get_object_or_404(Bed, id=bed_id)
        
        # Check if bed is available
        if bed.is_occupied:
            return JsonResponse({'error': 'Bed is already occupied'}, status=400)
        
        # Unassign current bed if any
        if boarder.bed:
            boarder.bed.is_occupied = False
            boarder.bed.save()
        
        # Assign new bed
        bed.is_occupied = True
        bed.save()
        
        boarder.bed = bed
        boarder.dormitory = bed.dormitory
        boarder.status = "BOARDER"
        boarder.save()
        
        return JsonResponse({
            'success': True,
            'bed_number': bed.number,
            'dormitory_name': bed.dormitory.name
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def meal_records(request):
    """View and manage meal attendance records"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    # Get meal records for today by default
    date_filter = request.GET.get('date', timezone.now().date().isoformat())
    
    meal_records = MealRecord.objects.filter(
        date=date_filter
    ).select_related('student__user').order_by('meal_type', 'student__user__last_name')
    
    # Group by meal type
    meal_groups = {}
    for record in meal_records:
        meal_type = record.meal_type
        if meal_type not in meal_groups:
            meal_groups[meal_type] = []
        meal_groups[meal_type].append(record)
    
    context = {
        'meal_groups': meal_groups,
        'date_filter': date_filter,
    }
    
    return render(request, 'boarding/meal_records.html', context)


@login_required
@require_http_methods(["POST"])
def record_meal(request):
    """Record meal attendance for a student"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        student_id = request.POST.get('student_id')
        date = request.POST.get('date')
        meal_type = request.POST.get('meal_type')
        taken = request.POST.get('taken') == 'true'
        
        student = get_object_or_404(StudentProfile, id=student_id)
        
        # Create or update meal record
        meal_record, created = MealRecord.objects.get_or_create(
            student=student,
            date=date,
            meal_type=meal_type,
            defaults={'taken': taken}
        )
        
        if not created:
            meal_record.taken = taken
            meal_record.save()
        
        return JsonResponse({
            'success': True,
            'created': created,
            'taken': meal_record.taken
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def wellbeing_checks(request):
    """View and manage wellbeing checks"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    checks = WellBeingCheck.objects.select_related('student__user').order_by('-date')
    
    # Pagination
    paginator = Paginator(checks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'boarding/wellbeing_checks.html', context)


@login_required
@require_http_methods(["POST"])
def add_wellbeing_check(request):
    """Add a new wellbeing check record"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        student_id = request.POST.get('student_id')
        note = request.POST.get('note')
        recorded_by = request.POST.get('recorded_by', request.user.get_full_name())
        
        student = get_object_or_404(StudentProfile, id=student_id)
        
        check = WellBeingCheck.objects.create(
            student=student,
            note=note,
            recorded_by=recorded_by
        )
        
        return JsonResponse({
            'success': True,
            'check_id': check.id,
            'date': check.date.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)