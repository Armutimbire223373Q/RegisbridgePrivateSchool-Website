from django.urls import path
from . import views

urlpatterns = [
    path("classes/", views.class_list, name="timetable_classes"),
    path("class/<int:classroom_id>/", views.class_timetable, name="class_timetable"),
]
