from django.urls import path
from . import views

urlpatterns = [
    path('cashier_dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('add_pharmacy_bill/', views.add_pharmacy_bill, name='add_pharmacy_bill'),
]