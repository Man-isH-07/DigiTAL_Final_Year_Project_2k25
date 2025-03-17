from datetime import datetime, time
from appointments.models import Appointment
from doctors.models import Doctor
import random
from faker import Faker

# Initialize Faker for generating dummy data
fake = Faker()

# Specify the doctor, date, and slot you want to use for dummy appointments
doctor_id = 1  # Replace with the actual doctor ID (e.g., Dr. John Doe)
date = datetime(2025, 3, 1).date()  # Example date: March 1, 2025
slot = "12:00"  # Example time slot (must match available_slots in Doctor model)

# Get the doctor
try:
    doctor = Doctor.objects.get(id=doctor_id)
    # Verify the slot is in the doctor's available slots
    available_slots = doctor.available_slots.split(',')
    if slot not in available_slots:
        raise ValueError(f"Slot {slot} is not available for Dr. {doctor.name}")
except Doctor.DoesNotExist:
    print(f"Doctor with ID {doctor_id} not found.")
    exit()

# Convert slot to time object
slot_time = datetime.strptime(slot, "%H:%M").time()

# Number of dummy appointments to create (e.g., 5)
num_appointments = 5

for i in range(num_appointments):
    # Generate dummy patient details
    patient_name = fake.name()
    patient_age = random.randint(18, 80)
    patient_contact = fake.phone_number()[:15]  # Limit to 15 chars as per model
    patient_email = fake.email()
    gender = random.choice(['Male', 'Female', 'Other'])
    blood_group = random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-'])
    symptoms = fake.text(max_nb_chars=200)  # Limit to reasonable length for symptoms

    # Create the appointment
    appointment = Appointment(
        user=None,  # Set to None for desk bookings or a specific user if needed
        doctor=doctor,
        date=date,
        time=slot_time,
        patient_name=patient_name,
        patient_age=patient_age,
        patient_contact=patient_contact,
        patient_email=patient_email,
        gender=gender,
        blood_group=blood_group,
        symptoms=symptoms,
        status='Pending',
        queue_position=i + 1,  # Assign sequential queue positions
        extra_time=0  # Default extra time
    )
    appointment.save()

    print(f"Created dummy appointment for {patient_name} with Dr. {doctor.name} on {date} at {slot}")

print(f"Created {num_appointments} dummy appointments for Dr. {doctor.name} on {date} at {slot}.")