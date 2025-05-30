from yamlize import Attribute, Object, YamlizingError

from crczp.mitre_common_lib.exceptions import ImproperlyConfigured

SSL_CA_CERTIFICATE_VERIFY = '/etc/ssl/certs'
JAVA_LINEAR_TRAINING_MITRE_ENDPOINT = 'http://127.0.0.1:8083/training/api/v1/visualizations/training-definitions/mitre-techniques'
JAVA_ADAPTIVE_TRAINING_MITRE_ENDPOINT = 'http://127.0.0.1:8082/adaptive-training/api/v1/visualizations/training-definitions/mitre-techniques'
FILE_STORAGE_LOCATION = 'crczp/mitre_matrix_visualizer_app/templates/'
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1


class Redis(Object):
    host = Attribute(type=str, default=REDIS_HOST)
    port = Attribute(type=int, default=REDIS_PORT)
    db = Attribute(type=int, default=REDIS_DB)


class CrczpConfiguration(Object):
    ssl_ca_certificate_verify = Attribute(type=str, default=SSL_CA_CERTIFICATE_VERIFY)
    java_linear_training_mitre_endpoint = Attribute(type=str,
                                                    default=JAVA_LINEAR_TRAINING_MITRE_ENDPOINT)
    java_adaptive_training_mitre_endpoint = Attribute(type=str,
                                                      default=JAVA_ADAPTIVE_TRAINING_MITRE_ENDPOINT)
    file_storage_location = Attribute(type=str, default=FILE_STORAGE_LOCATION)
    redis = Attribute(type=Redis, default=())

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    # Override
    @classmethod
    def load(cls, *args, **kwargs) -> 'CrczpConfiguration':
        """Factory method. Use it to create a new object of this class."""
        try:
            obj = super().load(*args, **kwargs)
        except YamlizingError as ex:
            raise ImproperlyConfigured(ex)
        return obj

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            return cls.load(f)
