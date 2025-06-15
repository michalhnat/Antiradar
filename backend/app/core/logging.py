import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    logs_dir = Path("/home/michal/projects/Antiradar/logs")
    logs_dir.mkdir(exist_ok=True, parents=True)

    log_file = logs_dir / "antiradar.log"

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()

    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger.setLevel(logging.INFO)

    for logger_name in [
        "backend.app.services",
        "backend.app.db",
        "backend.app.api",
        "fbchat_muqit",
    ]:
        module_logger = logging.getLogger(logger_name)
        module_logger.setLevel(logging.INFO)

    return logging.getLogger("backend.app")
