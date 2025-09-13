from collections import defaultdict

from django.shortcuts import render, get_object_or_404

from students.models import ClassRoom
from .models import Lesson, TimeSlot


def class_list(request):
    classes = ClassRoom.objects.select_related("grade_level").order_by(
        "grade_level__name", "name"
    )
    return render(request, "timetable/class_list.html", {"classes": classes})


def class_timetable(request, classroom_id: int):
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    lessons = (
        Lesson.objects.filter(classroom=classroom)
        .select_related("subject", "teacher__user", "timeslot")
        .order_by("timeslot__weekday", "timeslot__start_time")
    )

    # Group by weekday
    grouped = defaultdict(list)
    for l in lessons:
        grouped[l.timeslot.weekday].append(l)

    weekdays = [label for _, label in TimeSlot.WEEKDAY_CHOICES]
    context = {
        "classroom": classroom,
        "grouped": grouped,
        "weekdays": weekdays,
    }
    return render(request, "timetable/class_timetable.html", context)
