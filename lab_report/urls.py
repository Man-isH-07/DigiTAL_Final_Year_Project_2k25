from django.urls import path
from . import views

urlpatterns = [
    path('lab_dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('add_lab_report/', views.add_lab_report, name='add_lab_report'),
]