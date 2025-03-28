from django.urls import path
from . import views

urlpatterns = [
    path('manual_booking/', views.manual_booking, name='manual_booking'),
    path('appointment_history/', views.appointment_history, name='appointment_history'),
    path('virtual_waiting_room/', views.virtual_waiting_room, name='virtual_waiting_room'),
    path('update_queue_status/', views.update_queue_status, name='update_queue_status'),
    path('adjust_doctor_slot/', views.adjust_doctor_slot, name='adjust_doctor_slot'),
    path('fetch_wait_times/', views.fetch_wait_times, name='fetch_wait_times'),
    path('fetch_patient_timer/', views.fetch_patient_timer, name='fetch_patient_timer'),
    path('save_patient_timer/', views.save_patient_timer, name='save_patient_timer'),
    path('live_wait_time/<int:appointment_id>/', views.live_wait_time_detail, name='live_wait_time_detail'),
    path('fetch_session_status/', views.fetch_session_status, name='fetch_session_status'),  # New endpoint
]
