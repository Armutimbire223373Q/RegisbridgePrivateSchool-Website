from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
from io import BytesIO
from .models import (
    GradeScale, GradeLevel, AssessmentType, Assessment,
    Grade, ReportCard, SubjectGrade
)
from .forms import (
    AssessmentForm, BulkGradeForm, GradeForm,
    ReportCardGenerationForm, ReportCardApprovalForm,
    SubjectGradeForm
)

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Teachers').exists()

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'grading/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Assessment.objects.all()
        if not self.request.user.is_staff:
            if self.request.user.groups.filter(name='Teachers').exists():
                queryset = queryset.filter(
                    subject__in=self.request.user.teaching_subjects.all(),
                    class_group__in=self.request.user.teaching_classes.all()
                )
            else:  # Student
                queryset = queryset.filter(
                    class_group=self.request.user.student_profile.class_group
                )
        return queryset.select_related('subject', 'class_group', 'assessment_type')

class AssessmentCreateView(TeacherRequiredMixin, CreateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'grading/assessment_form.html'
    success_url = reverse_lazy('grading:assessment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.term = self.request.user.school.get_current_term()
        messages.success(self.request, 'Assessment created successfully.')
        return super().form_valid(form)

@login_required
def grade_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    
    # Check permissions
    if not request.user.is_staff and not request.user.groups.filter(name='Teachers').exists():
        messages.error(request, 'You do not have permission to grade assessments.')
        return redirect('grading:assessment_list')

    # Get students for this class
    students = assessment.class_group.students.all()
    
    if request.method == 'POST':
        # Process grades
        for student in students:
            score = request.POST.get(f'score_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}')
            if score:
                grade, created = Grade.objects.update_or_create(
                    student=student,
                    assessment=assessment,
                    defaults={
                        'score': score,
                        'remarks': remarks,
                        'graded_by': request.user
                    }
                )
        messages.success(request, 'Grades saved successfully.')
        return redirect('grading:assessment_list')

    # Get existing grades
    grades = {
        grade.student_id: grade 
        for grade in Grade.objects.filter(assessment=assessment)
    }

    context = {
        'assessment': assessment,
        'students': students,
        'grades': grades
    }
    return render(request, 'grading/grade_assessment.html', context)

@login_required
def student_grades(request):
    if request.user.groups.filter(name='Students').exists():
        # Student viewing their own grades
        grades = Grade.objects.filter(
            student=request.user
        ).select_related(
            'assessment', 'assessment__subject',
            'assessment__assessment_type'
        )
    elif request.user.groups.filter(name='Parents').exists():
        # Parent viewing their child's grades
        grades = Grade.objects.filter(
            student=request.user.parent_profile.child
        ).select_related(
            'assessment', 'assessment__subject',
            'assessment__assessment_type'
        )
    else:
        messages.error(request, 'Invalid access.')
        return redirect('homepage:home')

    # Group grades by subject
    subjects = {}
    for grade in grades:
        subject = grade.assessment.subject
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(grade)

    context = {
        'subjects': subjects
    }
    return render(request, 'grading/student_grades.html', context)

@login_required
def generate_report_cards(request):
    if not request.user.is_staff and not request.user.groups.filter(name='Teachers').exists():
        messages.error(request, 'You do not have permission to generate report cards.')
        return redirect('homepage:home')

    if request.method == 'POST':
        form = ReportCardGenerationForm(request.POST, school=request.user.school)
        if form.is_valid():
            term = form.cleaned_data['term']
            students = form.cleaned_data['students']
            include_attendance = form.cleaned_data['include_attendance']
            include_teacher_remarks = form.cleaned_data['include_teacher_remarks']

            for student in students:
                # Create or update report card
                report_card, created = ReportCard.objects.update_or_create(
                    student=student,
                    term=term,
                    defaults={
                        'class_group': student.student_profile.class_group,
                        'generated_by': request.user,
                        'status': 'draft'
                    }
                )

                # Calculate and update GPA
                report_card.calculate_gpa()

                # Generate PDF
                context = {
                    'report_card': report_card,
                    'student': student,
                    'term': term,
                    'include_attendance': include_attendance,
                    'include_teacher_remarks': include_teacher_remarks
                }
                html_string = render_to_string('grading/report_card_pdf.html', context)
                html = HTML(string=html_string)
                pdf_file = BytesIO()
                html.write_pdf(pdf_file)

                # Save PDF to report card
                report_card.generated_pdf.save(
                    f'report_card_{student.id}_{term.id}.pdf',
                    ContentFile(pdf_file.getvalue())
                )

            messages.success(request, 'Report cards generated successfully.')
            return redirect('grading:report_card_list')
    else:
        form = ReportCardGenerationForm(school=request.user.school)

    context = {
        'form': form
    }
    return render(request, 'grading/generate_report_cards.html', context)

class ReportCardListView(LoginRequiredMixin, ListView):
    model = ReportCard
    template_name = 'grading/report_card_list.html'
    context_object_name = 'report_cards'
    paginate_by = 20

    def get_queryset(self):
        queryset = ReportCard.objects.all()
        if self.request.user.groups.filter(name='Students').exists():
            queryset = queryset.filter(student=self.request.user)
        elif self.request.user.groups.filter(name='Parents').exists():
            queryset = queryset.filter(student=self.request.user.parent_profile.child)
        elif not self.request.user.is_staff:
            # Teachers see report cards for their students
            queryset = queryset.filter(
                class_group__in=self.request.user.teaching_classes.all()
            )
        return queryset.select_related('student', 'term', 'class_group')

@login_required
def approve_report_card(request, pk):
    report_card = get_object_or_404(ReportCard, pk=pk)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to approve report cards.')
        return redirect('grading:report_card_list')

    if request.method == 'POST':
        form = ReportCardApprovalForm(request.POST, instance=report_card)
        if form.is_valid():
            report_card = form.save(commit=False)
            if report_card.status == 'approved':
                report_card.approved_by = request.user
            elif report_card.status == 'published':
                report_card.published_at = timezone.now()
            report_card.save()
            messages.success(request, 'Report card status updated successfully.')
            return redirect('grading:report_card_list')
    else:
        form = ReportCardApprovalForm(instance=report_card)

    context = {
        'form': form,
        'report_card': report_card
    }
    return render(request, 'grading/approve_report_card.html', context)

@login_required
def download_report_card(request, pk):
    report_card = get_object_or_404(ReportCard, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and request.user != report_card.student:
        messages.error(request, 'You do not have permission to download this report card.')
        return redirect('grading:report_card_list')

    if report_card.status not in ['approved', 'published']:
        messages.error(request, 'This report card is not yet available for download.')
        return redirect('grading:report_card_list')

    # Serve the PDF file
    response = HttpResponse(report_card.generated_pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_card.generated_pdf.name}"'
    return response
