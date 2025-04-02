from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Patient, LabReport, LabTest
import json
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from django.http import HttpResponseForbidden, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LabReport, LabTest, Patient
from django.core.files.base import ContentFile
import json

@login_required
def lab_dashboard(request):
    if request.user.role != 'lab_technician':
        return HttpResponseForbidden("Only lab technicians can access this page.")

    pending_reports = LabReport.objects.filter(status='Pending')
    collected_reports = LabReport.objects.filter(status='Collected')
    completed_reports = LabReport.objects.filter(status='Completed')

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
                messages.success(request, "Lab report completed and file uploaded.")
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






''' Working
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

'''