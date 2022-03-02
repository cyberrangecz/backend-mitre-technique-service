from rest_framework.views import APIView
from mitre_matrix_visualizer_app.lib.mitre_matrix_generator import MitreMatrixGenerator
from django.http import HttpResponse
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema


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
        played = request.GET.get('played') == "true"
        template = MitreMatrixGenerator().generate_matrix(played)
        return HttpResponse(template)
