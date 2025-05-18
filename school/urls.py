from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'school'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main:home'), name='logout'),
    
    # Academic Section
    path('student-portal/', views.StudentParentPortalView.as_view(), name='student_portal'),
    path('teacher-portal/', views.TeacherPortalView.as_view(), name='teacher_portal'),
    
    # Administrative Section
    path('admin-portal/', views.AdminPortalView.as_view(), name='admin_portal'),
    path('accounting/', views.AccountingView.as_view(), name='accounting'),
    path('boarding/', views.BoardingView.as_view(), name='boarding'),
    path('hr/', views.HRView.as_view(), name='hr'),
    path('inventory/', views.InventoryView.as_view(), name='inventory'),
    
    # Staff Section
    path('accountant/', views.AccountantView.as_view(), name='accountant'),
    path('library/', views.LibraryView.as_view(), name='library'),
    path('health/', views.HealthCenterView.as_view(), name='health'),
    path('boarding-staff/', views.BoardingStaffView.as_view(), name='boarding_staff'),
    
    # Profile and Authentication
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Academic Portal Sections
    # path('academic-portal/students/', views.StudentSectionView.as_view(), name='student_section'),
    # path('academic-portal/parents/', views.ParentSectionView.as_view(), name='parent_section'),
    # path('academic-portal/teachers/', views.TeacherSectionView.as_view(), name='teacher_section'),
    
    # Administrative Portal Sections
    # path('admin-portal/accounting/', views.AccountingSectionView.as_view(), name='accounting'),
    # path('admin-portal/boarding/', views.BoardingSectionView.as_view(), name='boarding'),
    # path('admin-portal/hr/', views.HRSectionView.as_view(), name='hr'),
    # path('admin-portal/inventory/', views.InventorySectionView.as_view(), name='inventory'),
    
    # Staff Portal Sections
    # path('staff-portal/accountant/', views.AccountantSectionView.as_view(), name='accountant'),
    # path('staff-portal/librarian/', views.LibrarianSectionView.as_view(), name='librarian'),
    # path('staff-portal/nurse/', views.NurseSectionView.as_view(), name='nurse'),
    # path('staff-portal/boarding-staff/', views.BoardingStaffSectionView.as_view(), name='boarding_staff'),

    # HR Management URLs
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/employee/create/', views.employee_create, name='employee_create'),
    path('hr/employee/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('hr/leave/create/', views.leave_request_create, name='leave_request_create'),
    path('hr/leave/<int:pk>/action/', views.leave_request_action, name='leave_request_action'),
    path('hr/review/create/', views.performance_review_create, name='performance_review_create'),
    path('hr/training/create/', views.training_program_create, name='training_program_create'),
    path('hr/training/<int:pk>/enroll/', views.training_program_enroll, name='training_program_enroll'),

    # Employee Profile URLs
    path('employee/<int:employee_id>/profile/', views.employee_profile, name='employee_profile'),
    path('employee/<int:employee_id>/document/upload/', views.employee_document_upload, name='employee_document_upload'),
    path('employee/<int:employee_id>/document/<int:document_id>/delete/', views.employee_document_delete, name='employee_document_delete'),

    # Employee Management URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),
    
    # Document Management URLs
    path('employees/<int:employee_pk>/documents/add/', 
         views.EmployeeDocumentCreateView.as_view(), name='document-create'),
    path('documents/<int:pk>/delete/',
         views.EmployeeDocumentDeleteView.as_view(), name='document-delete'),
    
    # Leave Request URLs
    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave-request-list'),
    path('leave-requests/add/', views.LeaveRequestCreateView.as_view(), name='leave-request-create'),
    path('leave-requests/<int:pk>/edit/',
         views.LeaveRequestUpdateView.as_view(), name='leave-request-update'),
    
    # Performance Review URLs
    path('performance-reviews/',
         views.PerformanceReviewListView.as_view(), name='performance-review-list'),
    path('performance-reviews/add/',
         views.PerformanceReviewCreateView.as_view(), name='performance-review-create'),
]