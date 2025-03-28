"""
URL configuration for fyp project.
"""

from django.contrib import admin
from django.urls import path, include
from fyp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),
    path('users/', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('doctors/', include('doctors.urls')),
    path('ai_assistant/', include('ai_assistant.urls')),
    path('lab_report/', include('lab_report.urls')),
    path('medical_records/', include('medical_records.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)