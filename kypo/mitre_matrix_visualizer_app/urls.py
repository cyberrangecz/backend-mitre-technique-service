from django.urls import path

from kypo.mitre_matrix_visualizer_app import views

urlpatterns = [
    path('mitre-matrix-visualisation', views.GetMatrixVisualisationView.as_view(),
         name='mitre matrix visualisation'),
    path('mitre-technqiue-index', views.GetMitreTechniqueIndex.as_view(),
         name='mitre technique index'),
]
