"""
URL configuration for regisbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
from blog.sitemaps import PostSitemap, CategorySitemap

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
}

# URLs that don't need to be translated
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# URLs that should be translated
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('homepage.urls', namespace='homepage')),
    path('main/', include('main.urls', namespace='main')),
    path('admissions/', include('admissions.urls')),
    path('blog/', include('blog.urls')),
    path('school/', include('school.urls', namespace='school')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
