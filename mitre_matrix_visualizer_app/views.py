from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from mitre_matrix_visualizer_app.lib.mitre_matrix_generator import MitreMatrixGenerator

class TestView(APIView):
    """
    get: HENLOOO
    """
    def get(self, request, *args, **kwargs):
        """
        Henlo
        """
        #mitre_client = MitreClient()
        #mitre_client.test_get_mitre()
        MitreMatrixGenerator().test_generate()
        print("DONE")
        return Response("henlo")
