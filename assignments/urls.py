from django.urls import path
from . import views

app_name = "assignments"

urlpatterns = [
    path("", views.assignment_list, name="list"),
    path("<int:assignment_id>/", views.assignment_detail, name="detail"),
    path("<int:assignment_id>/submit/", views.submit_assignment, name="submit"),
    path(
        "submission/<int:submission_id>/grade/",
        views.grade_submission,
        name="grade_submission",
    ),
]
