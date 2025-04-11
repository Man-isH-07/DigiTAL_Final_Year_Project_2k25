# lab_report/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, LabReport, LabTest
import json
import hashlib
from blockchain.utils import add_record_to_blockchain
from blockchain.models import BlockchainRecord
from django.views.decorators.csrf import csrf_exempt

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

@login_required
@role_required('lab_technician')
def lab_dashboard(request):
    pending_reports = LabReport.objects.filter(status='Pending')
    collected_reports = LabReport.objects.filter(status='Collected')
    completed_reports = LabReport.objects.filter(status='Completed').order_by('-created_at')

    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        report = get_object_or_404(LabReport, id=report_id)

        if 'collect' in request.POST:
            report.status = 'Collected'
            report.save()
            messages.success(request, "Lab report marked as collected.")
        elif 'complete' in request.POST:
            report_file = request.FILES.get('report_file')
            if report_file:
                report.report_data = report_file
                report.status = 'Completed'
                report.save()

                data_hash = hashlib.sha256()
                for chunk in report_file.chunks():
                    data_hash.update(chunk)
                data_hash = data_hash.hexdigest()

                doctor_id = report.doctor.id

                try:
                    record_id, tx_hash = add_record_to_blockchain(
                        data_hash=data_hash,
                        record_type='LabReport',
                        patient_email=report.patient.email,
                        doctor_id=doctor_id
                    )

                    report.blockchain_record_id = record_id
                    report.transaction_hash = tx_hash
                    report.save()

                    BlockchainRecord.objects.create(
                        record_id=record_id,
                        transaction_hash=tx_hash,
                        data_hash=data_hash,
                        record_type='LabReport',
                        patient_email=report.patient.email,
                        doctor_id=doctor_id
                    )

                    messages.success(request, "Lab report completed, file uploaded, and stored on blockchain.")
                except Exception as e:
                    messages.error(request, f"Lab report completed, but failed to store on blockchain: {str(e)}")
            else:
                messages.error(request, "Please upload a report file to complete the lab report.")

        return redirect('lab_dashboard')

    return render(request, 'lab_report/lab_dashboard.html', {
        'pending_reports': pending_reports,
        'collected_reports': collected_reports,
        'completed_reports': completed_reports,
    })

@csrf_exempt
@login_required
@role_required('lab_technician')
def add_lab_report(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        report_data = data.get('report_data')
        try:
            patient = Patient.objects.get(id=patient_id)
            lab_report = LabReport.objects.create(
                patient=patient,
                tests=json.dumps([]),
                status='Completed',
                report_data=report_data
            )

            data_hash = hashlib.sha256(report_data.encode()).hexdigest()
            doctor_id = 0

            record_id, tx_hash = add_record_to_blockchain(
                data_hash=data_hash,
                record_type='LabReport',
                patient_email=patient.email,
                doctor_id=doctor_id
            )

            lab_report.blockchain_record_id = record_id
            lab_report.transaction_hash = tx_hash
            lab_report.save()

            BlockchainRecord.objects.create(
                record_id=record_id,
                transaction_hash=tx_hash,
                data_hash=data_hash,
                record_type='LabReport',
                patient_email=patient.email,
                doctor_id=doctor_id
            )

            return JsonResponse({'message': 'Lab report added successfully and stored on blockchain'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
@role_required('lab_technician')
def mark_collected(request):
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
@role_required('lab_technician')
def mark_completed(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        if 'report_data' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        try:
            report = LabReport.objects.get(id=report_id, status='Collected')
            report.report_data = request.FILES['report_data']
            report.status = 'Completed'
            report.save()

            data_hash = hashlib.sha256()
            for chunk in report.report_data.chunks():
                data_hash.update(chunk)
            data_hash = data_hash.hexdigest()

            doctor_id = report.doctor.id

            record_id, tx_hash = add_record_to_blockchain(
                data_hash=data_hash,
                record_type='LabReport',
                patient_email=report.patient.email,
                doctor_id=doctor_id
            )

            report.blockchain_record_id = record_id
            report.transaction_hash = tx_hash
            report.save()

            BlockchainRecord.objects.create(
                record_id=record_id,
                transaction_hash=tx_hash,
                data_hash=data_hash,
                record_type='LabReport',
                patient_email=report.patient.email,
                doctor_id=doctor_id
            )

            return JsonResponse({'message': 'Lab report marked as completed and stored on blockchain'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_lab_tests(request):
    query = request.GET.get('q', '')
    lab_tests = LabTest.objects.filter(name__icontains=query).values_list('name', flat=True)[:10]
    return JsonResponse({'tests': list(lab_tests)})