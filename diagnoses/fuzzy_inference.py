import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from .models import DiseaseGroup, GroupSymptom, Symptom, VitalSigns

class FuzzyDiseaseGroupDiagnosis:
    def __init__(self):
        self.disease_groups = DiseaseGroup.objects.all()
        self.variables = {}
        self.define_variables()

    def define_variables(self):
        # Definir variables lingüísticas para síntomas y signos vitales
        all_symptoms = Symptom.objects.all()

        # Definir variables para síntomas
        for symptom in all_symptoms:
            symptom_name = symptom.name.lower().replace(" ", "_")  # Normalizar a minúsculas y usar _
            self.variables[symptom_name] = ctrl.Antecedent(np.arange(0, 11, 1), symptom_name)
            self.variables[symptom_name]['low'] = fuzz.trimf(self.variables[symptom_name].universe, [0, 0, 5])
            self.variables[symptom_name]['medium'] = fuzz.trimf(self.variables[symptom_name].universe, [2, 5, 8])
            self.variables[symptom_name]['high'] = fuzz.trimf(self.variables[symptom_name].universe, [5, 10, 10])

        # Definir variables para signos vitales con nombres consistentes
        self.variables['blood_pressure'] = ctrl.Antecedent(np.arange(80, 181, 1), 'blood_pressure')
        self.variables['blood_pressure']['low'] = fuzz.trimf(self.variables['blood_pressure'].universe, [80, 80, 120])
        self.variables['blood_pressure']['normal'] = fuzz.trimf(self.variables['blood_pressure'].universe, [110, 120, 140])
        self.variables['blood_pressure']['high'] = fuzz.trimf(self.variables['blood_pressure'].universe, [130, 180, 180])

        self.variables['heart_rate'] = ctrl.Antecedent(np.arange(60, 161, 1), 'heart_rate')
        self.variables['heart_rate']['low'] = fuzz.trimf(self.variables['heart_rate'].universe, [60, 60, 80])
        self.variables['heart_rate']['normal'] = fuzz.trimf(self.variables['heart_rate'].universe, [70, 85, 100])
        self.variables['heart_rate']['high'] = fuzz.trimf(self.variables['heart_rate'].universe, [90, 160, 160])

        self.variables['temperature'] = ctrl.Antecedent(np.arange(35, 41, 0.1), 'temperature')
        self.variables['temperature']['low'] = fuzz.trimf(self.variables['temperature'].universe, [35, 35, 36.5])
        self.variables['temperature']['normal'] = fuzz.trimf(self.variables['temperature'].universe, [36, 37, 37.5])
        self.variables['temperature']['high'] = fuzz.trimf(self.variables['temperature'].universe, [37, 40, 40])

        # Definir variable para frecuencia respiratoria (respiratory_rate)
        self.variables['respiratory_rate'] = ctrl.Antecedent(np.arange(10, 31, 1), 'respiratory_rate')
        self.variables['respiratory_rate']['low'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [10, 10, 16])
        self.variables['respiratory_rate']['normal'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [12, 16, 20])
        self.variables['respiratory_rate']['high'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [18, 30, 30])

        # Definir variable para peso (weight)
        self.variables['weight'] = ctrl.Antecedent(np.arange(30, 151, 1), 'weight')
        self.variables['weight']['low'] = fuzz.trimf(self.variables['weight'].universe, [30, 30, 60])
        self.variables['weight']['normal'] = fuzz.trimf(self.variables['weight'].universe, [50, 75, 100])
        self.variables['weight']['high'] = fuzz.trimf(self.variables['weight'].universe, [90, 150, 150])

    def create_system_for_group(self, group):
        rules = []

        # Variable de salida: probabilidad de pertenencia al grupo (definida localmente aquí)
        probability = ctrl.Consequent(np.arange(0, 101, 1), 'probability')
        probability['low'] = fuzz.trimf(probability.universe, [0, 0, 50])
        probability['medium'] = fuzz.trimf(probability.universe, [25, 50, 75])
        probability['high'] = fuzz.trimf(probability.universe, [50, 100, 100])

        # Obtener los síntomas relevantes para el grupo de enfermedades
        group_symptoms = GroupSymptom.objects.filter(disease_group=group)

        # Definir reglas específicas para cada grupo de enfermedades
        for gs in group_symptoms:
            symptom_name = gs.symptom.name.lower().replace(" ", "_")  # Normalizar a minúsculas y _
            intensity = 'high' if gs.severity_level == 3 else 'medium' if gs.severity_level == 2 else 'low'
            rule = ctrl.Rule(self.variables[symptom_name][intensity], probability['high'])
            rules.append(rule)

        # Crear el sistema de control para el grupo
        system_ctrl = ctrl.ControlSystem(rules)
        system = ctrl.ControlSystemSimulation(system_ctrl)
        system.output_variable = probability  # Guardar la referencia de probabilidad para acceder en diagnose
        return system

    def diagnose(self, inputs):
        results = []

        for group in self.disease_groups:
            system = self.create_system_for_group(group)

            # Asignar entradas
            for key, value in inputs.items():
                normalized_key = key.lower().replace(" ", "_")
                if normalized_key in self.variables:
                    try:
                        system.input[normalized_key] = value
                    except ValueError:
                        continue  # Ignorar errores en la asignación sin mostrar mensajes
                else:
                    continue  # Ignorar variables desconocidas sin mensajes

            # Calcular probabilidad y obtener el resultado de salida
            system.compute()
            probability = system.output.get(system.output_variable.label)
            if probability is not None:
                results.append({
                    'group': group.name,
                    'probability': probability
                })

        return results
