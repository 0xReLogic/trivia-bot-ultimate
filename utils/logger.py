import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'trivia_bot.log')

def setup_logger():
    """
    Sets up a comprehensive logger for the application.
    """
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Create a logger object
    logger = logging.getLogger('TriviaBotLogger')
    logger.setLevel(logging.DEBUG) # Set the lowest level to capture all messages

    # Prevent adding handlers multiple times if this function is called more than once
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a rotating file handler
    # Rotates when the log file reaches 2MB, keeps 5 backup logs
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Only show INFO and above on the console

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create a global logger instance to be used by other modules
log = setup_logger()

log.info("Logger has been configured.")
