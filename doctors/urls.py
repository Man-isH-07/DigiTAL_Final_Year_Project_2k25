
from django.urls import path
from .views import doctors_list, get_doctor_slots  # Import the function

urlpatterns = [
    path('', doctors_list, name='doctors_list'),
    path('get-doctor-slots/<int:doctor_id>/', get_doctor_slots, name='get_doctor_slots'),  # ✅ API for slots
]
