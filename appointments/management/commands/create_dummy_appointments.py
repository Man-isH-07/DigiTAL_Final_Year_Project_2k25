from django.core.management.base import BaseCommand
from datetime import datetime, time
from appointments.models import Appointment
from doctors.models import Doctor
import random
from faker import Faker

# python manage.py create_dummy_appointments 1 2025-03-02 12:00 --count=5

class Command(BaseCommand):
    help = 'Creates dummy appointments for a specific doctor, date, and slot time'

    def add_arguments(self, parser):
        parser.add_argument('doctor_id', type=int, help='ID of the doctor')
        parser.add_argument('date', type=str, help='Date in YYYY-MM-DD format')
        parser.add_argument('slot', type=str, help='Time slot in HH:MM format (e.g., 12:00)')
        parser.add_argument('--count', type=int, default=5, help='Number of dummy appointments to create')

    def handle(self, *args, **options):
        doctor_id = options['doctor_id']
        date_str = options['date']
        slot = options['slot']
        count = options['count']

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            doctor = Doctor.objects.get(id=doctor_id)
            available_slots = doctor.available_slots.split(',')
            if slot not in available_slots:
                raise ValueError(f"Slot {slot} is not available for Dr. {doctor.name}")
            slot_time = datetime.strptime(slot, "%H:%M").time()

            fake = Faker()
            for i in range(count):
                patient_name = fake.name()
                patient_age = random.randint(18, 80)
                patient_contact = fake.phone_number()[:15]
                patient_email = fake.email()
                gender = random.choice(['Male', 'Female', 'Other'])
                blood_group = random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-'])
                symptoms = fake.text(max_nb_chars=200)

                appointment = Appointment(
                    user=None,
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
                    queue_position=i + 1,
                )
                appointment.save()

                self.stdout.write(f"Created dummy appointment for {patient_name} with Dr. {doctor.name} on {date} at {slot}")
            
            self.stdout.write(f"Created {count} dummy appointments for Dr. {doctor.name} on {date} at {slot}.")
        except Doctor.DoesNotExist:
            self.stdout.write(f"Error: Doctor with ID {doctor_id} not found.")
        except ValueError as e:
            self.stdout.write(f"Error: {e}")