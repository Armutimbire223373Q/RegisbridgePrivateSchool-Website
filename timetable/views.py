from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import TimeSlot, TeacherAvailability, ClassSchedule, Schedule
from .forms import TimeSlotForm, TeacherAvailabilityForm, ClassScheduleForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

@login_required
def schedule_view(request):
    """View for students and teachers to see their weekly schedule"""
    if not request.user.is_authenticated:
        return redirect('homepage:home')
    current_term = request.user.school.get_current_term()
    schedule, created = Schedule.objects.get_or_create(
        user=request.user,
        term=current_term
    )
    
    if created or request.GET.get('refresh'):
        schedule_data = schedule.generate_schedule()
    else:
        schedule_data = schedule.cached_schedule
    
    context = {
        'schedule': schedule_data,
        'term': current_term,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    return render(request, 'timetable/schedule.html', context)

class TimeSlotListView(StaffRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'timetable/timeslot_list.html'
    context_object_name = 'timeslots'
    ordering = ['day_of_week', 'start_time']

class TimeSlotCreateView(StaffRequiredMixin, CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = 'timetable/timeslot_form.html'
    success_url = reverse_lazy('timetable:timeslot_list')

    def form_valid(self, form):
        messages.success(self.request, 'Time slot created successfully.')
        return super().form_valid(form)

@login_required
def teacher_availability(request):
    """View for teachers to set their availability"""
    if not request.user.groups.filter(name='Teachers').exists():
        messages.error(request, 'Only teachers can access this page.')
        return redirect('main:home')
    
    if request.method == 'POST':
        form = TeacherAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.teacher = request.user
            availability.save()
            messages.success(request, 'Availability updated successfully.')
            return redirect('timetable:teacher_availability')
    else:
        form = TeacherAvailabilityForm()
    
    availabilities = TeacherAvailability.objects.filter(teacher=request.user)
    context = {
        'form': form,
        'availabilities': availabilities
    }
    return render(request, 'timetable/teacher_availability.html', context)

class ClassScheduleListView(LoginRequiredMixin, ListView):
    model = ClassSchedule
    template_name = 'timetable/class_schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        current_term = self.request.user.school.get_current_term()
        if self.request.user.is_staff:
            return ClassSchedule.objects.filter(term=current_term)
        elif self.request.user.groups.filter(name='Teachers').exists():
            return ClassSchedule.objects.filter(teacher=self.request.user, term=current_term)
        else:  # Student
            return ClassSchedule.objects.filter(
                class_group=self.request.user.student_profile.class_group,
                term=current_term
            )

class ClassScheduleCreateView(StaffRequiredMixin, CreateView):
    model = ClassSchedule
    form_class = ClassScheduleForm
    template_name = 'timetable/class_schedule_form.html'
    success_url = reverse_lazy('timetable:class_schedule_list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_term'] = self.request.user.school.get_current_term()
        return kwargs

@login_required
def ajax_check_conflicts(request):
    """AJAX endpoint to check for scheduling conflicts"""
    time_slot_id = request.GET.get('time_slot')
    teacher_id = request.GET.get('teacher')
    room_id = request.GET.get('room')
    class_group_id = request.GET.get('class_group')
    current_term = request.user.school.get_current_term()

    conflicts = []
    if all([time_slot_id, teacher_id, room_id, class_group_id]):
        # Check teacher availability
        if not TeacherAvailability.objects.filter(
            teacher_id=teacher_id,
            time_slot_id=time_slot_id,
            is_available=True
        ).exists():
            conflicts.append('Teacher is not available during this time slot')

        # Check existing schedules
        existing = ClassSchedule.objects.filter(
            term=current_term,
            time_slot_id=time_slot_id
        ).filter(
            Q(teacher_id=teacher_id) |
            Q(room_id=room_id) |
            Q(class_group_id=class_group_id)
        )
        
        if existing.exists():
            conflicts.append('There is a scheduling conflict with an existing class')

    return JsonResponse({'conflicts': conflicts})
