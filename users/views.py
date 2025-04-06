from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password
from appointments.views import send_session_notification
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from appointments.models import Appointment, SessionHistory
from doctors.models import Doctor
from datetime import datetime
from lab_report.models import LabTest, Patient, LabReport
import base64
from django.core.files.base import ContentFile
import uuid
import json
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser
from appointments.models import Appointment
from medical_records.models import MedicalRecord
import hashlib
from blockchain.utils import add_record_to_blockchain
from blockchain.models import BlockchainRecord
from django.core.mail import EmailMessage
from django.conf import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to access this page.")

    errors = []
    if request.method == 'POST':
        if 'change_password' in request.POST:
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password and confirm_password and new_password == confirm_password:
                user = get_object_or_404(CustomUser, id=user_id)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, f"Password changed successfully for {user.username}!")
            else:
                messages.error(request, "Passwords do not match or are empty.")
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            role = request.POST.get('role')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            specialization = request.POST.get('specialization', 'General')
            experience = request.POST.get('experience', 0)
            available_slots = request.POST.get('available_slots', '09:00,12:00,15:00')

            if not username or not email or not role or not password1 or not password2:
                errors.append("All fields are required.")
            if password1 != password2:
                errors.append("Passwords do not match.")
            if CustomUser.objects.filter(username=username).exists():
                errors.append("Username already exists.")
            if CustomUser.objects.filter(email=email).exists():
                errors.append("Email already exists.")
            if role not in ['admin', 'doctor', 'desk', 'user', 'lab_technician']:
                errors.append("Invalid role selected.")

            if not errors:
                user = CustomUser.objects.create(
                    username=username,
                    email=email,
                    role=role,
                    password=make_password(password1)
                )
                if role == 'doctor':
                    Doctor.objects.create(
                        user=user,
                        name=username,
                        specialization=specialization,
                        experience=int(experience),
                        available_slots=available_slots
                    )
                messages.success(request, f"User {username} created successfully!")
                return redirect('admin_dashboard')
            else:
                for error in errors:
                    messages.error(request, error)

    users = CustomUser.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'users/admin_dashboard.html', {
        'errors': errors,
        'users': users,
        'doctors': doctors
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        selected_role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == selected_role:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.role == 'desk':
                    return redirect('desk_dashboard')
                elif user.role == 'user':
                    return redirect('user_dashboard')
                elif user.role == 'lab_technician':
                    return redirect('lab_dashboard')
            else:
                return render(request, 'users/login.html', {'error': 'Role mismatch. Please select the correct role.'})
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing')  

@login_required
def user_dashboard(request):
    if request.user.role != 'user':
        return HttpResponseForbidden("Only users can access this page.")

    # Get the user's appointments (only completed ones)
    appointments = Appointment.objects.filter(
        patient_email=request.user.email,
        status='Completed'
    )

    # Get lab reports associated with these appointments
    lab_reports = []
    for appointment in appointments:
        try:
            patient = Patient.objects.get(email=appointment.patient_email)
            # Get lab reports for this patient with status 'Completed'
            reports = LabReport.objects.filter(patient=patient, status='Completed')
            lab_reports.extend(reports)
        except Patient.DoesNotExist:
            continue

    # Get prescriptions associated with these appointments
    prescriptions = []
    for appointment in appointments:
        # Find medical records of type 'Prescription' for this appointment
        medical_records = MedicalRecord.objects.filter(
            patient_name=appointment.patient_name,
            record_type='Prescription',
            doctor=appointment.doctor.user  # Ensure the doctor matches
        )
        prescriptions.extend(medical_records)

    return render(request, 'users/user_dashboard.html', {
        'lab_reports': lab_reports,
        'prescriptions': prescriptions  # Pass prescriptions to the template
    })

@login_required
def user_reports_and_prescriptions(request):
    if request.user.role != 'user':
        return HttpResponseForbidden("Only users can access this page.")

    # Get the user's appointments (only completed ones)
    appointments = Appointment.objects.filter(
        patient_email=request.user.email,
        status='Completed'
    )

    # Get lab reports associated with these appointments
    lab_reports = []
    for appointment in appointments:
        try:
            patient = Patient.objects.get(email=appointment.patient_email)
        except Patient.DoesNotExist:
            # Create the Patient if it doesn't exist
            try:
                patient = Patient.objects.create(
                    email=appointment.patient_email,
                    name=appointment.patient_name,
                    phone=appointment.patient_contact
                )
                logger.info(f"Created patient: {patient.id}, {patient.name}, {patient.email}, {patient.phone}")
            except Exception as e:
                logger.error(f"Error creating patient: {e}")
                continue
        # Get lab reports for this patient with status 'Completed'
        reports = LabReport.objects.filter(patient=patient, status='Completed')
        lab_reports.extend(reports)

    # Get prescriptions associated with these appointments
    prescriptions = []
    for appointment in appointments:
        # Find medical records of type 'Prescription' for this appointment
        medical_records = MedicalRecord.objects.filter(
            patient_name=appointment.patient_name,
            record_type='Prescription',
            doctor=appointment.doctor.user  # Ensure the doctor matches
        )
        prescriptions.extend(medical_records)

    # Sort lab reports by updated_at (newest to oldest)
    lab_reports.sort(key=lambda x: x.updated_at, reverse=True)

    # Sort prescriptions by created_at (newest to oldest)
    prescriptions.sort(key=lambda x: x.created_at, reverse=True)

    return render(request, 'users/user_reports_and_prescriptions.html', {
        'lab_reports': lab_reports,
        'prescriptions': prescriptions
    })

@login_required
def desk_dashboard(request):
    if request.user.role != 'desk':
        return HttpResponseForbidden("Only desk users can access this page.")

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')

        if not all([name, email, phone, doctor_id, date, time]):
            messages.error(request, "All fields are required.")
            return redirect('desk_dashboard')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            available_slots = doctor.available_slots.split(",")

            if time not in available_slots:
                messages.error(request, "Invalid time slot selected!")
                return redirect('desk_dashboard')

            time_obj = datetime.strptime(time, "%H:%M").time()
            date_obj = datetime.strptime(date, '%Y-%m-d').date()

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
                message="Your appointment has been successfully booked with DigiTAL."
            )

            # Create or update Patient instance
            try:
                patient = Patient.objects.get(email=email)
                # If the patient's name or phone doesn't match, update it
                if patient.name != name or patient.phone != phone:
                    patient.name = name
                    patient.phone = phone
                    patient.save()
                    print(f"Updated patient: {patient.id}, {patient.name}, {patient.email}, {patient.phone}")
            except Patient.DoesNotExist:
                try:
                    patient = Patient.objects.create(
                        email=email,
                        name=name,
                        phone=phone
                    )
                    print(f"Created patient: {patient.id}, {patient.name}, {patient.email}, {patient.phone}")
                except Exception as e:
                    messages.error(request, f"Failed to create patient: {e}")
                    print(f"Error creating patient: {e}")
                    return redirect('desk_dashboard')

            messages.success(request, "Appointment booked successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            print(f"Error in desk_dashboard: {e}")

        return redirect('desk_dashboard')

    doctors = Doctor.objects.all()

    return render(request, 'users/desk_dashboard.html', {
        'doctors': doctors,
    })


from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.contrib import messages
from appointments.views import send_session_notification
from appointments.models import Appointment, SessionHistory
from doctors.models import Doctor
from datetime import datetime
from medical_records.models import MedicalRecord
from lab_report.models import LabTest, Patient, LabReport
import base64
from django.core.files.base import ContentFile
import uuid
import json
from django.core.mail import EmailMessage
from django.conf import settings
import logging
from blockchain.utils import add_record_to_blockchain
from blockchain.models import BlockchainRecord
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@role_required('doctor')
@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Only doctors can access this page.")

    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("No doctor profile found for this user.")

    current_date = datetime.now().date()
    active_session = SessionHistory.objects.filter(
        doctor=doctor,
        date=current_date,
        is_active=True
    ).first()

    current_patient = None
    if active_session:
        current_patient = active_session.current_patient

    medical_records = MedicalRecord.objects.filter(doctor=request.user, record_type='LabRequest')
    lab_reports = [record.lab_report for record in medical_records if record.lab_report]

    if request.method == 'POST':
        if 'save_all' in request.POST:
            patient_id = request.POST.get('patient_id')
            prescription_image_data = request.POST.get('prescription_image')
            lab_requests = request.POST.getlist('lab_requests[]')
            if patient_id:
                appointment = get_object_or_404(Appointment, id=patient_id)
                doctor_id = request.user.doctor_profile.id

                if prescription_image_data:
                    format, imgstr = prescription_image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_file = ContentFile(base64.b64decode(imgstr), name=f'prescription_{uuid.uuid4()}.{ext}')
                    medical_record = MedicalRecord.objects.create(
                        patient_name=appointment.patient_name,
                        doctor=request.user,
                        record_type='Prescription',
                        data='',
                        prescription_image=image_file
                    )
                    data_hash = hashlib.sha256(imgstr.encode()).hexdigest()
                    record_id, tx_hash = add_record_to_blockchain(
                        data_hash=data_hash,
                        record_type='Prescription',
                        patient_email=appointment.patient_email,
                        doctor_id=doctor_id
                    )
                    medical_record.blockchain_record_id = record_id
                    medical_record.transaction_hash = tx_hash
                    medical_record.save()
                    BlockchainRecord.objects.create(
                        record_id=record_id,
                        transaction_hash=tx_hash,
                        data_hash=data_hash,
                        record_type='Prescription',
                        patient_email=appointment.patient_email,
                        doctor_id=doctor_id
                    )
                    patient_email = appointment.patient_email
                    subject = 'Your Prescription from DigiTEL'
                    message = f'Dear {appointment.patient_name},\n\nPlease find your prescription attached.\n\nBest regards,\nDigiTEL Team'
                    email = EmailMessage(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [patient_email],
                    )
                    email.attach_file(medical_record.prescription_image.path)
                    email.send()

                if lab_requests:
                    for test_name in lab_requests:
                        if not LabTest.objects.filter(name=test_name).exists():
                            LabTest.objects.create(name=test_name)
                    try:
                        patient = Patient.objects.get(email=appointment.patient_email)
                        if patient.name != appointment.patient_name or patient.phone != appointment.patient_contact:
                            patient.name = appointment.patient_name
                            patient.phone = appointment.patient_contact
                            patient.save()
                    except Patient.DoesNotExist:
                        patient = Patient.objects.create(
                            email=appointment.patient_email,
                            name=appointment.patient_name,
                            phone=appointment.patient_contact
                        )
                    lab_report = LabReport.objects.create(
                        patient=patient,
                        doctor=request.user,
                        tests=json.dumps(lab_requests),
                        status='Pending'
                    )
                    medical_record = MedicalRecord.objects.create(
                        patient_name=appointment.patient_name,
                        doctor=request.user,
                        record_type='LabRequest',
                        data=json.dumps(lab_requests),
                        lab_report=lab_report
                    )
                    data_hash = hashlib.sha256(json.dumps(lab_requests).encode()).hexdigest()
                    record_id, tx_hash = add_record_to_blockchain(
                        data_hash=data_hash,
                        record_type='LabRequest',
                        patient_email=appointment.patient_email,
                        doctor_id=doctor_id
                    )
                    medical_record.blockchain_record_id = record_id
                    medical_record.transaction_hash = tx_hash
                    medical_record.save()
                    BlockchainRecord.objects.create(
                        record_id=record_id,
                        transaction_hash=tx_hash,
                        data_hash=data_hash,
                        record_type='LabRequest',
                        patient_email=appointment.patient_email,
                        doctor_id=doctor_id
                    )

                messages.success(request, "Prescription and lab requests saved successfully! Data stored on blockchain.")
                return redirect('doctor_dashboard')
        else:
            messages.error(request, "Invalid form submission.")

    return render(request, 'users/doctor_dashboard.html', {
        'doctor': doctor,
        'doctor_name': doctor.name,
        'current_date': current_date,
        'active_session': active_session,
        'current_patient': current_patient,
        'lab_reports': lab_reports
    })

@login_required
def secure_view(request):
    return render(request, 'secure_page.html')

@login_required
def edit_user(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to access this page.")

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')

        errors = []
        if not username or not email or not role:
            errors.append("All fields are required.")
        if role not in ['admin', 'doctor', 'desk', 'user', 'lab_technician']:
            errors.append("Invalid role selected.")
        if CustomUser.objects.filter(username=username).exclude(id=user_id).exists():
            errors.append("Username already exists.")
        if CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
            errors.append("Email already exists.")

        if not errors:
            user.username = username
            user.email = email
            user.role = role
            user.save()

            messages.success(request, f"User {username} updated successfully!")
            return redirect('admin_dashboard')
        else:
            for error in errors:
                messages.error(request, error)

    return render(request, 'users/edit_user.html', {
        'user': user,
    })

@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to access this page.")

    user = CustomUser.objects.get(id=user_id)
    user.delete()
    return redirect('admin_dashboard')