import logging
from app.core.logging import LOGGING_CONFIG
import logging.config

logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a project-wide configured logger.
    """
    return logging.getLogger(name)
