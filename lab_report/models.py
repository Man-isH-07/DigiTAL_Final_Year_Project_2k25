# lab_report/models.py
from django.db import models
from django.conf import settings
import json

class Patient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class LabTest(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class LabReport(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Collected', 'Collected'),
        ('Completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_reports', null=True)
    tests = models.TextField()
    report_data = models.FileField(upload_to='lab_reports/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blockchain_record_id = models.PositiveIntegerField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=66, null=True, blank=True)

    def __str__(self):
        return f"Lab Report for {self.patient.name} - {self.created_at}"

    def get_tests(self):
        if self.tests:
            return json.loads(self.tests)
        return []