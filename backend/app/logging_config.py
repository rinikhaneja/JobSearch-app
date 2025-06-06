import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_file = os.getenv('LOG_FILE', 'backend/logs/app.log')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('custom_logger')
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    handler.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler (logs only warnings and above)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Remove all handlers associated with the logger object (to avoid duplicates)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
    logger.addHandler(ch)

    # Suppress third-party logs
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
    logging.getLogger("serpapi").setLevel(logging.ERROR)

    # Optional: Block any log message containing 'json_result' or 'Results:'
    class NoSerpApiJsonFilter(logging.Filter):
        def filter(self, record):
            return 'json_result' not in record.getMessage() and 'Results:' not in record.getMessage()

    ch.addFilter(NoSerpApiJsonFilter())
    handler.addFilter(NoSerpApiJsonFilter())

    # Add filter to root logger as well
    root_logger = logging.getLogger()
    root_logger.addFilter(NoSerpApiJsonFilter())

    return logger 