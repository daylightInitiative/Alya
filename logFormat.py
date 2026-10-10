import logging
from config import app_config

class CustomFormatter(logging.Formatter):
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[94;20m"
    GREEN = "\x1b[92;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    BASE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(self):
        super().__init__()
        self._formatters = {
            logging.DEBUG: logging.Formatter(self.BLUE + self.BASE_FORMAT + self.RESET),
            logging.INFO: logging.Formatter(self.GREEN + self.BASE_FORMAT + self.RESET),
            logging.WARNING: logging.Formatter(self.YELLOW + self.BASE_FORMAT + self.RESET),
            logging.ERROR: logging.Formatter(self.RED + self.BASE_FORMAT + self.RESET),
            logging.CRITICAL: logging.Formatter(self.BOLD_RED + self.BASE_FORMAT + self.RESET),
        }
        self._default_formatter = logging.Formatter(self.BASE_FORMAT)

    def format(self, record):
        formatter = self._formatters.get(record.levelno, self._default_formatter)
        return formatter.format(record)


def setup_logger(log):
    log.setLevel(app_config.console_log_level) 
    
    if log.hasHandlers():
        log.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CustomFormatter())
    
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(app_config.file_log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    file_handler.setFormatter(file_formatter)
    
    log.addHandler(console_handler)
    log.addHandler(file_handler)
