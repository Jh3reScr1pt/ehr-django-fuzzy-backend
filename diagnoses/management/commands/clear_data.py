from django.core.management.base import BaseCommand
from diagnoses.models import Symptom, VitalSigns, Disease, DiseaseGroup, GroupSymptom, Diagnosis, DiagnosisSymptom, DiagnosisGroupProbability

class Command(BaseCommand):
    help = "Clear all data from diagnoses tables"

    def handle(self, *args, **kwargs):
        # Eliminar todos los registros de cada tabla
        Symptom.objects.all().delete()
        VitalSigns.objects.all().delete()
        Disease.objects.all().delete()
        DiseaseGroup.objects.all().delete()
        GroupSymptom.objects.all().delete()
        Diagnosis.objects.all().delete()
        DiagnosisSymptom.objects.all().delete()
        DiagnosisGroupProbability.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all records from diagnoses tables'))
