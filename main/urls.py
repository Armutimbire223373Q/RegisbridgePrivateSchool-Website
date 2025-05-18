from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('academics/', views.academics, name='academics'),
    path('curriculum/', views.curriculum, name='curriculum'),
    path('student-life/', views.student_life, name='student_life'),
    path('news/', views.NewsListView.as_view(), name='news'),
    path('parents/', views.FAQListView.as_view(), name='parents'),
    path('contact/', views.contact, name='contact'),
]

# Error handlers
handler400 = 'main.views.bad_request'
handler403 = 'main.views.permission_denied'
handler404 = 'main.views.page_not_found'
handler500 = 'main.views.server_error' 