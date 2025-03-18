from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from appointments.models import Appointment, Doctor
from appointments.views import send_session_notification
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import SymptomMapping
import spacy

nlp = spacy.load("en_ner_bc5cdr_md")


@login_required
def analyze_symptoms(request):
    if request.method == 'GET':
        symptoms_text = request.GET.get('symptoms', '').lower()
        if not symptoms_text:
            return JsonResponse({'error': 'Symptoms are required'}, status=400)

        doc = nlp(symptoms_text)
        symptoms = list(set([ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]))

        if not symptoms:
            symptoms = [symptoms_text]

        doctors = []
        seen_doctors = set()  # To avoid duplicates
        for symptom in symptoms:
            print(f"Processing symptom: {symptom}")
            # Fetch all mappings without distinct
            mappings = SymptomMapping.objects.filter(symptom__iexact=symptom)
            for mapping in mappings:
                if mapping.doctor and mapping.doctor.id not in seen_doctors:
                    doctor_data = {
                        'id': mapping.doctor.id,
                        'name': mapping.doctor.name,
                        'specialization': mapping.doctor.specialization,
                        'slots': mapping.doctor.available_slots.split(',') if isinstance(mapping.doctor.available_slots, str) else mapping.doctor.available_slots
                    }
                    doctors.append(doctor_data)
                    seen_doctors.add(mapping.doctor.id)

        if not doctors:
            fallback_map = {
                'headache': 'Neurology',
                'fever': 'General Medicine',
                'chest pain': 'Cardiology',
                'cough': 'Pulmonology',
                'abdominal pain': 'Gastroenterology',
            }
            for symptom in symptoms:
                if symptom in fallback_map:
                    # Fetch doctors without distinct
                    fallback_doctors = Doctor.objects.filter(specialization=fallback_map[symptom]).values(
                        'id', 'name', 'specialization', 'available_slots'
                    )
                    for doctor in fallback_doctors:
                        if doctor['id'] not in seen_doctors:
                            doctor_data = {
                                'id': doctor['id'],
                                'name': doctor['name'],
                                'specialization': doctor['specialization'],
                                'slots': doctor['available_slots'].split(',') if isinstance(doctor['available_slots'], str) else doctor['available_slots']
                            }
                            doctors.append(doctor_data)
                            seen_doctors.add(doctor['id'])

        if not doctors:
            return JsonResponse({'error': 'No doctors found for the identified symptoms.'}, status=404)

        return JsonResponse({'doctors': doctors})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def book_appointment_api(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date', datetime.now().strftime('%Y-%m-%d'))
        time = request.POST.get('time')

        if not all([name, email, phone, doctor_id, time]):
            return JsonResponse({'error': 'All fields (name, email, phone, doctor_id, time) are required'}, status=400)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            available_slots = doctor.available_slots.split(",") if doctor.available_slots else []

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

            return JsonResponse({'message': 'Appointment booked successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)