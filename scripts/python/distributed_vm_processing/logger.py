#
# StackDriver Logger
#
from google.cloud import logging as google_logging
import logging as python_logger
import socket

DEFAULT_SOURCE = "Scripts"


class Logger:
    def __init__(self, source=DEFAULT_SOURCE, environment="development"):
        self.source = source
        if environment != "development":
            client = google_logging.Client()
            handler = client.get_default_handler()
            self.logger = python_logger.getLogger('cloudLogger')
            self.logger.setLevel(python_logger.INFO)
            self.logger.addHandler(handler)
        else:
            self.logger = python_logger.getLogger('localLogger')
            self.logger.setLevel(python_logger.DEBUG)

    def info(self, log_message=""):
        message = "{} [INFO] Source: {} {}".format(socket.gethostname(), self.source, log_message)
        self.logger.info(message)
        print(message)

    def warn(self, log_message=""):
        message = "{} [WARN] Source: {} {}".format(socket.gethostname(), self.source, log_message)
        self.logger.warn(message)
        print(message)

    def error(self, log_message=""):
        message = "{} [ERROR] Source: {} {}".format(socket.gethostname(), self.source, log_message)
        self.logger.error(message)
        print(message)
