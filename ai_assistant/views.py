import spacy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from appointments.models import Appointment, Doctor
from appointments.views import send_session_notification
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import SymptomMapping

# Load the spaCy model (use en_ner_bc5cdr_md for medical NER)
nlp = spacy.load("en_ner_bc5cdr_md")

@login_required
def ai_assistant(request):
    return render(request, 'ai_assistant/ai_assistant.html')

@login_required
def analyze_symptoms(request):
    if request.method == 'GET':
        symptoms_text = request.GET.get('symptoms', '')
        if not symptoms_text:
            return JsonResponse({'error': 'Symptoms are required'}, status=400)

        # Use the medical NER model to extract symptoms
        doc = nlp(symptoms_text)
        symptoms = [ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]

        if not symptoms:
            return JsonResponse({'error': 'No recognizable symptoms found. Please describe your symptoms in more detail.'}, status=400)

        # Look up specializations using the SymptomMapping model
        specializations = set()
        for symptom in symptoms:
            mappings = SymptomMapping.objects.filter(symptom__iexact=symptom)
            for mapping in mappings:
                specializations.add(mapping.specialization)

        # Fallback: If no mappings are found, use a simple dictionary
        if not specializations:
            fallback_map = {
                'headache': 'Neurology',
                'fever': 'General Medicine',
                'chest pain': 'Cardiology',
                'cough': 'Pulmonology',
                'abdominal pain': 'Gastroenterology',
            }
            for symptom in symptoms:
                if symptom in fallback_map:
                    specializations.add(fallback_map[symptom])

        if not specializations:
            return JsonResponse({'error': 'No matching specializations found for the identified symptoms.'}, status=404)

        # Find doctors with matching specializations
        doctors = Doctor.objects.filter(specialization__in=specializations)
        if not doctors.exists():
            return JsonResponse({'error': 'No doctors found for the identified specializations.'}, status=404)

        doctor_list = [
            {'id': doctor.id, 'name': doctor.name, 'specialization': doctor.specialization, 'slots': doctor.available_slots.split(',')}
            for doctor in doctors
        ]

        return JsonResponse({'doctors': doctor_list})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def book_appointment_api(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date', datetime.now().strftime('%Y-%m-%d'))  # Default to today
        time = request.POST.get('time')

        if not all([name, email, phone, doctor_id, time]):
            return JsonResponse({'error': 'All fields (name, email, phone, doctor_id, time) are required'}, status=400)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            available_slots = doctor.available_slots.split(",")

            if time not in available_slots:
                return JsonResponse({'error': 'Invalid time slot selected'}, status=400)

            time_obj = datetime.strptime(time, "%H:%M").time()
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()

            appointment = Appointment.objects.create(
                user=request.user,
                patient_name=name,
                patient_email=email,
                patient_contact=phone,
                doctor=doctor,
                date=date_obj,
                time=time_obj,
                status='Pending'
            )

            send_session_notification(
                appointments=[appointment],
                subject="Appointment Booking Confirmation",
                message="Your appointment has been successfully booked with DigiTAL via AI Assistant."
            )

            return JsonResponse({'success': True, 'message': 'Appointment booked successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)