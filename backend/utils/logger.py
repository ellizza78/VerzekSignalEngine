"""
Logging configuration for Verzek AutoTrader
"""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Setup a logger with both file and console handlers
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if log_file provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Default loggers
api_logger = setup_logger('verzek_api', '/var/log/verzek_api.log')
worker_logger = setup_logger('verzek_worker', '/var/log/verzek_worker.log')
