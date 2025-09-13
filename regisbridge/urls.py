"""
URL configuration for regisbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Admin branding
admin.site.site_header = "Regisbridge Administration"
admin.site.site_title = "Regisbridge Admin"
admin.site.index_title = "Welcome to Regisbridge Admin Portal"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("public.urls", "public"), namespace="public")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("teachers/", include(("teachers.urls", "teachers"), namespace="teachers")),
    path("students/", include(("students.urls", "students"), namespace="students")),
    path("parents/", include(("parents.urls", "parents"), namespace="parents")),
    path("assignments/", include(("assignments.urls", "assignments"), namespace="assignments")),
    path("grades/", include(("grades.urls", "grades"), namespace="grades")),
    path("api/", include("core_api.urls")),
    path("attendance/", include(("core_attendance.urls", "core_attendance"), namespace="core_attendance")),
    path("timetable/", include(("core_timetable.urls", "core_timetable"), namespace="core_timetable")),
    path("fees/", include(("fees.urls", "fees"), namespace="fees")),
    path("messaging/", include(("messaging.urls", "messaging"), namespace="messaging")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("inventory/", include(("core_inventory.urls", "core_inventory"), namespace="core_inventory")),
    path("boarding/", include(("boarding.urls", "boarding"), namespace="boarding")),
    path("reports/", include(("reports.urls", "reports"), namespace="reports")),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
