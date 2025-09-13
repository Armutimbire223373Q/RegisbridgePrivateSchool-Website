from django.urls import path
from . import views

app_name = "boarding"

urlpatterns = [
    path("", views.boarding_dashboard, name="dashboard"),
    path("dormitories/", views.dormitories_list, name="dormitories"),
    path("dormitories/<int:dormitory_id>/", views.dormitory_detail, name="dormitory_detail"),
    path("boarders/", views.boarders_list, name="boarders"),
    path("boarders/<int:boarder_id>/", views.boarder_detail, name="boarder_detail"),
    path("boarders/<int:boarder_id>/assign-bed/", views.assign_bed, name="assign_bed"),
    path("meals/", views.meal_records, name="meal_records"),
    path("meals/record/", views.record_meal, name="record_meal"),
    path("wellbeing/", views.wellbeing_checks, name="wellbeing_checks"),
    path("wellbeing/add/", views.add_wellbeing_check, name="add_wellbeing_check"),
]


