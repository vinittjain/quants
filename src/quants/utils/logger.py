import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO):
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create file handler with TimedRotatingFileHandler
    log_file = os.path.join(log_dir, f"quants_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str):
    return logging.getLogger(name)


def clear_old_logs(log_dir: str, days_to_keep: int = 30):
    """
    Clear log files older than the specified number of days.

    :param log_dir: Directory containing log files
    :param days_to_keep: Number of days to keep logs for
    """
    logger = get_logger(__name__)
    current_time = datetime.now()
    for filename in os.listdir(log_dir):
        if filename.endswith(".log"):
            file_path = os.path.join(log_dir, filename)
            file_modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if current_time - file_modification_time > timedelta(days=days_to_keep):
                os.remove(file_path)
                logger.info(f"Deleted old log file: {filename}")
