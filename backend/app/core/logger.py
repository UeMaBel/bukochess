import logging
import logging.config

from app.core.logging import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a project-wide configured logger.
    """
    return logging.getLogger(name)
