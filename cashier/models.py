from django.db import models
from lab_report.models import Patient  # Reusing Patient from lab_report

class PharmacyBill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    bill_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pharmacy Bill for {self.patient.name} - {self.created_at}"