from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from mitre_matrix_visualizer_app.lib.mitre_techniques_client import test_get_mitre


class TestView(APIView):
    """
    get: HENLOOO
    """
    def get(self, request, *args, **kwargs):
        """
        Henlo
        """
        test_get_mitre()
        print("DONE")
        return Response("henlo")
