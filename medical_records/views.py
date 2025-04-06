# medical_records/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import MedicalRecord 
from appointments.models import Appointment
from doctors.models import Doctor

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

@login_required
@role_required('doctor')
def medical_records_list(request):
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Only doctors can access this page.")

    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("No doctor profile found for this user.")

    appointments = Appointment.objects.filter(doctor=doctor)
    patient_names = appointments.values_list('patient_name', flat=True)
    
    medical_records = MedicalRecord.objects.filter(patient_name__in=patient_names).order_by('-created_at')

    return render(request, 'medical_records/medical_records_list.html', {
        'medical_records': medical_records,
        'doctor': doctor
    })