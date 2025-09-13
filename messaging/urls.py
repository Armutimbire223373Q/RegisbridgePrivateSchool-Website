from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("compose/", views.compose, name="compose"),
    path("thread/<int:thread_id>/", views.thread_view, name="thread_view"),
]
