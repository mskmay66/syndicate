import os
import logging
from logging.handlers import RotatingFileHandler

from .file_manager import generate_log_path


def setup_logging(
    name, service_name, level=logging.INFO, max_bytes=10 * 1024 * 1024, backup_count=5
):
    """Sets up logging for the application with a rotating file handler.

    Args:
        name (str): The name of the logger to be created.
        service_name (str): _description_
        level (logging.LOGGINGLEVEL, optional): The level to log. Defaults to logging.INFO.
        max_bytes (int, optional): The max size of log file. Defaults to 10*1024*1024.
        backup_count (int, optional): The number of backups. Defaults to 5.

    Returns:
        logging.logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.propagate = False

    log_path = generate_log_path(service_name)
    if not os.path.exists(log_path):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

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
