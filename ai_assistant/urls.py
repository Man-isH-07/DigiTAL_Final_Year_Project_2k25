from django.urls import path
from .views import ai_assistant, analyze_symptoms, book_appointment_api

urlpatterns = [
    path('', ai_assistant, name='ai_assistant'),
    path('analyze_symptoms/', analyze_symptoms, name='analyze_symptoms'),
    path('book_appointment/', book_appointment_api, name='book_appointment_api'),
]