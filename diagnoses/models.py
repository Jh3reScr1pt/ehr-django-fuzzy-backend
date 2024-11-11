from django.db import models

# Modelo de síntomas generales
class Symptom(models.Model):
    name = models.CharField(max_length=100)  # Nombre del síntoma, por ejemplo, "Dolor de cabeza"
    description = models.TextField(null=True, blank=True)  # Descripción opcional del síntoma

    def __str__(self):
        return self.name

# Modelo de signos vitales objetivos
class VitalSigns(models.Model):
    blood_pressure = models.CharField(max_length=20)  # Presión arterial, por ejemplo, '120/80'
    heart_rate = models.IntegerField()  # Frecuencia cardíaca en bpm
    respiratory_rate = models.IntegerField()  # Frecuencia respiratoria en respiraciones por minuto
    temperature = models.FloatField()  # Temperatura en grados Celsius
    weight = models.FloatField()  # Peso en kilogramos

    def __str__(self):
        return f"BP: {self.blood_pressure}, HR: {self.heart_rate}"

# Modelo para enfermedades con código CIE-10
class Disease(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la enfermedad, por ejemplo, "Neumonía"
    cie_code = models.CharField(max_length=10, unique=True)  # Código CIE-10 de la enfermedad

    def __str__(self):
        return f"{self.name} ({self.cie_code})"

# Modelo de grupo de enfermedades (Ej: IRA, Enfermedades Gastrointestinales)
class DiseaseGroup(models.Model):
    name = models.CharField(max_length=100)  # Nombre del grupo de enfermedades, como "IRA"
    cie_codes = models.ManyToManyField(Disease)  # Enlace a varias enfermedades con sus códigos CIE-10

    def __str__(self):
        return self.name

# Modelo de síntomas específicos relacionados con grupos de enfermedades
class GroupSymptom(models.Model):
    disease_group = models.ForeignKey(DiseaseGroup, on_delete=models.CASCADE)  # Grupo de enfermedad
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)  # Síntoma específico relacionado
    severity_level = models.IntegerField()  # Nivel de intensidad del síntoma, de 0 a 3

    def __str__(self):
        return f"{self.symptom.name} - {self.disease_group.name} - Severity: {self.severity_level}"

# Modelo de diagnóstico presuntivo
class Diagnosis(models.Model):
    symptoms = models.ManyToManyField(Symptom, through='DiagnosisSymptom')  # Relación con síntomas y su intensidad
    vital_signs = models.OneToOneField(VitalSigns, on_delete=models.CASCADE)  # Relación uno-a-uno con los signos vitales
    groups = models.ManyToManyField(DiseaseGroup, through='DiagnosisGroupProbability')  # Grupos de enfermedades con probabilidades
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha del diagnóstico

    def __str__(self):
        return f"Diagnosis on {self.created_at}"

# Tabla intermedia para síntomas específicos en el diagnóstico, con nivel de intensidad
class DiagnosisSymptom(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    intensity = models.IntegerField()  # Nivel de intensidad del síntoma (0-3)

    def __str__(self):
        return f"{self.symptom.name} - Intensity: {self.intensity}"

# Tabla intermedia para almacenar el nivel de probabilidad de cada grupo en el diagnóstico
class DiagnosisGroupProbability(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    disease_group = models.ForeignKey(DiseaseGroup, on_delete=models.CASCADE)
    probability_level = models.FloatField()  # Nivel de probabilidad específico para este diagnóstico y grupo

    def __str__(self):
        return f"{self.disease_group.name} - Probability: {self.probability_level}"
