import logging
import multiprocessing
from os import environ as env

from dotenv import load_dotenv
from gunicorn import glogging

load_dotenv()

PORT = env.get("HOST_PORT", "8080")
DEBUG_MODE = env.get("DEBUG_MODE", True)
LOG_LEVEL = env.get("LOG_LEVEL", "info")
preload_app = True

# Gunicorn config
bind = ":" + PORT
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
loglevel = str(LOG_LEVEL)
accesslog = "-"

# Need to override the logger to remove healthcheck (ping) form accesslog


class CustomGunicornLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)

        # Add filters to Gunicorn logger
        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(PingFilter())
        logger.addFilter(ReadyFilter())


class PingFilter(logging.Filter):
    def filter(self, record):
        return "GET /ping" not in record.getMessage()


class ReadyFilter(logging.Filter):
    def filter(self, record):
        return "GET /ready" not in record.getMessage()


logger_class = CustomGunicornLogger
