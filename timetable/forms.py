from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import TimeSlot, TeacherAvailability, ClassSchedule

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        day_of_week = cleaned_data.get('day_of_week')

        if start_time and end_time and end_time <= start_time:
            raise ValidationError(_('End time must be after start time'))

        # Check for overlapping time slots on the same day
        if start_time and end_time and day_of_week is not None:
            overlapping = TimeSlot.objects.filter(
                day_of_week=day_of_week
            ).filter(
                (models.Q(start_time__lt=end_time) & models.Q(end_time__gt=start_time))
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise ValidationError(_('This time slot overlaps with an existing one'))

        return cleaned_data

class TeacherAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TeacherAvailability
        fields = ['time_slot', 'is_available', 'reason']
        widgets = {
            'reason': forms.TextInput(attrs={'placeholder': 'Reason for unavailability'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_slot'].queryset = TimeSlot.objects.all().order_by('day_of_week', 'start_time')
        self.fields['reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_available = cleaned_data.get('is_available')
        reason = cleaned_data.get('reason')

        if not is_available and not reason:
            self.add_error('reason', _('Please provide a reason for unavailability'))

        return cleaned_data

class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['class_group', 'subject', 'teacher', 'time_slot', 'room', 'is_recurring']
        widgets = {
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, current_term=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_term = current_term
        
        # Filter teachers to only those in the Teachers group
        self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(
            groups__name='Teachers'
        ).order_by('last_name', 'first_name')
        
        # Order time slots by day and time
        self.fields['time_slot'].queryset = TimeSlot.objects.all().order_by(
            'day_of_week', 'start_time'
        )

    def clean(self):
        cleaned_data = super().clean()
        time_slot = cleaned_data.get('time_slot')
        teacher = cleaned_data.get('teacher')
        room = cleaned_data.get('room')
        class_group = cleaned_data.get('class_group')

        if all([time_slot, teacher, room, class_group, self.current_term]):
            # Check teacher availability
            if not TeacherAvailability.objects.filter(
                teacher=teacher,
                time_slot=time_slot,
                is_available=True
            ).exists():
                raise ValidationError(_('Teacher is not available during this time slot'))

            # Check for scheduling conflicts
            existing = ClassSchedule.objects.filter(
                term=self.current_term,
                time_slot=time_slot
            ).filter(
                models.Q(teacher=teacher) |
                models.Q(room=room) |
                models.Q(class_group=class_group)
            )
            
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                conflicts = []
                for schedule in existing:
                    if schedule.teacher == teacher:
                        conflicts.append(_('Teacher is already scheduled for another class'))
                    if schedule.room == room:
                        conflicts.append(_('Room is already booked'))
                    if schedule.class_group == class_group:
                        conflicts.append(_('Class group already has a subject scheduled'))
                raise ValidationError(conflicts)

        return cleaned_data 