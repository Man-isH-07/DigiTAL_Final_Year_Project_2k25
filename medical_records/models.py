# medical_records/models.py
from django.db import models
from users.models import CustomUser
from lab_report.models import LabReport
import json

class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('Prescription', 'Prescription'),
        ('LabRequest', 'Lab Request'),
    ]

    patient_name = models.CharField(max_length=255)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    data = models.TextField()
    prescription_image = models.ImageField(upload_to='prescriptions/', null=True, blank=True)
    lab_report = models.ForeignKey(LabReport, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    blockchain_record_id = models.PositiveIntegerField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=66, null=True, blank=True)

    def __str__(self):
        return f"{self.record_type} for {self.patient_name} by Dr. {self.doctor.username} on {self.created_at}"

    def get_lab_tests(self):
        if self.record_type == 'LabRequest' and self.data:
            return json.loads(self.data)
        return []