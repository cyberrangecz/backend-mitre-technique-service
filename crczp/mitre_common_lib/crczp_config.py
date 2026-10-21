"""CRCZP application configuration loaded from a YAML file via yamlize."""

from pathlib import Path
from typing import Any

from yamlize import Attribute, Object, YamlizingError

from crczp.mitre_common_lib.exceptions import ImproperlyConfigured

SSL_CA_CERTIFICATE_VERIFY = '/etc/ssl/certs'
TRAINING_MITRE_TECHNIQUES_ENDPOINT = (
    'http://127.0.0.1:8083/training/api/v1/training-definitions/played-mitre-techniques'
)
FILE_STORAGE_LOCATION = (
    str(Path(__file__).resolve().parent.parent / 'mitre_matrix_visualizer_app' / 'templates') + '/'
)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1


class Redis(Object):  # type: ignore[misc]
    """Redis connection settings."""

    host = Attribute(type=str, default=REDIS_HOST)
    port = Attribute(type=int, default=REDIS_PORT)
    db = Attribute(type=int, default=REDIS_DB)


class CrczpConfiguration(Object):  # type: ignore[misc]
    """Top-level CRCZP runtime configuration."""

    ssl_ca_certificate_verify = Attribute(type=str, default=SSL_CA_CERTIFICATE_VERIFY)
    training_mitre_techniques_endpoint = Attribute(
        type=str, default=TRAINING_MITRE_TECHNIQUES_ENDPOINT
    )
    file_storage_location = Attribute(type=str, default=FILE_STORAGE_LOCATION)
    redis = Attribute(type=Redis, default=())

    def __init__(self, **kwargs: Any) -> None:
        for key, val in kwargs.items():
            setattr(self, key, val)

    # Override
    @classmethod
    def load(cls, *args: Any, **kwargs: Any) -> 'CrczpConfiguration':
        """Factory method. Use it to create a new object of this class."""
        try:
            obj = super().load(*args, **kwargs)
        except YamlizingError as ex:
            raise ImproperlyConfigured(ex) from ex
        return obj  # type: ignore[no-any-return]

    @classmethod
    def from_file(cls, path: str) -> 'CrczpConfiguration':
        """Load configuration from a YAML file at the given path."""
        with open(path, encoding='utf-8') as f:
            return cls.load(f)
