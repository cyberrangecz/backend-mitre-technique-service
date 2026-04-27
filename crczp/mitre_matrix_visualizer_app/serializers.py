"""DRF serializers for MITRE technique and matrix-update response data."""

from typing import Any

from rest_framework import serializers


class TechniqueSerializer(serializers.Serializer):  # type: ignore[misc]
    """Serializes a single MITRE ATT&CK technique (code + name)."""

    code = serializers.CharField()
    name = serializers.CharField()

    def create(self, validated_data: dict[str, Any]) -> None:
        """Not implemented - read-only serializer."""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> None:
        """Not implemented - read-only serializer."""
        raise NotImplementedError


class UpdateMatrixDataResponseSerializer(serializers.Serializer):  # type: ignore[misc]
    """Serializes the response message from a matrix-data update request."""

    message = serializers.CharField()

    def create(self, validated_data: dict[str, Any]) -> None:
        """Not implemented - read-only serializer."""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> None:
        """Not implemented - read-only serializer."""
        raise NotImplementedError
