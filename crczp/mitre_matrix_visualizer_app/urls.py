from django.urls import path

from crczp.mitre_matrix_visualizer_app import views

urlpatterns = [
    path('mitre-matrix-visualisation', views.GetMatrixVisualisationView.as_view(),
         name='mitre matrix visualisation'),
    path('mitre-technqiue-index', views.GetMitreTechniqueIndexView.as_view(),
         name='mitre technique index'),
    path('mitre-update-matrix-data', views.UpdateMatrixDataView.as_view(),
         name='update mitre matrix data'),
]
