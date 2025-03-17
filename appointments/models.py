from django.db import models
from users.models import CustomUser
from doctors.models import Doctor
from django.db.models import Sum
from datetime import datetime

class Appointment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Optional for desk bookings
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20, 
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Treated', 'Treated'),
            ('Skipped', 'Skipped')
        ],
        default='Pending'
    )
    # Patient details
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    patient_age = models.PositiveIntegerField(blank=True, null=True)
    patient_contact = models.CharField(max_length=15, blank=True, null=True)
    patient_email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    # Queue management fields
    queue_position = models.PositiveIntegerField(default=0)  # Position in queue
    last_email_sent = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last wait time email sent")
    can_update = models.BooleanField(default=False, help_text="True if the appointment can be updated (past due by 2 hours)")

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} ({self.date}, {self.time})"

    def calculate_wait_time(self, session_start_time=None):
        """Calculate wait time in minutes based on queue position and session start time."""
        base_time = 20  # Default 20-minute treatment time
        
        if session_start_time:
            from datetime import datetime, timedelta
            current_time = datetime.now()
            session_duration = (current_time - session_start_time).total_seconds() / 60  # Minutes
            base_wait = max(0, (self.queue_position - 1) * base_time - session_duration)
            return int(base_wait)
        return (self.queue_position - 1) * base_time

    def calculate_live_wait_time(self, session_data=None):
        """Calculate live wait time in minutes based on session data and queue position."""
        if self.status != 'Pending':
            return 0  # No wait time if not pending
        if not session_data or 'doctor_id' not in session_data or 'date' not in session_data or 'slot' not in session_data:
            return self.calculate_wait_time()  # Fall back to static calculation if no session data
        doctor_id = session_data['doctor_id']
        date = datetime.strptime(session_data['date'], '%Y-%m-%d').date()
        slot = session_data['slot']
        doctor = Doctor.objects.get(id=doctor_id)
        if self.doctor != doctor or self.date != date or not self.time.strftime("%H:%M").startswith(slot):
            return self.calculate_wait_time()  # Fall back if appointment doesn’t match session
        appointments = Appointment.objects.filter(
            doctor=doctor, date=date, time__startswith=slot, status='Pending'
        ).order_by('queue_position')
        current_patient_timer = session_data.get('patient_timer', 1200)  # Default to 20 mins (in seconds)
        for appt in appointments:
            if appt.id == self.id:
                base_time = 20 * 60  # Default 20-minute treatment time in seconds
                if appt.queue_position == 1:  # Current patient
                    return max(0, current_patient_timer / 60)  # In minutes
                else:
                    return max(0, (appt.queue_position - 1) * base_time - (1200 - current_patient_timer)) / 60  # In minutes
        return self.calculate_wait_time()  # Fallback if not found

    def can_be_updated(self):
        """Check if the appointment can be updated (past due by 2 hours)."""
        from datetime import datetime, timedelta
        appointment_time = datetime.combine(self.date, self.time)
        current_time = datetime.now()
        time_passed = current_time - appointment_time
        return time_passed > timedelta(hours=2) and self.status == 'Pending'

class SessionHistory(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    slot = models.CharField(max_length=10)  # e.g., "18:00"
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Track if session is currently active
    current_patient = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_session')
    patient_timer = models.PositiveIntegerField(default=1200, help_text="Remaining time in seconds for the current patient")

    def __str__(self):
        return f"Session for Dr. {self.doctor.name} on {self.date} at {self.slot}"