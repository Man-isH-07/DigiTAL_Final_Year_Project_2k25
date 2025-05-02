from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from appointments.models import Appointment
from doctors.models import Doctor
from django.contrib import messages
from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment, SessionHistory
from django import forms
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from lab_report.models import Patient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_required
def manual_booking(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_grp')
        symptoms = request.POST.get('symptoms', '')

        doctor = Doctor.objects.get(id=doctor_id)
        available_slots = doctor.available_slots.split(",")

        if time not in available_slots:
            messages.error(request, "Invalid time slot selected!")
            return redirect('manual_booking')

        time_obj = datetime.strptime(time, "%H:%M").time()

        appointment = Appointment.objects.create(
            user=request.user,
            doctor=doctor,
            date=date,
            time=time_obj,
            patient_name=name,
            patient_age=age,
            patient_contact=contact,
            patient_email=email,
            gender=gender,
            blood_group=blood_group,
            symptoms=symptoms,
            status='Pending'
        )

        # Create or update Patient instance
        try:
            patient = Patient.objects.get(email=email)
            if patient.name != name or patient.phone != contact:
                patient.name = name
                patient.phone = contact
                patient.save()
                logger.info(f"Updated patient: {patient.id}, {patient.name}, {patient.email}, {patient.phone}")
        except Patient.DoesNotExist:
            try:
                patient = Patient.objects.create(
                    email=email,
                    name=name,
                    phone=contact
                )
                logger.info(f"Created patient: {patient.id}, {patient.name}, {patient.email}, {patient.phone}")
            except Exception as e:
                messages.error(request, f"Failed to create patient: {e}")
                logger.error(f"Error creating patient: {e}")
                return redirect('manual_booking')

        send_session_notification(
            appointments=[appointment],
            subject="Appointment Booking Confirmation",
            message="Your appointment has been successfully booked with DigiTAL."
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect('manual_booking')

    doctors = Doctor.objects.all()
    return render(request, 'appointments/manual_booking.html', {'doctors': doctors})

@login_required
def get_doctor_slots(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        slots = doctor.available_slots.split(',')
        return JsonResponse({'slots': slots})
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

@login_required
def appointment_history(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-date', '-time')
    active_session = SessionHistory.objects.filter(is_active=True).first()
    session_data = {
        'doctor_id': active_session.doctor.id if active_session else None,
        'date': active_session.date.strftime('%Y-%m-%d') if active_session else None,
        'slot': active_session.slot if active_session else None,
        'patient_timer': active_session.patient_timer if active_session else 1200
    } if active_session else {}
    
    for appt in appointments:
        if appt.status == 'Pending':
            appt.live_wait_time = appt.calculate_live_wait_time(session_data)
        else:
            appt.live_wait_time = 0
    return render(request, 'users/appointment_history.html', {'appointments': appointments})

@login_required
def live_wait_time_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    active_session = SessionHistory.objects.filter(is_active=True).first()
    initial_wait_time_seconds = None  

    if active_session and appointment.status == 'Pending':
        session_data = {
            'doctor_id': active_session.doctor.id,
            'date': active_session.date.strftime('%Y-%m-%d'),
            'slot': active_session.slot,
            'patient_timer': active_session.patient_timer
        }
        initial_wait_time_minutes = appointment.calculate_live_wait_time(session_data)
        initial_wait_time_seconds = int(initial_wait_time_minutes * 60)

        if active_session.current_patient:
            queue_position = appointment.queue_position
            if queue_position == 1:  
                initial_wait_time_seconds = max(0, active_session.patient_timer)
            else:
                base_wait_time = (queue_position - 1) * 20 * 60  
                elapsed_time = 1200 - active_session.patient_timer  
                initial_wait_time_seconds = max(0, base_wait_time - elapsed_time)

    print(f"Debug - live_wait_time_detail: appointment_id={appointment_id}, initial_wait_time_seconds={initial_wait_time_seconds}, appointment.id={appointment.id}")

    return render(request, 'users/live_wait_time_detail.html', {
        'appointment': appointment,
        'initial_wait_time_seconds': initial_wait_time_seconds, 
        'session_active': active_session is not None  
    })
    
class QueueFilterForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Doctor")
    date = forms.DateField(label="Date", widget=forms.DateInput(attrs={'type': 'date'}))
    slot = forms.ChoiceField(choices=[], label="Time Slot")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slot'].choices = [('', 'Select a Time Slot')] + [
            (slot, slot) for slot in ["09:00", "12:00", "15:00", "18:00"]
        ]

class WaitingRoomForm(forms.Form):
    pass

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'doctor']

@login_required
def virtual_waiting_room(request):
    if request.user.role != 'desk':
        return HttpResponseForbidden("Only desk users can access this page.")

    session_started = False
    current_patient = None
    session_start_time = None
    appointments = None
    can_start_session = False
    error = None

    queue_form = QueueFilterForm()
    session_form = WaitingRoomForm()

    # Check for an active session in SessionHistory
    active_session = SessionHistory.objects.filter(is_active=True).first()
    if active_session:
        doctor = active_session.doctor
        date = active_session.date
        slot = active_session.slot
        current_patient = active_session.current_patient
        session_start_time = active_session.start_time
        remaining_time = active_session.patient_timer

        appointments = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time__startswith=slot,
            status='Pending'
        ).order_by('queue_position')

        # If there are no Pending appointments, end the session
        if not appointments.exists():
            active_session.is_active = False
            active_session.end_time = timezone.now()
            active_session.duration_minutes = (active_session.end_time - active_session.start_time).total_seconds() // 60
            active_session.save()
            active_session = None  # Clear the active session
            current_patient = None
            session_start_time = None
            appointments = None
            session_started = False
        else:
            session_started = True

            # Calculate initial wait times for rendering
            for appt in appointments:
                if appt != current_patient:
                    adjusted_position = appt.queue_position
                    if adjusted_position <= 0:
                        continue
                    appt.live_wait_time = adjusted_position * 20
                else:
                    appt.live_wait_time = 0

    if request.method == 'POST' and 'filter_queue' in request.POST:
        queue_form = QueueFilterForm(request.POST)
        if queue_form.is_valid():
            doctor = queue_form.cleaned_data['doctor']
            date = queue_form.cleaned_data['date']
            slot = queue_form.cleaned_data['slot']
        else:
            doctor_id = request.POST.get('doctor', '')
            date_str = request.POST.get('date', '')
            slot = request.POST.get('slot', '')
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except (Doctor.DoesNotExist, ValueError) as e:
                logger.error(f"Error processing filter queue: {str(e)}")
                error = "Invalid doctor or date format. Please try again."
                return render(request, 'appointments/virtual_waiting_room.html', {
                    'queue_form': QueueFilterForm(),
                    'session_form': WaitingRoomForm(),
                    'doctors': Doctor.objects.all(),
                    'appointments': None,
                    'session_started': False,
                    'current_patient': None,
                    'session_start_time': None,
                    'can_start_session': False,
                    'error': error
                })

        adjusted_slots = doctor.get_adjusted_slots(date)
        if slot not in adjusted_slots:
            slot += ':00'

        if SessionHistory.objects.filter(doctor=doctor, date=date, slot=slot, is_active=False).exists():
            error = f"A session for Dr. {doctor.name} on {date} at {slot} has already ended."
            return render(request, 'appointments/virtual_waiting_room.html', {
                'queue_form': QueueFilterForm(),
                'session_form': WaitingRoomForm(),
                'doctors': Doctor.objects.all(),
                'appointments': None,
                'session_started': False,
                'current_patient': None,
                'session_start_time': None,
                'can_start_session': False,
                'error': error
            })

        appointments = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time__startswith=slot,
            status='Pending'
        ).order_by('queue_position')

        for i, appt in enumerate(appointments, start=1):
            appt.queue_position = i
            appt.save()

        can_start_session = True
        request.session['filtered_data'] = {
            'doctor_id': doctor.id,
            'date': date.strftime('%Y-%m-%d'),
            'slot': slot
        }

        return render(request, 'appointments/virtual_waiting_room.html', {
            'queue_form': QueueFilterForm(),
            'session_form': WaitingRoomForm(),
            'doctors': Doctor.objects.all(),
            'appointments': appointments,
            'session_started': False,
            'current_patient': None,
            'session_start_time': None,
            'can_start_session': can_start_session,
            'error': error
        })

    if request.method == 'POST' and 'start_session' in request.POST:
        filtered_data = request.session.get('filtered_data', {})
        if filtered_data:
            try:
                doctor = Doctor.objects.get(id=filtered_data['doctor_id'])
                date = datetime.strptime(filtered_data['date'], '%Y-%m-%d').date()
                slot = filtered_data['slot']

                adjusted_slots = doctor.get_adjusted_slots(date)
                if slot not in adjusted_slots:
                    slot += ':00'

                appointments = Appointment.objects.filter(
                    doctor=doctor,
                    date=date,
                    time__startswith=slot,
                    status='Pending'
                ).order_by('queue_position')

                if appointments.exists():
                    current_patient = appointments.first()
                    SessionHistory.objects.create(
                        doctor=doctor,
                        date=date,
                        slot=slot,
                        start_time=timezone.now(),
                        is_active=True,
                        current_patient=current_patient,
                        patient_timer=1200
                    )

                    send_session_notification(
                        appointments=appointments,
                        subject="Virtual Waiting Room Session Started",
                        message=f"Your appointment session for Dr. {doctor.name} on {date} at {slot} has started.",
                        include_wait_time=True
                    )

                    del request.session['filtered_data']
                    return redirect('virtual_waiting_room')
            except Doctor.DoesNotExist:
                error = "Doctor not found. Please filter again."

    if request.method == 'POST' and 'treated' in request.POST:
        active_session = SessionHistory.objects.filter(is_active=True).first()
        if active_session:
            try:
                doctor = active_session.doctor
                date = active_session.date
                slot = active_session.slot

                current_patient = active_session.current_patient
                current_patient.status = 'Treated'
                current_patient.save()

                remaining_appointments = Appointment.objects.filter(
                    doctor=doctor, date=date, time__startswith=slot, status='Pending'
                ).order_by('queue_position')
                for i, appt in enumerate(remaining_appointments, start=1):
                    appt.queue_position = i
                    appt.save()

                appointments = remaining_appointments

                if appointments.exists():
                    next_patient = appointments.first()
                    active_session.current_patient = next_patient
                    active_session.patient_timer = 1200  # Force reset to 20 minutes
                    active_session.save()
                    return JsonResponse({
                        'success': True,
                        'next_patient_id': next_patient.id,
                        'next_patient_name': next_patient.patient_name,
                        'patient_timer': 1200
                    })
                else:
                    active_session.is_active = False
                    active_session.end_time = timezone.now()
                    active_session.duration_minutes = (active_session.end_time - active_session.start_time).total_seconds() // 60
                    active_session.save()
                    return JsonResponse({'success': True, 'next_patient_id': None})
            except Exception as e:
                logger.error(f"Error processing treated patient: {str(e)}")
                error = "Error processing treated patient."
                return JsonResponse({'success': False, 'error': str(e)})

    if request.method == 'POST' and 'end_session' in request.POST:
        active_session = SessionHistory.objects.filter(is_active=True).first()
        if active_session:
            try:
                active_session.is_active = False
                active_session.end_time = timezone.now()
                active_session.duration_minutes = (active_session.end_time - active_session.start_time).total_seconds() // 60
                active_session.save()

                return render(request, 'appointments/virtual_waiting_room.html', {
                    'queue_form': QueueFilterForm(),
                    'session_form': WaitingRoomForm(),
                    'doctors': Doctor.objects.all(),
                    'appointments': None,
                    'session_started': False,
                    'current_patient': None,
                    'session_start_time': None,
                    'can_start_session': False,
                    'error': None,
                    'message': 'Session ended successfully.'
                })
            except Exception as e:
                logger.error(f"Error ending session: {str(e)}")
                error = "Error ending session."

    return render(request, 'appointments/virtual_waiting_room.html', {
        'queue_form': queue_form,
        'session_form': session_form,
        'doctors': Doctor.objects.all(),
        'appointments': appointments,
        'session_started': session_started,
        'current_patient': current_patient,
        'session_start_time': session_start_time,
        'can_start_session': can_start_session,
        'error': error
    })

@login_required
@csrf_exempt
def update_queue_status(request):
    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        action = request.POST.get("action")
        active_session = SessionHistory.objects.filter(is_active=True).first()

        if not active_session or not appointment_id or not action:
            return JsonResponse({"success": False, "error": "Invalid request data or no active session"})

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if action == "treated":
                active_session.current_patient = None
                active_session.patient_timer = 1200  # Reset to 20 minutes
                if Appointment.objects.filter(doctor=active_session.doctor, date=active_session.date, time__startswith=active_session.slot, status='Pending').exists():
                    next_patient = Appointment.objects.filter(
                        doctor=active_session.doctor, date=active_session.date, time__startswith=active_session.slot, status='Pending'
                    ).order_by('queue_position').first()
                    active_session.current_patient = next_patient
                    active_session.patient_timer = 1200  # Reset for new patient
                    next_patient_name = next_patient.patient_name
                else:
                    next_patient_name = None
                appointment.status = "Treated"
                appointment.save()
                active_session.save()
                return JsonResponse({
                    "success": True,
                    "next_patient_id": active_session.current_patient.id if active_session.current_patient else None,
                    "next_patient_name": next_patient_name,
                    "patient_timer": active_session.patient_timer
                })
            elif action == "skip":
                appointment.status = "Skipped"
                appointment.save()
                if Appointment.objects.filter(doctor=active_session.doctor, date=active_session.date, time__startswith=active_session.slot, status='Pending').exists():
                    next_patient = Appointment.objects.filter(
                        doctor=active_session.doctor, date=active_session.date, time__startswith=active_session.slot, status='Pending'
                    ).order_by('queue_position').first()
                    active_session.current_patient = next_patient
                    active_session.patient_timer = 1200  # Reset for new patient
                    next_patient_name = next_patient.patient_name
                else:
                    next_patient_name = None
                active_session.save()
                return JsonResponse({
                    "success": True,
                    "next_patient_id": active_session.current_patient.id if active_session.current_patient else None,
                    "next_patient_name": next_patient_name,
                    "patient_timer": active_session.patient_timer
                })
            elif action == "add_time":
                active_session.patient_timer = active_session.patient_timer + 300  # Add 5 minutes (300 seconds), no cap
                active_session.save()
                return JsonResponse({
                    "success": True,
                    "patient_timer": active_session.patient_timer
                })
        except Appointment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Appointment not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid method"})

@login_required
def fetch_patient_timer(request):
    active_session = SessionHistory.objects.filter(is_active=True).first()
    if active_session and active_session.patient_timer is not None:
        return JsonResponse({"success": True, "current_patient_timer": active_session.patient_timer})
    elif active_session:
        elapsed_seconds = (timezone.now() - active_session.start_time).total_seconds()
        remaining_seconds = max(0, 1200 - elapsed_seconds)
        active_session.patient_timer = int(remaining_seconds)
        active_session.save()
        return JsonResponse({"success": True, "current_patient_timer": int(remaining_seconds)})
    else:
        return JsonResponse({"success": False, "error": "No active session found."})
    
@login_required
@csrf_exempt
def save_patient_timer(request):
    if request.method == 'POST':
        remaining_time = int(request.POST.get('remaining_time', 1200))
        active_session = SessionHistory.objects.filter(is_active=True).first()
        if active_session:
            active_session.patient_timer = remaining_time
            active_session.save()
            return JsonResponse({"success": True, "saved_time": remaining_time})
        else:
            return JsonResponse({"success": False, "error": "No active session to save timer."})
    return JsonResponse({"success": False, "error": 'Invalid request method'})

@login_required
def fetch_wait_times(request):
    active_session = SessionHistory.objects.filter(is_active=True).first()
    wait_times = []
    time_format = request.GET.get('format', 'seconds')

    if active_session:
        doctor = active_session.doctor
        date = active_session.date
        slot = active_session.slot
        current_patient_timer = active_session.patient_timer
        current_patient_id = active_session.current_patient.id if active_session.current_patient else None

        try:
            adjusted_slots = doctor.get_adjusted_slots(date)
            if slot not in adjusted_slots:
                slot += ':00'
            session_appointments = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time__startswith=slot,
                status='Pending'
            ).order_by('queue_position')

            session_data = {
                'doctor_id': doctor.id,
                'date': date.strftime('%Y-%m-%d'),
                'slot': slot,
                'patient_timer': current_patient_timer,  # Include the live timer
                'current_patient_id': current_patient_id
            }

            for appt in session_appointments:
                # Calculate wait time based on queue position and current patient's timer
                if appt.id == current_patient_id:
                    # Current patient: wait time is the remaining timer
                    wait_time_minutes = max(0, current_patient_timer / 60)
                else:
                    # Subsequent patients: wait time is current patient's timer + (position - 1) * 20 minutes
                    position = appt.queue_position
                    if position <= 1:
                        wait_time_minutes = 0  # Shouldn't happen since current patient is handled above
                    else:
                        # Use the actual current patient timer instead of a fixed 20 minutes
                        wait_time_minutes = max(0, (current_patient_timer / 60) + (position - 2) * 20)

                if time_format == 'seconds':
                    wait_time = int(wait_time_minutes * 60)
                else:
                    wait_time = int(wait_time_minutes)

                wait_times.append({
                    "id": appt.id,
                    "wait_time": wait_time,
                    "status": appt.status,
                    "patient_name": appt.patient_name,
                    "time": appt.time.strftime('%H:%M'),
                    "queue_position": appt.queue_position
                })
        except Doctor.DoesNotExist as e:
            logger.error(f"Doctor not found in fetch_wait_times: {str(e)}")

    return JsonResponse({"success": True, "wait_times": wait_times})
    
@login_required
def adjust_doctor_slot(request):
    if request.user.role != 'desk':
        return HttpResponseForbidden("Only desk users can adjust slots.")
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        hours = int(request.POST.get('hours', 0))  
        doctor = Doctor.objects.get(id=doctor_id)
        doctor.temp_slot_adjustment = hours
        doctor.save()
        appointments = Appointment.objects.filter(doctor=doctor, date=date)
        for appt in appointments:
            appt.time = time(hour=(appt.time.hour + hours) % 24, minute=appt.time.minute)  # Adjust time
            appt.save()
        return JsonResponse({'success': True})
    doctors = Doctor.objects.all()
    return render(request, 'appointments/adjust_slot.html', {'doctors': doctors})

from django.core.mail import send_mail
from django.conf import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

def send_session_notification(appointments, subject, message, include_wait_time=False, session_data=None):
    for appointment in appointments:
        if not appointment.patient_email:
            logger.warning(f"No email provided for appointment ID {appointment.id}")
            continue

        detailed_message = (
            f"{message}\n\n"
            f"Appointment Details:\n"
            f"Doctor: {appointment.doctor.name}\n"
            f"Date: {appointment.date}\n"
            f"Time: {appointment.time.strftime('%H:%M')}\n"
            f"Patient: {appointment.patient_name}\n"
        )

        if include_wait_time and appointment.status == 'Pending':
            wait_time = appointment.calculate_live_wait_time(session_data) if session_data else appointment.calculate_wait_time()
            detailed_message += f"Current Wait Time: {int(wait_time)} minutes\n"

        try:
            send_mail(
                subject=subject,
                message=detailed_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[appointment.patient_email],
                fail_silently=False,
            )
            logger.info(f"Email sent to {appointment.patient_email} for appointment ID {appointment.id}")
        except Exception as e:
            logger.error(f"Failed to send email to {appointment.patient_email}: {str(e)}")

# for doctor Dashboard
@login_required
def fetch_session_status(request):
    if request.user.role != 'doctor':
        return JsonResponse({'success': False, 'error': 'Only doctors can access this page.'})

    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No doctor profile found.'})

    current_date = datetime.now().date()
    active_session = SessionHistory.objects.filter(
        doctor=doctor,
        date=current_date,
        is_active=True
    ).first()

    if active_session:
        return JsonResponse({
            'success': True,
            'is_active': active_session.is_active,
            'slot': active_session.slot,
            'start_time': active_session.start_time.strftime('%H:%M'),
            'current_patient_id': active_session.current_patient.id if active_session.current_patient else None,
            'current_patient_name': active_session.current_patient.patient_name if active_session.current_patient else None,
            'patient_timer': active_session.patient_timer,
        })
    else:
        return JsonResponse({
            'success': True,
            'is_active': False,
        })