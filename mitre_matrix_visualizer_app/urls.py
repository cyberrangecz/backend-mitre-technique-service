from django.urls import path

from mitre_matrix_visualizer_app import views

urlpatterns = [
    path('mitre-matrix-visualisation', views.GetMatrixVisualisationView.as_view(), name='mitre matrix visualisation'),
]
