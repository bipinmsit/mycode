from .base_config import BaseConfig

class ProductionConfig(BaseConfig):
    ENV = 'production'

    # Model Monitoring Services Config
    MODEL_MONITORING_SERVICE_BASE_URL = 'http://production:8080'