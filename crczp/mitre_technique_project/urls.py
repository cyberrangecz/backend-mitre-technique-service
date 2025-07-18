from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from rest_framework import permissions

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin', admin.site.urls, name='admin'),

    # OpenAPI schema JSON
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),

    path('', include('crczp.mitre_matrix_visualizer_app.urls')),
]

urlpatterns = [
    path(settings.URL_PREFIX, include(urlpatterns)),
]
