from django.db import migrations

def add_initial_lab_tests(apps, schema_editor):
    LabTest = apps.get_model('lab_report', 'LabTest')
    initial_tests = [
        'Blood Test',
        'Urine Test',
        'X-Ray',
        'MRI Scan',
        'CT Scan',
        'ECG',
        'Ultrasound',
        'Lipid Profile',
        'Liver Function Test',
        'Kidney Function Test',
    ]
    for test_name in initial_tests:
        LabTest.objects.create(name=test_name)

class Migration(migrations.Migration):
    dependencies = [
        ('lab_report', '0002_labreport_status_tests'),  # Adjust based on your last migration
    ]

    operations = [
        migrations.RunPython(add_initial_lab_tests),
    ]