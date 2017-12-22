from .base_config import BaseConfig

class DevelopmentConfig(BaseConfig):
    ENV = 'development'

    # Model Monitoring Services Config
    MODEL_MONITORING_SERVICE_BASE_URL = 'http://localhost:8080'
    TO_MONITOR_LOGS = False