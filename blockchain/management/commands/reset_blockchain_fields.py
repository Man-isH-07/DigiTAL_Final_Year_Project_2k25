from django.core.management.base import BaseCommand
from blockchain.models import BlockchainRecord
from medical_records.models import MedicalRecord
from lab_report.models import LabReport

class Command(BaseCommand):
    help = 'Resets blockchain-related fields in the database without flushing all data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-records',
            action='store_true',
            help='Delete all BlockchainRecord entries instead of resetting their fields'
        )

    def handle(self, *args, **options):
        # Option to delete BlockchainRecord entries
        if options['delete_records']:
            blockchain_records_count = BlockchainRecord.objects.count()
            BlockchainRecord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {blockchain_records_count} BlockchainRecord entries'
            ))
        else:
            # Reset record_id and transaction_hash in BlockchainRecord
            blockchain_records = BlockchainRecord.objects.all()
            for record in blockchain_records:
                record.record_id = None
                record.transaction_hash = None
                record.save()
            self.stdout.write(self.style.SUCCESS(
                f'Reset blockchain fields for {blockchain_records.count()} BlockchainRecord entries'
            ))

        # Reset blockchain_record_id and transaction_hash in MedicalRecord
        medical_records = MedicalRecord.objects.all()
        for record in medical_records:
            record.blockchain_record_id = None
            record.transaction_hash = None
            record.save()
        self.stdout.write(self.style.SUCCESS(
            f'Reset blockchain fields for {medical_records.count()} MedicalRecord entries'
        ))

        # Reset blockchain_record_id and transaction_hash in LabReport
        lab_reports = LabReport.objects.all()
        for report in lab_reports:
            report.blockchain_record_id = None
            report.transaction_hash = None
            report.save()
        self.stdout.write(self.style.SUCCESS(
            f'Reset blockchain fields for {lab_reports.count()} LabReport entries'
        ))