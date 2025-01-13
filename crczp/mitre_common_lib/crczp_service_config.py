from yamlize import Attribute, Object, YamlizingError, Sequence, Typed, StrList

from crczp.mitre_common_lib.crczp_config import CrczpConfiguration
from crczp.mitre_common_lib.exceptions import ImproperlyConfigured

DEBUG = True
MICROSERVICE_NAME = 'mitre-technique-service'
ALLOWED_HOSTS = ['*']  # Allow everyone
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = []


class AllowedOidcProviders(Sequence):
    item_type = Typed(dict)


class CrczpServiceConfig(Object):
    microservice_name = Attribute(type=str, default=MICROSERVICE_NAME)
    debug = Attribute(type=bool, default=DEBUG)
    allowed_hosts = Attribute(type=StrList, default=tuple(ALLOWED_HOSTS))
    cors_origin_allow_all = Attribute(type=bool, default=CORS_ORIGIN_ALLOW_ALL)
    cors_origin_whitelist = Attribute(type=StrList, default=tuple(CORS_ORIGIN_WHITELIST))

    app_config = Attribute(type=CrczpConfiguration, key='application_configuration')

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    # Override
    @classmethod
    def load(cls, *args, **kwargs) -> 'CrczpServiceConfig':
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
