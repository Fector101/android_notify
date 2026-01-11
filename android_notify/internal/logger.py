import logging
import sys
import os

class KivyColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\x1b[1;36m',    # bold cyan
        'INFO': '\x1b[1;92m',     # bold lime green
        'WARNING': '\x1b[1;93m',  # bold yellow
        'ERROR': '\x1b[1;91m',    # bold red
        'CRITICAL': '\x1b[1;95m', # bold magenta
    }
    RESET = '\x1b[0m'

    def format(self, record):
        level = record.levelname.ljust(7)
        name = record.name.ljust(14)
        msg = record.getMessage()

        if getattr(sys.stdout, "isatty", lambda: False)():
            color = self.COLORS.get(record.levelname, '')
            level = f"{color}{level}{self.RESET}"

        return f"[{level}] [{name}] {msg}"


logger = logging.getLogger("android_notify")
# logger.setLevel(logging.NOTSET) # this override app logger level

handler = logging.StreamHandler(sys.stdout)
formatter = KivyColorFormatter()
handler.setFormatter(formatter)
# handler.setLevel(logging.WARNING) # this override app logger level

# Avoid duplicate logs if root logger is configured
logger.propagate = False
# if not logger.handlers:
logger.addHandler(handler)
logger._configured = True



env_level = os.getenv("ANDROID_NOTIFY_LOGLEVEL")
if env_level:
    # noinspection PyBroadException
    try:
        logging.getLogger("android_notify").setLevel( getattr(logging, env_level.upper()) )
    except Exception as android_notify_loglevel_error:
        print("android_notify_loglevel_error:",android_notify_loglevel_error)
        pass



if __name__ == "__main__":
    from kivymd.app import MDApp

    logger.debug("Debug message - should not appear with INFO level")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
