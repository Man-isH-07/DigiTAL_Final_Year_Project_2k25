import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_dir)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fyp.settings")  # Updated to match your project name
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from ai_assistant.models import SymptomMapping
from django.db.models import Count

def remove_duplicates():
    print("Starting duplicate removal process...")

    # Step 1: Normalize symptom field to lowercase
    print("Normalizing symptom fields to lowercase...")
    for mapping in SymptomMapping.objects.all():
        if mapping.symptom != mapping.symptom.lower():
            mapping.symptom = mapping.symptom.lower()
            mapping.save()
            print(f"Normalized: {mapping.symptom} -> {mapping.condition} (Dr. {mapping.doctor.name})")

    # Step 2: Identify duplicates based on symptom (lowercase), condition, and doctor
    print("Identifying duplicates...")
    duplicates = (SymptomMapping.objects.values('symptom', 'condition', 'doctor')
                  .annotate(count=Count('id'))
                  .filter(count__gt=1))

    # Step 3: Keep the first occurrence and delete the rest
    total_deleted = 0
    for duplicate in duplicates:
        instances = SymptomMapping.objects.filter(
            symptom=duplicate['symptom'],
            condition=duplicate['condition'],
            doctor=duplicate['doctor']
        ).order_by('id')

        instance_to_keep = instances.first()
        if instance_to_keep:
            instances_to_delete = SymptomMapping.objects.filter(
                symptom=duplicate['symptom'],
                condition=duplicate['condition'],
                doctor=duplicate['doctor']
            ).exclude(id=instance_to_keep.id)

            deleted_count, _ = instances_to_delete.delete()
            total_deleted += deleted_count
            if deleted_count > 0:
                print(f"Deleted {deleted_count} duplicate(s) for symptom: {duplicate['symptom']}, condition: {duplicate['condition']}, doctor: {duplicate['doctor']} (Kept ID: {instance_to_keep.id})")

    # Step 4: Verify the result
    print(f"Total duplicates deleted: {total_deleted}")
    print("Remaining SymptomMapping entries:")
    for mapping in SymptomMapping.objects.all():
        print(f"{mapping}")

if __name__ == "__main__":
    remove_duplicates()