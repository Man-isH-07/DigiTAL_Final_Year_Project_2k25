from django.db import models

# Create your models here.
from django.db import models
from users.models import CustomUser

class MedicalRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    report = models.FileField(upload_to='reports/')
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.description}"
