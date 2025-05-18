from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import (
    LeadershipMember, TuitionFee, Scholarship, ImportantDate,
    HostelFacility, StudentService, ParentResource, PaymentMethod,
    PrivacyPolicy, Employee, LeaveRequest, PerformanceReview, TrainingProgram,
    EmployeeDocument, Department
)
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .forms import EmployeeForm, EmployeeDocumentForm, LeaveRequestForm, PerformanceReviewForm, TrainingProgramForm
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

# Custom Mixins
class RoleRequiredMixin(UserPassesTestMixin):
    role_required = None

    def test_func(self):
        return self.request.user.groups.filter(name=self.role_required).exists()

class LeadershipTeamView(ListView):
    model = LeadershipMember
    template_name = 'school/leadership.html'
    context_object_name = 'members'
    
    def get_queryset(self):
        return LeadershipMember.objects.filter(is_active=True)

class TuitionFeesView(ListView):
    model = TuitionFee
    template_name = 'school/tuition.html'
    context_object_name = 'fees'
    
    def get_queryset(self):
        return TuitionFee.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scholarships'] = Scholarship.objects.filter(is_active=True)
        return context

class ImportantDatesView(ListView):
    model = ImportantDate
    template_name = 'school/important_dates.html'
    context_object_name = 'dates'
    
    def get_queryset(self):
        return ImportantDate.objects.filter(is_active=True)

class StudentLifeView(ListView):
    model = HostelFacility
    template_name = 'school/student_life.html'
    context_object_name = 'facilities'
    
    def get_queryset(self):
        return HostelFacility.objects.filter(is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = StudentService.objects.filter(is_active=True)
        return context

class ParentsCornerView(ListView):
    model = ParentResource
    template_name = 'school/parents_corner.html'
    context_object_name = 'resources'
    
    def get_queryset(self):
        return ParentResource.objects.filter(is_active=True)

class PaymentView(ListView):
    model = PaymentMethod
    template_name = 'school/payment.html'
    context_object_name = 'methods'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)

class PrivacyPolicyView(DetailView):
    model = PrivacyPolicy
    template_name = 'school/privacy_policy.html'
    
    def get_object(self):
        return PrivacyPolicy.objects.first()

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user group
            if user.groups.filter(name='Students').exists() or user.groups.filter(name='Parents').exists():
                return redirect('school:student_section')
            elif user.groups.filter(name='Teachers').exists():
                return redirect('school:teacher_section')
            elif user.groups.filter(name='Accountants').exists():
                return redirect('school:accountant')
            elif user.groups.filter(name='Admin').exists():
                return redirect('school:admin_portal')
            else:
                return redirect('school:staff_portal')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'school/login.html')

# Main Portal Views
class AcademicPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/portals/academic_portal.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Students', 'Parents', 'Teachers']).exists()

class AdminPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/portals/admin_portal.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

class StaffPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/portals/staff_portal.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Accountants', 'Librarians', 'Nurses', 'BoardingStaff']).exists()

# Academic Section Views
class StudentParentPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/academic/student_section.html'
    
    def test_func(self):
        return self.request.user.is_student or self.request.user.is_parent

class TeacherPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/academic/teacher_section.html'
    
    def test_func(self):
        return self.request.user.is_teacher

# Administrative Section Views
class AdminPortalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class AccountingView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/admin/accounting.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class BoardingView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/admin/boarding.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class HRView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/admin/hr.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class InventoryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/admin/inventory.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

# Staff Section Views
class AccountantView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/staff/accountant.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name='accountant').exists()

class LibraryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/staff/library.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name='librarian').exists()

class HealthCenterView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/staff/health.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name='nurse').exists()

class BoardingStaffView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'school/sections/staff/boarding_staff.html'
    
    def test_func(self):
        return self.request.user.groups.filter(name='boarding_staff').exists()

@login_required
@permission_required('school.view_employee')
def hr_dashboard(request):
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='ACTIVE').count()
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    upcoming_reviews = PerformanceReview.objects.filter(
        review_date__gte=timezone.now().date()
    ).count()

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'pending_leaves': pending_leaves,
        'upcoming_reviews': upcoming_reviews,
        'recent_employees': Employee.objects.order_by('-date_joined')[:5],
        'leave_requests': LeaveRequest.objects.filter(status='PENDING')[:5],
        'upcoming_reviews_list': PerformanceReview.objects.filter(
            review_date__gte=timezone.now().date()
        ).order_by('review_date')[:5],
        'training_programs': TrainingProgram.objects.filter(
            end_date__gte=timezone.now().date()
        )[:5]
    }
    return render(request, 'school/sections/admin/hr.html', context)

@login_required
@permission_required('school.add_employee')
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, 'Employee created successfully.')
            return JsonResponse({'status': 'success', 'message': 'Employee created successfully'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@permission_required('school.change_employee')
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@permission_required('school.add_leaverequest')
def leave_request_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user.employee
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully.')
            return JsonResponse({'status': 'success', 'message': 'Leave request submitted successfully'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@permission_required('school.change_leaverequest')
def leave_request_action(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    action = request.POST.get('action')
    
    if action not in ['approve', 'reject']:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'})
    
    leave_request.status = 'APPROVED' if action == 'approve' else 'REJECTED'
    leave_request.approved_by = request.user
    leave_request.approved_on = timezone.now()
    leave_request.save()
    
    return JsonResponse({
        'status': 'success',
        'message': f'Leave request {leave_request.status.lower()} successfully'
    })

@login_required
@permission_required('school.add_performancereview')
def performance_review_create(request):
    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Performance review submitted successfully.')
            return JsonResponse({'status': 'success', 'message': 'Performance review submitted successfully'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@permission_required('school.add_trainingprogram')
def training_program_create(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, 'Training program created successfully.')
            return JsonResponse({'status': 'success', 'message': 'Training program created successfully'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def training_program_enroll(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    
    if program.is_full:
        return JsonResponse({'status': 'error', 'message': 'Program is already full'})
    
    program.participants.add(request.user.employee)
    return JsonResponse({
        'status': 'success',
        'message': 'Enrolled in training program successfully'
    })

@login_required
def employee_profile(request, employee_id):
    """View for displaying employee profile and related information."""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Check if the user has permission to view this profile
    if not request.user.is_staff and request.user != employee.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    context = {
        'employee': employee,
        'documents': EmployeeDocument.objects.filter(employee=employee).order_by('-uploaded_at'),
        'leave_requests': LeaveRequest.objects.filter(employee=employee).order_by('-start_date')[:5],
        'performance_reviews': PerformanceReview.objects.filter(employee=employee).order_by('-review_date')[:5],
    }
    
    return render(request, 'school/sections/admin/employee_profile.html', context)

@login_required
@require_http_methods(['POST'])
def employee_document_upload(request, employee_id):
    """View for handling document uploads for employees."""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Check if the user has permission to upload documents
    if not request.user.is_staff and request.user != employee.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        document = EmployeeDocument.objects.create(
            employee=employee,
            name=request.POST.get('name'),
            document_type=request.POST.get('document_type'),
            file=request.FILES.get('file')
        )
        return JsonResponse({
            'success': True,
            'document': {
                'id': document.id,
                'name': document.name,
                'document_type': document.document_type,
                'uploaded_at': document.uploaded_at.strftime('%b %d, %Y'),
                'file_url': document.file.url
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(['DELETE'])
def employee_document_delete(request, employee_id, document_id):
    """View for handling document deletion."""
    document = get_object_or_404(EmployeeDocument, id=document_id, employee_id=employee_id)
    
    # Check if the user has permission to delete documents
    if not request.user.is_staff and request.user != document.employee.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        document.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Employee Views
class EmployeeListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Employee
    template_name = 'school/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.GET.get('department')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if department:
            queryset = queryset.filter(department__name=department)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['statuses'] = Employee.EMPLOYMENT_STATUS
        return context

class EmployeeDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = Employee
    template_name = 'school/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        context['documents'] = employee.documents.all()
        context['leave_requests'] = employee.leave_requests.all()[:5]
        context['performance_reviews'] = employee.performance_reviews.all()[:5]
        return context

class EmployeeCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Employee
    template_name = 'school/employee_form.html'
    fields = ['department', 'employee_id', 'designation', 'date_joined', 'status',
              'contact_number', 'emergency_contact', 'address', 'salary']
    success_url = reverse_lazy('school:employee-list')

    def form_valid(self, form):
        messages.success(self.request, 'Employee created successfully.')
        return super().form_valid(form)

class EmployeeUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Employee
    template_name = 'school/employee_form.html'
    fields = ['department', 'designation', 'status', 'contact_number',
              'emergency_contact', 'address', 'salary']
    
    def get_success_url(self):
        return reverse_lazy('school:employee-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully.')
        return super().form_valid(form)

class EmployeeDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Employee
    template_name = 'school/employee_confirm_delete.html'
    success_url = reverse_lazy('school:employee-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Employee deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Document Views
class EmployeeDocumentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = EmployeeDocument
    template_name = 'school/document_form.html'
    fields = ['document_type', 'title', 'file', 'notes']

    def form_valid(self, form):
        form.instance.employee = get_object_or_404(Employee, pk=self.kwargs['employee_pk'])
        messages.success(self.request, 'Document uploaded successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('school:employee-detail', kwargs={'pk': self.kwargs['employee_pk']})

class EmployeeDocumentDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = EmployeeDocument
    template_name = 'school/document_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('school:employee-detail', kwargs={'pk': self.object.employee.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Leave Request Views
class LeaveRequestListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'school/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.groups.filter(name='Staff').exists():
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee__user=self.request.user)

class LeaveRequestCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = LeaveRequest
    template_name = 'school/leave_request_form.html'
    fields = ['leave_type', 'start_date', 'end_date', 'reason']
    success_url = reverse_lazy('school:leave-request-list')

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        messages.success(self.request, 'Leave request submitted successfully.')
        return super().form_valid(form)

class LeaveRequestUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = LeaveRequest
    template_name = 'school/leave_request_form.html'
    fields = ['status']
    success_url = reverse_lazy('school:leave-request-list')

    def form_valid(self, form):
        form.instance.approved_by = self.request.user
        messages.success(self.request, 'Leave request updated successfully.')
        return super().form_valid(form)

# Performance Review Views
class PerformanceReviewListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = PerformanceReview
    template_name = 'school/performance_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.groups.filter(name='Staff').exists():
            return PerformanceReview.objects.all()
        return PerformanceReview.objects.filter(employee__user=self.request.user)

class PerformanceReviewCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PerformanceReview
    template_name = 'school/performance_review_form.html'
    fields = ['employee', 'review_date', 'performance_score', 'strengths',
              'areas_for_improvement', 'goals', 'comments']
    success_url = reverse_lazy('school:performance-review-list')

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        messages.success(self.request, 'Performance review created successfully.')
        return super().form_valid(form)

# Profile View
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'school/profile.html' 