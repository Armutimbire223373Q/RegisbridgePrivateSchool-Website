from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("admissions/", views.admissions, name="admissions"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("academics/", views.academics, name="academics"),
    path("student-life/", views.student_life, name="student_life"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("inventory/", views.inventory, name="inventory"),
    path("boarding/", views.boarding, name="boarding"),
    # Portal entry (login required)
    path("student-portal/", views.student_portal_entry, name="student_portal_entry"),
]
