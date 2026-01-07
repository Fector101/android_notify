import logging
import sys
import os

# -------------------------
# Detect Android
# -------------------------
try:
    from jnius import autoclass, JavaException
    ANDROID = True
    Log = autoclass("android.util.Log")
except (ImportError,JavaException):
    ANDROID = False
    Log = None


# -------------------------
# Kivy-style colored formatter (desktop)
# -------------------------
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

# -------------------------
# Android Logcat Handler
# -------------------------
if ANDROID:
    class LogcatHandler(logging.Handler):
        LEVEL_MAP = {
            logging.DEBUG:    Log.DEBUG,
            logging.INFO:     Log.INFO,
            logging.WARNING:  Log.WARN,
            logging.ERROR:    Log.ERROR,
            logging.CRITICAL: Log.ASSERT,
        }

        def emit(self, record):
            tag = record.name
            msg = self.format(record)
            level = self.LEVEL_MAP.get(record.levelno, Log.INFO)
            Log.println(level, tag, msg)
else:
    LogcatHandler = None  # safe fallback for desktop

# -------------------------
# Logger setup
# -------------------------
logger = logging.getLogger("android_notify")

# Default to NOTSET so users can control level with setLevel()
logger.setLevel(logging.NOTSET)
logger.propagate = False

# Choose handler
if ANDROID and LogcatHandler is not None:
    handler = LogcatHandler()
    formatter = logging.Formatter("%(levelname)s: [%(name)s] %(message)s")
else:
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
