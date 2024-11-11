from rest_framework import serializers
from .models import Symptom, VitalSigns, Disease, DiseaseGroup, GroupSymptom, Diagnosis, DiagnosisSymptom, DiagnosisGroupProbability

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'

class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = '__all__'

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'

class DiseaseGroupSerializer(serializers.ModelSerializer):
    cie_codes = DiseaseSerializer(many=True, read_only=True)

    class Meta:
        model = DiseaseGroup
        fields = ['id', 'name', 'cie_codes']

class GroupSymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSymptom
        fields = '__all__'

class DiagnosisSymptomSerializer(serializers.ModelSerializer):
    symptom_name = serializers.CharField(source='symptom.name')  # Obtenemos el nombre del síntoma desde el modelo Symptom

    class Meta:
        model = DiagnosisSymptom
        fields = ['symptom_name', 'intensity']  # Incluye 'intensity' desde DiagnosisSymptom

class DiagnosisGroupProbabilitySerializer(serializers.ModelSerializer):
    disease_group = DiseaseGroupSerializer(read_only=True)

    class Meta:
        model = DiagnosisGroupProbability
        fields = ['disease_group', 'probability_level']

class DiagnosisSerializer(serializers.ModelSerializer):
    symptoms = DiagnosisSymptomSerializer(many=True, source='diagnosissymptom_set', read_only=True)  # Acceso a través de la relación `diagnosissymptom_set`
    vital_signs = VitalSignsSerializer()
    groups = DiagnosisGroupProbabilitySerializer(many=True, source='diagnosisgroupprobability_set', read_only=True)  # Acceso a través de la relación `diagnosisgroupprobability_set`

    class Meta:
        model = Diagnosis
        fields = ['id', 'symptoms', 'vital_signs', 'groups', 'created_at']
