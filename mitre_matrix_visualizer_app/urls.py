"""Mitre Matrix Technique Visualizer urls."""

from django.urls import path

from mitre_matrix_visualizer_app import views

urlpatterns = [
    path('test', views.TestView.as_view(), name='test'),
]