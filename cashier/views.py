from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PharmacyBill
from lab_report.models import Patient
import json

@login_required
def cashier_dashboard(request):
    if request.user.role != 'cashier':
        return redirect('user_dashboard')  # Redirect unauthorized users
    patients = Patient.objects.all()
    bills = PharmacyBill.objects.all()
    return render(request, 'cashier/cashier_dashboard.html', {'patients': patients, 'bills': bills})

@csrf_exempt
@login_required
def add_pharmacy_bill(request):
    if request.user.role != 'cashier':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        bill_data = data.get('bill_data')
        try:
            patient = Patient.objects.get(id=patient_id)
            PharmacyBill.objects.create(patient=patient, bill_data=bill_data)
            return JsonResponse({'message': 'Pharmacy bill added successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)