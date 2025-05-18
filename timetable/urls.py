from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    # Schedule views
    path('', views.schedule_view, name='schedule'),
    path('class-schedules/', views.ClassScheduleListView.as_view(), name='class_schedule_list'),
    path('class-schedules/create/', views.ClassScheduleCreateView.as_view(), name='class_schedule_create'),
    
    # Time slot management
    path('timeslots/', views.TimeSlotListView.as_view(), name='timeslot_list'),
    path('timeslots/create/', views.TimeSlotCreateView.as_view(), name='timeslot_create'),
    
    # Teacher availability
    path('availability/', views.teacher_availability, name='teacher_availability'),
    
    # AJAX endpoints
    path('ajax/check-conflicts/', views.ajax_check_conflicts, name='ajax_check_conflicts'),
] 