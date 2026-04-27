from rest_framework import serializers


class TechniqueSerializer(serializers.Serializer):  # type: ignore[misc]
    code = serializers.CharField()
    name = serializers.CharField()


class UpdateMatrixDataResponseSerializer(serializers.Serializer):  # type: ignore[misc]
    message = serializers.CharField()
