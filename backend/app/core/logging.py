import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = Path("/home/michal/projects/Antiradar/logs")
    logs_dir.mkdir(exist_ok=True, parents=True)

    # Log file path
    log_file = logs_dir / "antiradar.log"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure the root logger
    root_logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Set up console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # Set up file handler with rotation (10MB max size, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Set global log level
    root_logger.setLevel(logging.INFO)

    # Configure specific modules
    for logger_name in [
        "backend.app.services",
        "backend.app.db",
        "backend.app.api",
        "fbchat_muqit",
    ]:
        module_logger = logging.getLogger(logger_name)
        module_logger.setLevel(logging.INFO)

    # Return the main application logger
    return logging.getLogger("backend.app")
