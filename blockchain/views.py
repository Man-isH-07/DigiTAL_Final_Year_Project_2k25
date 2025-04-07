# blockchain/views.py
from django.shortcuts import render
from .models import BlockchainRecord
from .utils import get_record_from_blockchain
from datetime import datetime

def blockchain_dashboard(request):
    records = BlockchainRecord.objects.all().order_by('-record_id')  # New to old
    blockchain_data = []
    for record in records:
        try:
            bc_data = get_record_from_blockchain(record.record_id)
            blockchain_data.append({
                'record_id': record.record_id,
                'transaction_hash': record.transaction_hash,
                'data_hash': bc_data['data_hash'],
                'record_type': bc_data['record_type'],
                'patient_email': bc_data['patient_email'],
                'timestamp': record.timestamp.strftime('%B %d, %Y, %I:%M %p'),
            })
        except Exception as e:
            print(f"Error retrieving record {record.record_id}: {e}")
    return render(request, 'blockchain/dashboard.html', {'records': blockchain_data})