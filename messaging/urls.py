from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Message threads
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('thread/new/', views.create_thread, name='create_thread'),
    path('thread/<int:pk>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('thread/<int:thread_id>/send/', views.send_message, name='send_message'),
    path('thread/<int:pk>/archive/', views.archive_thread, name='archive_thread'),
    
    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/new/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/read/', views.mark_announcement_read, name='mark_announcement_read'),
] 