from rest_framework import serializers


class TechniqueSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
