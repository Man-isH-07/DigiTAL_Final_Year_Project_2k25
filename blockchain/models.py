# blockchain/models.py
from django.db import models

class BlockchainRecord(models.Model):
    record_id = models.PositiveIntegerField()
    transaction_hash = models.CharField(max_length=66)
    data_hash = models.CharField(max_length=64)
    record_type = models.CharField(max_length=20)
    patient_email = models.EmailField()
    doctor_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.record_type} - {self.record_id}"