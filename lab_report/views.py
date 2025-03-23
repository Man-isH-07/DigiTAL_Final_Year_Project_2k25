from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Patient, LabReport
import json

@login_required
def lab_dashboard(request):
    if request.user.role != 'lab_technician':
        return redirect('user_dashboard')  # Redirect unauthorized users
    patients = Patient.objects.all()
    reports = LabReport.objects.all()
    return render(request, 'lab_report/lab_dashboard.html', {'patients': patients, 'reports': reports})

@csrf_exempt
@login_required
def add_lab_report(request):
    if request.user.role != 'lab_technician':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        report_data = data.get('report_data')
        try:
            patient = Patient.objects.get(id=patient_id)
            LabReport.objects.create(patient=patient, report_data=report_data)
            return JsonResponse({'message': 'Lab report added successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)