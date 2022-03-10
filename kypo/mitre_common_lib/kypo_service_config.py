from yamlize import Attribute, Object, YamlizingError, Sequence, Typed, StrList

from kypo.mitre_common_lib.kypo_config import KypoConfiguration
from kypo.mitre_common_lib.exceptions import ImproperlyConfigured

DEBUG = True
MICROSERVICE_NAME = 'kypo-sandbox-service'
ALLOWED_HOSTS = ['*']  # Allow everyone
AUTHENTICATED_REST_API = False
ALLOWED_OIDC_PROVIDERS = []
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = []



class AllowedOidcProviders(Sequence):
    item_type = Typed(dict)


class Authentication(Object):
    authenticated_rest_api = Attribute(type=bool, default=AUTHENTICATED_REST_API)
    allowed_oidc_providers = Attribute(type=AllowedOidcProviders,
                                       default=tuple(ALLOWED_OIDC_PROVIDERS))
    roles_registration_url = Attribute(type=str)
    roles_acquisition_url = Attribute(type=str)

    def __init__(self, authenticated_rest_api, allowed_oidc_providers,
                 roles_registration_url, roles_acquisition_url):
        self.authenticated_rest_api = authenticated_rest_api
        self.allowed_oidc_providers = allowed_oidc_providers
        self.roles_registration_url = roles_registration_url
        self.roles_acquisition_url = roles_acquisition_url


class KypoServiceConfig(Object):
    microservice_name = Attribute(type=str, default=MICROSERVICE_NAME)
    debug = Attribute(type=bool, default=DEBUG)
    allowed_hosts = Attribute(type= StrList, default=tuple(ALLOWED_HOSTS))
    cors_origin_allow_all = Attribute(type=bool, default=CORS_ORIGIN_ALLOW_ALL)
    cors_origin_whitelist = Attribute(type=StrList, default=tuple(CORS_ORIGIN_WHITELIST))

    authentication = Attribute(type=Authentication)
    app_config = Attribute(type=KypoConfiguration, key='application_configuration')

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    # Override
    @classmethod
    def load(cls, *args, **kwargs) -> 'KypoServiceConfig':
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
