from django.urls import path
from . import views

urlpatterns = [
    path('patient_reports/', views.patient_reports, name='patient_reports'),
]
