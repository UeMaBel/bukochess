import logging


def get_logger(name: str) -> logging.Logger:
    """
    Returns a project-wide configured logger.
    """
    return logging.getLogger(name)
