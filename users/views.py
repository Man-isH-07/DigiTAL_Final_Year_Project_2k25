from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.http import HttpResponseForbidden
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from appointments.views import send_session_notification
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.contrib import messages
from appointments.models import Appointment, SessionHistory
from doctors.models import Doctor
from datetime import datetime
from medical_records.models import MedicalRecord
from lab_report.models import LabTest, Patient, LabReport
import base64
from django.core.files.base import ContentFile
import uuid
import json

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
    return render(request, 'users/user_dashboard.html')

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

            # Create or get Patient instance
            patient, created = Patient.objects.get_or_create(
                email=email,
                defaults={'name': name, 'phone': phone}
            )

            messages.success(request, "Appointment booked successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('desk_dashboard')

    doctors = Doctor.objects.all()

    return render(request, 'users/desk_dashboard.html', {
        'doctors': doctors,
    })

@role_required('doctor')
@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Only doctors can access this page.")

    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("No doctor profile found for this user. Please contact the admin to create a doctor profile.")

    current_date = datetime.now().date()
    active_session = SessionHistory.objects.filter(
        doctor=doctor,
        date=current_date,
        is_active=True
    ).first()

    current_patient = None
    if active_session:
        current_patient = active_session.current_patient

    if request.method == 'POST':
        if 'prescription' in request.POST:
            patient_id = request.POST.get('patient_id')
            prescription_image_data = request.POST.get('prescription_image')
            if patient_id and prescription_image_data:
                appointment = get_object_or_404(Appointment, id=patient_id)
                format, imgstr = prescription_image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(base64.b64decode(imgstr), name=f'prescription_{uuid.uuid4()}.{ext}')
                MedicalRecord.objects.create(
                    patient_name=appointment.patient_name,
                    doctor=request.user,
                    record_type='Prescription',
                    data='',
                    prescription_image=image_file
                )
                appointment.status = 'Completed'
                appointment.save()
                messages.success(request, "Prescription saved successfully!")
                return redirect('doctor_dashboard')
        elif 'lab_request' in request.POST:
            patient_id = request.POST.get('patient_id')
            lab_requests = request.POST.getlist('lab_requests[]')
            if patient_id and lab_requests:
                appointment = get_object_or_404(Appointment, id=patient_id)
                # Add new tests to LabTest model if they don't exist
                for test_name in lab_requests:
                    if not LabTest.objects.filter(name=test_name).exists():
                        LabTest.objects.create(name=test_name)
                # Create or get Patient instance
                patient, created = Patient.objects.get_or_create(
                    email=appointment.patient_email,
                    defaults={'name': appointment.patient_name, 'phone': appointment.patient_contact}
                )
                # Create LabReport with status "Pending"
                lab_report = LabReport.objects.create(
                    patient=patient,
                    tests=json.dumps(lab_requests),
                    status='Pending'
                )
                # Create MedicalRecord and link to LabReport
                MedicalRecord.objects.create(
                    patient_name=appointment.patient_name,
                    doctor=request.user,
                    record_type='LabRequest',
                    data=json.dumps(lab_requests),
                    lab_report=lab_report
                )
                appointment.status = 'Completed'
                appointment.save()
                messages.success(request, "Lab request saved successfully!")
                return redirect('doctor_dashboard')
        else:
            messages.error(request, "Invalid form submission.")

    return render(request, 'users/doctor_dashboard.html', {
        'doctor': doctor,
        'current_date': current_date,
        'active_session': active_session,
        'current_patient': current_patient
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