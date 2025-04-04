# blockchain/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.blockchain_dashboard, name='blockchain_dashboard'),
]