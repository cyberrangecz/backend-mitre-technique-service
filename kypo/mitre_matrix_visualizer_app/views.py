from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from kypo.mitre_matrix_visualizer_app import serializers
from kypo.mitre_matrix_visualizer_app.lib.mitre_matrix_generator import MitreMatrixGenerator, MitreClient
from kypo.mitre_common_lib.exceptions import AuthenticationTokenMissing
from django.http import HttpResponse
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema

from kypo.mitre_matrix_visualizer_app.lib.technique import Technique


class GetMatrixVisualisationView(APIView):

    @swagger_auto_schema(manual_parameters=[
                             openapi.Parameter('played', openapi.IN_QUERY,
                                               description="Only training definitions marked as "
                                                           "played will be added to the "
                                                           "visualization.",
                                               type=openapi.TYPE_BOOLEAN, default=False),
                         ])
    def get(self, request, *args, **kwargs):
        """
        Get matrix of MITRE ATT&CK tactics and techniques related to game definitions.
        """
        auth_bearer_token = None
        for header in request.META.items():
            if header[0] == 'HTTP_AUTHORIZATION':
                auth_bearer_token = header[1]
        if not auth_bearer_token:
            raise AuthenticationTokenMissing("Authentication token is missing from the header")

        played = request.GET.get('played') == "true"
        template = MitreMatrixGenerator().generate_matrix(auth_bearer_token, played)
        return HttpResponse(template)


class GetMitreTechniqueIndexView(generics.ListAPIView):
    serializer_class = serializers.TechniqueSerializer

    def get(self, request, *args, **kwargs):
        """
        Get index of mitre techniques containing their names and codes.
        """
        client = MitreClient()
        (_, _, technique_index) = client.get_tactics_techniques_with_backup()
        serializer = self.serializer_class(technique_index, many=True)
        return Response({'techniques': serializer.data})
