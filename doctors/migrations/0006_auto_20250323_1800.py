from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_users_for_doctors(apps, schema_editor):
    Doctor = apps.get_model('doctors', 'Doctor')
    CustomUser = apps.get_model('users', 'CustomUser')
    for doctor in Doctor.objects.all():
        if not doctor.user:  # Only create a user if not already linked
            username = doctor.name.lower().replace(' ', '_')
            email = f"{username}@hos.com"
            user = CustomUser.objects.create(
                username=username,
                email=email,
                password=make_password('1234'),
                role='doctor',
                first_name=doctor.name.split()[0],
                last_name=' '.join(doctor.name.split()[1:])
            )
            doctor.user = user
            doctor.save()

class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0005_doctor_user'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_users_for_doctors),
    ]