from .base_config import BaseConfig

class TestConfig(BaseConfig):
    ENV = 'test'

    # Model Monitoring Services Config
    MODEL_MONITORING_SERVICE_BASE_URL = 'http://localhost:8080'
