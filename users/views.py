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
        print("POST request received")  

        
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        print(f"Username: {username}, Email: {email}, Role: {role}")

        if not username or not email or not role or not password1 or not password2:
            errors.append("All fields are required.")
        if password1 != password2:
            errors.append("Passwords do not match.")
        if CustomUser.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        if CustomUser.objects.filter(email=email).exists():
            errors.append("Email already exists.")
        if role not in ['admin', 'doctor', 'desk', 'user']:
            errors.append("Invalid role selected.")

        if not errors:
            print("No validation errors, creating user")
            user = CustomUser.objects.create(
                username=username,
                email=email,
                role=role,
                password=make_password(password1)
            )
            print(f"User created successfully: {user}")
            return redirect('admin_dashboard')
        else:
            print(f"Validation errors: {errors}")

    users = CustomUser.objects.all()
    return render(request, 'users/admin_dashboard.html', {
        'errors': errors,
        'users': users
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


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from doctors.models import Doctor
from datetime import datetime

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
                message="Your appointment has been successfully booked with DigiTAL."
            )

            messages.success(request, "Appointment booked successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('desk_dashboard')

    doctors = Doctor.objects.all()

    return render(request, 'users/desk_dashboard.html', {
        'doctors': doctors,
    })

@login_required
@role_required('doctor')
def doctor_dashboard(request):
    return render(request, 'users/doctor_dashboard.html')


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
        if role not in ['admin', 'doctor', 'desk', 'user']:
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


