import logging
import sys
import os

class KivyColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\x1b[36m',    # cyan
        'INFO': '\x1b[92m',     # lime green
        'WARNING': '\x1b[93m',  # yellow
        'ERROR': '\x1b[91m',    # red
        'CRITICAL': '\x1b[95m', # magenta
    }
    RESET = '\x1b[0m'

    def format(self, record):
        level = record.levelname.ljust(7)
        name = record.name.ljust(14)
        msg = record.getMessage()
        if sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, '')
            level = f"{color}{level}{self.RESET}"
        return f"[{level}] [{name}] {msg}"


logger = logging.getLogger("android_notify")

logger.setLevel(logging.NOTSET)
logger.propagate = False

handler = logging.StreamHandler()
formatter = KivyColorFormatter()
handler.setFormatter(formatter)
handler.setLevel(logging.NOTSET)  # respect logger level

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(handler)

logger._configured = True



env_level = os.getenv("ANDROID_NOTIFY_LOGLEVEL")
if env_level:
    # noinspection PyBroadException
    try:
        logging.getLogger("android_notify").setLevel(
            getattr(logging, env_level.upper())
        )
    except:
        pass




# import logging
# import sys
#
# class KivyColorFormatter(logging.Formatter):
#     COLORS = {
#         'DEBUG': '\x1b[36m',  # cyan
#         'INFO': '\x1b[92m',   # lime green ✅
#         'WARNING': '\x1b[93m',
#         'ERROR': '\x1b[91m',
#         'CRITICAL': '\x1b[95m',
#     }
#     RESET = '\x1b[0m'
#
#     def format(self, record):
#         level = record.levelname.ljust(7)
#         name = record.name.ljust(14)
#         msg = record.getMessage()
#
#         if sys.stdout.isatty():
#             color = self.COLORS.get(record.levelname, '')
#             level = f"{color}{level}{self.RESET}"
#
#         return f"[{level}] [{name}] {msg}"
#
#
# logger = logging.getLogger("android_notify")
# logger.setLevel(logging.NOTSET)  # inherit from user
#
#
# handler = logging.StreamHandler()
# handler.setFormatter(KivyColorFormatter())
#
# # Avoid duplicate logs if root logger is configured
# logger.propagate = False
# logger.addHandler(handler)
