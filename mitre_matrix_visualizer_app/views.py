from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response


class TestView(APIView):
    """
    get: HENLOOO
    """
    def get(self, request, *args, **kwargs):
        """
        Henlo
        """
        return Response("henlo")
