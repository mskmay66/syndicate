import logging
from logging.handlers import RotatingFileHandler

from .file_manager import generate_log_path


def setup_logging(
    name, service_name, level=logging.INFO, max_bytes=10 * 1024 * 1024, backup_count=5
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.propagate = False

    log_path = generate_log_path(service_name)
    handler = RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count
    )
    formatter = logging.Formatter(
        "[%(asctime)s] %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
