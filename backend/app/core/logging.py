import logging.config
from copy import deepcopy
from pathlib import Path

LOG_DIR = Path("logs")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": (
                "[%(asctime)s] [%(levelname)s] [%(name)s] "
                "[%(filename)s:%(lineno)d] %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "bukochess.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


def configure_logging(log_dir: Path = LOG_DIR) -> None:
    """Configure application logging when the ASGI application starts."""
    log_dir.mkdir(parents=True, exist_ok=True)
    config = deepcopy(LOGGING_CONFIG)
    config["handlers"]["file"]["filename"] = str(log_dir / "bukochess.log")
    logging.config.dictConfig(config)
