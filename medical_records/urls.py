from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.medical_records_list, name='medical_records_list'),
]