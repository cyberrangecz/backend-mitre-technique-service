"""Django AppConfig for the MITRE matrix visualiser application."""

from django.apps import AppConfig


class MitreMatrixVisualizerAppConfig(AppConfig):  # type: ignore[misc]
    """App configuration for crczp.mitre_matrix_visualizer_app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = __package__
