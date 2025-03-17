from django import forms
from .models import Appointment

class ManualBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'user', 'doctor', 'date', 'time', 'patient_name',
            'patient_age', 'patient_contact', 'patient_email',
            'gender', 'blood_group', 'symptoms', 'photo', 'status'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

