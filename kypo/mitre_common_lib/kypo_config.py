from yamlize import Attribute, Object, YamlizingError

from kypo.mitre_common_lib.exceptions import ImproperlyConfigured

SSL_CA_CERTIFICATE_VERIFY = '/etc/ssl/certs'
DATABASE_ENGINE = "django.db.backends.postgresql"
DATABASE_HOST = "localhost"
DATABASE_NAME = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_PORT = "5432"
DATABASE_USER = "postgres"


class Database(Object):
    engine = Attribute(type=str, default=DATABASE_ENGINE)
    host = Attribute(type=str, default=DATABASE_HOST)
    name = Attribute(type=str, default=DATABASE_NAME)
    password = Attribute(type=str, default=DATABASE_PASSWORD)
    port = Attribute(type=str, default=DATABASE_PORT)
    user = Attribute(type=str, default=DATABASE_USER)

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class KypoConfiguration(Object):
    database = Attribute(type=Database)
    ssl_ca_certificate_verify = Attribute(type=str, default=SSL_CA_CERTIFICATE_VERIFY)

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    # Override
    @classmethod
    def load(cls, *args, **kwargs) -> 'KypoConfiguration':
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
