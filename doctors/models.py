from django.db import models
from django.conf import settings

class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='doctor_profile',
    )
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    image = models.ImageField(upload_to='doctors/', null=True)
    available_slots = models.TextField(help_text="Comma-separated available slots (e.g., 09:00,15:00,19:00)")
    temp_slot_adjustment = models.IntegerField(default=0, help_text="Temporary hours added to slots (e.g., 1 or 2 hours)")

    def __str__(self):
        return self.name

    def get_adjusted_slots(self, date):
        """Return slots adjusted by temp_slot_adjustment for a specific date."""
        if self.temp_slot_adjustment:
            from datetime import time
            slots = self.available_slots.split(',')
            adjusted_slots = []
            for slot in slots:
                hour, minute = map(int, slot.split(':'))
                hour += self.temp_slot_adjustment
                if hour >= 24:
                    hour -= 24  # Handle overflow (e.g., 23:00 + 2 = 01:00 next day)
                adjusted_slots.append(f"{hour:02d}:{minute:02d}")
            return adjusted_slots
        return self.available_slots.split(',')