from django.urls import path
from . import views

urlpatterns = [
    path('lab_dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('add_lab_report/', views.add_lab_report, name='add_lab_report'),
    path('mark_collected/', views.mark_collected, name='mark_collected'),
    path('mark_completed/', views.mark_completed, name='mark_completed'),
    path('get_lab_tests/', views.get_lab_tests, name='get_lab_tests'),
]