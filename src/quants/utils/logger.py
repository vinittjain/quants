import logging
import sys
from typing import Optional


def setup_logging(log_file: Optional[str] = None, log_level: int = logging.INFO):
    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger
