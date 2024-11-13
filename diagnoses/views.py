from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Diagnosis, VitalSigns, DiseaseGroup, Symptom, DiagnosisSymptom, DiagnosisGroupProbability
from .serializers import DiagnosisSerializer, VitalSignsSerializer
from .fuzzy_inference import FuzzyDiseaseGroupDiagnosis  # Cambiado para el nuevo sistema

class DiagnosesListCreateView(generics.ListCreateAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

    def create(self, request, *args, **kwargs):
        vital_signs_data = request.data.get('vital_signs')
        symptoms_data = request.data.get('symptoms')

        # Crear signos vitales
        vital_signs_serializer = VitalSignsSerializer(data=vital_signs_data)
        if vital_signs_serializer.is_valid():
            vital_signs = vital_signs_serializer.save()
        else:
            return Response(vital_signs_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Crear diagnóstico sin grupos de enfermedades por ahora
        diagnosis = Diagnosis.objects.create(vital_signs=vital_signs)

        # Inicializar intensidades de síntomas
        symptom_intensities = {}

        # Obtener todos los síntomas de la base de datos
        all_symptoms = Symptom.objects.all()

        # Establecer intensidad de 0 para todos los síntomas, si no están en la solicitud
        for symptom in all_symptoms:
            symptom_name_normalized = symptom.name.lower().replace(" ", "_")
            symptom_intensities[symptom_name_normalized] = 0  # Intensidad por defecto

        # Actualizar las intensidades para los síntomas presentes en la solicitud
        for symptom_data in symptoms_data:
            symptom = Symptom.objects.get(id=symptom_data['symptom_id'])
            normalized_name = symptom.name.lower().replace(" ", "_")
            DiagnosisSymptom.objects.create(diagnosis=diagnosis, symptom=symptom, intensity=symptom_data['intensity'])
            symptom_intensities[normalized_name] = symptom_data['intensity']  # Usar la intensidad proporcionada

        # Usar FuzzyDiseaseGroupDiagnosis para obtener probabilidades por grupo de enfermedades
        fuzzy_system = FuzzyDiseaseGroupDiagnosis()
        inputs = {
            'blood_pressure': vital_signs_data['blood_pressure'],
            'heart_rate': vital_signs_data['heart_rate'],
            'respiratory_rate': vital_signs_data['respiratory_rate'],
            'temperature': vital_signs_data['temperature'],
            'weight': vital_signs_data['weight'],
            **symptom_intensities  # Agregar todos los síntomas con su intensidad
        }
        group_probabilities = fuzzy_system.diagnose(inputs)

        # Asignar probabilidades calculadas a cada grupo de enfermedades
        for group_prob in group_probabilities:
            group = DiseaseGroup.objects.get(name=group_prob['group'])
            DiagnosisGroupProbability.objects.create(
                diagnosis=diagnosis,
                disease_group=group,
                probability_level=group_prob['probability']
            )

        serializer = DiagnosisSerializer(diagnosis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DiagnosisDetailView(generics.RetrieveAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer