from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import MedicalRecord

@login_required
def patient_reports(request):
    reports = MedicalRecord.objects.filter(user=request.user)
    return render(request, 'medical_records/patient_reports.html', {'reports': reports})
