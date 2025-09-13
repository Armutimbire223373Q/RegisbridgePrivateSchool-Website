from django.urls import path
from . import views

app_name = "parents"

urlpatterns = [
    path("children/", views.children_list, name="children_list"),
    path("child/<int:student_id>/", views.child_detail, name="child_detail"),
    path(
        "child/<int:student_id>/attendance/",
        views.child_attendance,
        name="child_attendance",
    ),
    path("child/<int:student_id>/grades/", views.child_grades, name="child_grades"),
]
