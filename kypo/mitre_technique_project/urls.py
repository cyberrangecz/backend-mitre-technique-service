from django.contrib import admin
from django.urls import path, re_path, include

from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi
from rest_framework import permissions

VERSION = 'v1'
URL_PREFIX = f'mitre-technique/api/{VERSION}/'

schema_view = get_schema_view(
    openapi.Info(
        title="KYPO mitre technique REST API documentation",
        default_version=VERSION,
        description="",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin', admin.site.urls),

    path('doc', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('', include('kypo.mitre_matrix_visualizer_app.urls')),
]

urlpatterns = [
    path(URL_PREFIX, include(urlpatterns)),
]
