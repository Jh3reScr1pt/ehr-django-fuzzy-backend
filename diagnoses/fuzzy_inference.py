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

        for symptom in all_symptoms:
                symptom_name = symptom.name.lower().replace(" ", "_")
                self.variables[symptom_name] = ctrl.Antecedent(np.arange(0, 4, 1), symptom_name)  # Cambiado a rango de 0 a 3
                self.variables[symptom_name]['low'] = fuzz.trimf(self.variables[symptom_name].universe, [0, 0, 1])
                self.variables[symptom_name]['normal'] = fuzz.trimf(self.variables[symptom_name].universe, [1, 2, 3])
                self.variables[symptom_name]['high'] = fuzz.trimf(self.variables[symptom_name].universe, [2, 3, 3])

        # Definir variables para signos vitales
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

        self.variables['respiratory_rate'] = ctrl.Antecedent(np.arange(10, 31, 1), 'respiratory_rate')
        self.variables['respiratory_rate']['low'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [10, 10, 16])
        self.variables['respiratory_rate']['normal'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [12, 16, 20])
        self.variables['respiratory_rate']['high'] = fuzz.trimf(self.variables['respiratory_rate'].universe, [18, 30, 30])

        self.variables['weight'] = ctrl.Antecedent(np.arange(30, 151, 1), 'weight')
        self.variables['weight']['low'] = fuzz.trimf(self.variables['weight'].universe, [30, 30, 60])
        self.variables['weight']['normal'] = fuzz.trimf(self.variables['weight'].universe, [50, 75, 100])
        self.variables['weight']['high'] = fuzz.trimf(self.variables['weight'].universe, [90, 150, 150])

    def create_system_for_group(self, group):
        rules = []
        probability = ctrl.Consequent(np.arange(0, 101, 1), 'probability')
        probability['low'] = fuzz.trimf(probability.universe, [0, 0, 50])
        probability['normal'] = fuzz.trimf(probability.universe, [25, 50, 75])
        probability['high'] = fuzz.trimf(probability.universe, [50, 100, 100])

        # Reglas para el grupo "Infecciones Respiratorias Agudas"
        if group.name == "Infecciones Respiratorias Agudas":
            # Reglas para síntomas respiratorios y fiebre alta
            rules.append(ctrl.Rule(self.variables['congestión_nasal']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_garganta']['high'] | self.variables['dolor_de_garganta']['normal'], probability['high']))
            rules.append(ctrl.Rule(self.variables['estornudos']['high'] & self.variables['congestión_nasal']['high'], probability['high']))
            
            # Combinaciones de fiebre alta con otros síntomas respiratorios severos
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & (self.variables['tos']['high'] | self.variables['dolor_de_garganta']['high']), probability['high']))
            rules.append(ctrl.Rule(self.variables['dificultad_para_respirar']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['respiratory_rate']['high'] & self.variables['fiebre']['high'], probability['high']))

            # Nuevas combinaciones críticas
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['respiratory_rate']['high'] & self.variables['fiebre']['high'] & self.variables['congestión_nasal']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_garganta']['high'] & self.variables['tos']['high'] & self.variables['congestión_nasal']['high'], probability['high']))

            # Combinación crítica de todos los síntomas principales en alto
            rules.append(ctrl.Rule(
                self.variables['congestión_nasal']['high'] &
                self.variables['dolor_de_garganta']['high'] &
                self.variables['estornudos']['high'] &
                self.variables['fiebre']['high'] &
                self.variables['tos']['high'],
                probability['high']
            ))

            # Penalización para fiebre baja junto con otros síntomas de baja intensidad
            rules.append(ctrl.Rule(self.variables['fiebre']['low'] & self.variables['congestión_nasal']['low'], probability['low']))

        # Reglas para el grupo "Enfermedades Gastrointestinales"
        elif group.name == "Enfermedades Gastrointestinales":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['náuseas']['high'] & self.variables['vómitos']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['diarrea']['high'] & self.variables['dolor_abdominal']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['náuseas']['high'] & self.variables['dolor_abdominal']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['vómitos']['high'] & self.variables['diarrea']['high'], probability['high']))

            # Uso de signos vitales con síntomas clave
            rules.append(ctrl.Rule(self.variables['diarrea']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['náuseas']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['vómitos']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_abdominal']['high'] & self.variables['blood_pressure']['low'], probability['high']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['náuseas']['normal'] & self.variables['vómitos']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['diarrea']['normal'] & self.variables['dolor_abdominal']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['náuseas']['normal'] & self.variables['diarrea']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['dolor_abdominal']['normal'] & self.variables['heart_rate']['normal'], probability['normal']))

            # Penalizaciones y probabilidades bajas
            rules.append(ctrl.Rule(self.variables['fiebre']['low'] & self.variables['náuseas']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['diarrea']['low'] & self.variables['dolor_abdominal']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['náuseas']['low'] & self.variables['vómitos']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['low'] & self.variables['diarrea']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['náuseas']['high'] &
                self.variables['vómitos']['high'] &
                self.variables['diarrea']['high'] &
                self.variables['dolor_abdominal']['high'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['náuseas']['high'] &
                self.variables['vómitos']['high'] &
                self.variables['fiebre']['high'] &
                self.variables['heart_rate']['high'],
                probability['high']
            ))

            # Fiebre alta sin presencia de náuseas o vómitos (posible infección no gastrointestinal)
            rules.append(ctrl.Rule(
                self.variables['fiebre']['high'] & ~(self.variables['náuseas']['high'] | self.variables['vómitos']['high']),
                probability['low']
            ))

        # Reglas para el grupo "Enfermedades Infecciosas y Parasitarias"
        elif group.name == "Enfermedades Infecciosas y Parasitarias":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['diarrea']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['pérdida_de_apetito']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['dolor_abdominal']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['diarrea']['high'] & self.variables['fatiga']['high'], probability['high']))
            
            # Uso de signos vitales con síntomas
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['respiratory_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['temperature']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['diarrea']['high'] & self.variables['blood_pressure']['low'], probability['high']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['dolor_abdominal']['normal'] & self.variables['diarrea']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['fiebre']['normal'] & self.variables['pérdida_de_apetito']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['náuseas']['normal'] & self.variables['vómitos']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['fatiga']['normal'] & self.variables['heart_rate']['normal'], probability['normal']))

            # Combinaciones leves y penalizaciones
            rules.append(ctrl.Rule(self.variables['diarrea']['low'] & self.variables['dolor_abdominal']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['fiebre']['low'] & self.variables['náuseas']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['pérdida_de_apetito']['low'] & self.variables['vómitos']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['temperature']['low'] & self.variables['fiebre']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['fiebre']['high'] &
                self.variables['diarrea']['high'] &
                self.variables['dolor_abdominal']['high'] &
                self.variables['fatiga']['high'] &
                self.variables['heart_rate']['high'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['fiebre']['high'] &
                self.variables['vómitos']['high'] &
                self.variables['náuseas']['high'] &
                self.variables['temperature']['high'],
                probability['high']
            ))

        # Reglas para el grupo "Enfermedades del Sistema Nervioso"
        elif group.name == "Enfermedades del Sistema Nervioso":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['high'] & self.variables['mareos']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['high'] & self.variables['fatiga']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['mareos']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['high'] & self.variables['blood_pressure']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['mareos']['high'] & self.variables['blood_pressure']['high'], probability['high']))

            # Uso de signos vitales
            rules.append(ctrl.Rule(self.variables['heart_rate']['high'] & self.variables['dolor_de_cabeza']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['high'] & self.variables['mareos']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['respiratory_rate']['high'] & self.variables['dolor_de_cabeza']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['temperature']['high'] & self.variables['dolor_de_cabeza']['high'], probability['high']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['normal'] & self.variables['mareos']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['normal'] & self.variables['fatiga']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['normal'] & self.variables['mareos']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['heart_rate']['normal'] & self.variables['dolor_de_cabeza']['normal'], probability['normal']))

            # Penalizaciones y probabilidades bajas
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['low'] & self.variables['mareos']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['heart_rate']['low'] & self.variables['dolor_de_cabeza']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['low'] & self.variables['mareos']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['temperature']['low'] & self.variables['dolor_de_cabeza']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['dolor_de_cabeza']['high'] &
                self.variables['mareos']['high'] &
                self.variables['heart_rate']['high'] &
                self.variables['blood_pressure']['high'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['dolor_de_cabeza']['high'] &
                self.variables['fatiga']['high'] &
                self.variables['temperature']['high'] &
                self.variables['respiratory_rate']['high'],
                probability['high']
            ))


        # Reglas para el grupo "Enfermedades del Sistema Urinario"
        elif group.name == "Enfermedades del Sistema Urinario":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['high'] & self.variables['dolor_abdominal']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['high'] & self.variables['fatiga']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['dolor_abdominal']['high'], probability['high']))

            # Uso de signos vitales con síntomas clave
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['high'] & self.variables['blood_pressure']['low'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fiebre']['normal'] & self.variables['blood_pressure']['low'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['fiebre']['high'] & self.variables['respiratory_rate']['high'], probability['high']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['normal'] & self.variables['fiebre']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['normal'] & self.variables['dolor_abdominal']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['normal'] & self.variables['fiebre']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['normal'] & self.variables['fatiga']['normal'], probability['normal']))

            # Penalizaciones y probabilidades bajas
            rules.append(ctrl.Rule(self.variables['dolor_al_orinar']['low'] & self.variables['fiebre']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['low'] & self.variables['fiebre']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['heart_rate']['low'] & self.variables['dolor_abdominal']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['fiebre']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['dolor_al_orinar']['high'] &
                self.variables['fiebre']['high'] &
                self.variables['dolor_abdominal']['high'] &
                self.variables['blood_pressure']['low'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['dolor_al_orinar']['high'] &
                self.variables['fiebre']['high'] &
                self.variables['heart_rate']['high'] &
                self.variables['respiratory_rate']['high'],
                probability['high']
            ))

        # Reglas para el grupo "Enfermedades de la Piel y Tejido Subcutáneo"
        elif group.name == "Enfermedades de la Piel y Tejido Subcutáneo":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['dolor_abdominal']['low'], probability['high']))
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['erupciones_cutáneas']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['fatiga']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['fiebre']['normal'], probability['normal']))

            # Uso de signos vitales con síntomas clave
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['fiebre']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['erupciones_cutáneas']['high'] & self.variables['temperature']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['picazón']['high'] & self.variables['respiratory_rate']['high'], probability['normal']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['picazón']['normal'] & self.variables['erupciones_cutáneas']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['picazón']['normal'] & self.variables['fatiga']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['fiebre']['normal'] & self.variables['erupciones_cutáneas']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['picazón']['normal'] & self.variables['heart_rate']['normal'], probability['normal']))

            # Penalizaciones y probabilidades bajas
            rules.append(ctrl.Rule(self.variables['picazón']['low'] & self.variables['erupciones_cutáneas']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['picazón']['low'] & self.variables['fatiga']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['heart_rate']['low'] & self.variables['picazón']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['fiebre']['low'] & self.variables['erupciones_cutáneas']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['picazón']['high'] &
                self.variables['erupciones_cutáneas']['high'] &
                self.variables['fiebre']['high'] &
                self.variables['heart_rate']['high'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['picazón']['high'] &
                self.variables['fatiga']['high'] &
                self.variables['temperature']['high'] &
                self.variables['erupciones_cutáneas']['high'],
                probability['high']
            ))


        # Reglas para el grupo "Enfermedades del Sistema Circulatorio"
        elif group.name == "Enfermedades del Sistema Circulatorio":
            # Combinaciones altas de síntomas clave
            rules.append(ctrl.Rule(self.variables['mareos']['high'] & self.variables['fatiga']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['high'] & self.variables['mareos']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fatiga']['high'] & self.variables['dolor_de_cabeza']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['high'] & self.variables['fatiga']['high'], probability['high']))

            # Uso de signos vitales con síntomas clave
            rules.append(ctrl.Rule(self.variables['mareos']['high'] & self.variables['blood_pressure']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['fatiga']['high'] & self.variables['heart_rate']['high'], probability['high']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['high'] & self.variables['heart_rate']['high'], probability['high']))

            # Combinaciones moderadas
            rules.append(ctrl.Rule(self.variables['mareos']['normal'] & self.variables['dolor_de_cabeza']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['fatiga']['normal'] & self.variables['blood_pressure']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['mareos']['normal'] & self.variables['heart_rate']['normal'], probability['normal']))
            rules.append(ctrl.Rule(self.variables['dolor_de_cabeza']['normal'] & self.variables['heart_rate']['normal'], probability['normal']))

            # Penalizaciones y probabilidades bajas
            rules.append(ctrl.Rule(self.variables['mareos']['low'] & self.variables['fatiga']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['blood_pressure']['low'] & self.variables['dolor_de_cabeza']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['heart_rate']['low'] & self.variables['mareos']['low'], probability['low']))
            rules.append(ctrl.Rule(self.variables['fatiga']['low'] & self.variables['heart_rate']['low'], probability['low']))

            # Casos críticos: múltiples síntomas altos simultáneamente
            rules.append(ctrl.Rule(
                self.variables['mareos']['high'] &
                self.variables['fatiga']['high'] &
                self.variables['blood_pressure']['high'] &
                self.variables['heart_rate']['high'],
                probability['high']
            ))

            rules.append(ctrl.Rule(
                self.variables['dolor_de_cabeza']['high'] &
                self.variables['mareos']['high'] &
                self.variables['blood_pressure']['high'] &
                self.variables['heart_rate']['high'],
                probability['high']
            ))

            # Consideración para niveles intermedios
            rules.append(ctrl.Rule(
                self.variables['blood_pressure']['normal'] & 
                self.variables['fatiga']['normal'] & 
                self.variables['mareos']['normal'],
                probability['normal']
            ))


        # Crear el sistema de control para el grupo
        system_ctrl = ctrl.ControlSystem(rules)
        system = ctrl.ControlSystemSimulation(system_ctrl)
        system.output_variable = probability
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
                        continue

            # Calcular probabilidad y obtener el resultado de salida
            system.compute()
            probability = system.output.get(system.output_variable.label)
            if probability is not None:
                results.append({
                    'group': group.name,
                    'probability': probability
                })

        # Ordenar los resultados por probabilidad de diagnóstico en orden descendente
        results = sorted(results, key=lambda x: x['probability'], reverse=True)

        # Devolver solo los 3 grupos de enfermedades con mayor probabilidad
        return results[:3]

