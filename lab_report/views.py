from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Patient, LabReport, LabTest
import json

@login_required
def lab_dashboard(request):
    if request.user.role != 'lab_technician':
        return redirect('user_dashboard')
    pending_reports = LabReport.objects.filter(status='Pending')
    collected_reports = LabReport.objects.filter(status='Collected')
    completed_reports = LabReport.objects.filter(status='Completed')
    return render(request, 'lab_report/lab_dashboard.html', {
        'pending_reports': pending_reports,
        'collected_reports': collected_reports,
        'completed_reports': completed_reports
    })

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
            LabReport.objects.create(patient=patient, tests=json.dumps([]), status='Completed', report_data=report_data)
            return JsonResponse({'message': 'Lab report added successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def mark_collected(request):
    if request.user.role != 'lab_technician':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        try:
            report = LabReport.objects.get(id=report_id, status='Pending')
            report.status = 'Collected'
            report.save()
            return JsonResponse({'message': 'Sample marked as collected'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def mark_completed(request):
    if request.user.role != 'lab_technician':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        if 'report_data' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        try:
            report = LabReport.objects.get(id=report_id, status='Collected')
            report.report_data = request.FILES['report_data']
            report.status = 'Completed'
            report.save()
            return JsonResponse({'message': 'Lab report marked as completed'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_lab_tests(request):
    query = request.GET.get('q', '')
    lab_tests = LabTest.objects.filter(name__icontains=query).values_list('name', flat=True)[:10]
    return JsonResponse({'tests': list(lab_tests)})