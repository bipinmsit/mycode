from .test_config import TestConfig
from .development_config import DevelopmentConfig
from .production_config import ProductionConfig

class ConfigFactory(object):
    class __ConfigFactory:
        def __init__(self, environment):
            env_switcher = {
                'test': TestConfig,
                'development': DevelopmentConfig,
                'production': ProductionConfig
            }

            # Get the class from env_switcher
            self.env = env_switcher.get(environment, DevelopmentConfig)

        def __str__(self):
            return repr(self) + self.env

        def get_environment(self):
            return self.env()

    # First Instance Initialization
    instance = None
    def __init__(self, environment="development"):
        # Singleton Pattern for Config Class to have single instance
        if not ConfigFactory.instance:
            ConfigFactory.instance = ConfigFactory.__ConfigFactory(environment)

    # method to redirect calls to the single instance
    def __getattr__(self, name):
        return getattr(self.instance, name)