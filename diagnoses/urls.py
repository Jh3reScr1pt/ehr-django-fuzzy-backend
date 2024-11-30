from django.urls import path
from . import views

urlpatterns = [
    path('diagnoses/', views.DiagnosesListCreateView.as_view(), name='diagnoses_list_create'),
    path('diagnosis/<int:pk>/', views.DiagnosisDetailView.as_view(), name='diagnosis_detail'),
    path('symptoms/', views.SymptomListView.as_view(), name='symptom_list'),
]
