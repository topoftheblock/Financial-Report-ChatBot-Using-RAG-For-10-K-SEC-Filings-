import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a centralized logger for the application.
    """
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if the logger already exists
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Output logs to standard out (stdout) which is best practice for Docker/Cloud
        handler = logging.StreamHandler(sys.stdout)

        # Professional formatting: Timestamp - Module - Severity - Message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent logs from propagating to the root logger to avoid duplicates
        logger.propagate = False

    return logger
