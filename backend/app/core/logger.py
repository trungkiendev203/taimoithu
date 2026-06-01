import logging
import sys

def setup_logger():
    logger = logging.getLogger("taimoithu")
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times in dev
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()
