from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Doctor

def doctors_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors/doctors_list.html', {'doctors': doctors})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doctor

@login_required
def get_doctor_slots(request, doctor_id):
    """Fetch available slots for a selected doctor."""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        slots = doctor.available_slots.split(',')  # Convert stored slots to list
        return JsonResponse({'slots': slots})
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)