from django.db import models
from doctors.models import Doctor

class SymptomMapping(models.Model):
    symptom = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for existing data

    def __str__(self):
        if self.doctor:
            return f"{self.symptom} -> {self.condition} ({self.doctor.name})"
        return f"{self.symptom} -> {self.condition} (No doctor assigned)"