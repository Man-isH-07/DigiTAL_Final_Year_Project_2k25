from django.db import models

class SymptomMapping(models.Model):
    symptom = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.symptom} -> {self.condition} ({self.specialization})"