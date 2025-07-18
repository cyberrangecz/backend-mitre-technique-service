from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from crczp.mitre_matrix_visualizer_app import serializers
from crczp.mitre_matrix_visualizer_app.lib.mitre_matrix_generator import MitreMatrixGenerator, MitreClient
from crczp.mitre_common_lib.exceptions import AuthenticationTokenMissing
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter


class GetMatrixVisualisationView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='played',
                type=bool,
                location=OpenApiParameter.QUERY,
                description=(
                    "Only training definitions marked as played will be "
                    "added to the visualization."
                ),
                required=False
            )
        ],
        responses={200: None},  # Adjust if you have a specific response schema
        description="Get matrix of MITRE ATT&CK tactics and techniques related to game definitions."
    )
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
        (_, _, technique_index) = client.get_tactics_techniques()
        serializer = self.serializer_class(technique_index, many=True)
        return Response({'techniques': serializer.data})


class UpdateMatrixDataView(APIView):
    serializer_class = serializers.UpdateMatrixDataResponseSerializer

    def put(self, request, *args, **kwargs):
        """
        Update the MITRE ATT&CK matrix data in the cache
        """
        client = MitreClient()
        update_message = client.update_matrix_data()
        return Response({'message': update_message})
