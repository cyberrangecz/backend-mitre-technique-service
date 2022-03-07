from yamlize import Attribute, Object, YamlizingError

TEST_CONFIG_VAR = "Hi"


class KypoServiceConfig(Object):
    test_config_var = Attribute(type=str, default=TEST_CONFIG_VAR)

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
            raise Exception(ex)
        return obj

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            return cls.load(f)
