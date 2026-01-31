import logging
import sys
import os
import traceback

try:
    from jnius import autoclass
except ModuleNotFoundError:
    autoclass = lambda x: None


def on_kivy_android():
    kivy_build = os.environ.get('KIVY_BUILD', '')
    if kivy_build in {'android'}:
        return True
    elif 'P4A_BOOTSTRAP' in os.environ:
        return True
    elif 'ANDROID_ARGUMENT' in os.environ:
        return True

    return False


def on_flet_app():
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")


def on_android_platform():
    return on_kivy_android() or on_flet_app()


def android_print(msg):
    msg = str(msg)
    if on_android_platform():
        Log = autoclass("android.util.Log")
        Log.i("python", msg)
        return None
    print(msg)
    return None


class KivyColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\x1b[1;36m',  # bold cyan
        'INFO': '\x1b[1;92m',  # bold lime green
        'WARNING': '\x1b[1;93m',  # bold yellow
        'ERROR': '\x1b[1;91m',  # bold red
        'CRITICAL': '\x1b[1;95m',  # bold magenta
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


class AndroidNotifyLogger:
    """
    Patch logger for Android (Flet) where stdout logs don't always show.
    Uses android.util.Log directly.
    """

    TAG = "python"

    LEVELS = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40,
        "critical": 50,
    }

    def __init__(self, level="debug"):
        self.Log = autoclass("android.util.Log")
        self.level = self.LEVELS[level]

    def setLevel(self, level):
        if isinstance(level, str):
            level = level.lower()
            if level not in self.LEVELS:
                raise ValueError(f"Invalid log level: {level}")
            self.level = self.LEVELS[level]
        else:
            self.Log.e(self.TAG, "Dude No such Level")
            # raise TypeError("Log level must be a string")

    def _log(self, level, msg):
        if self.LEVELS[level] < self.level:
            return

        msg = str(msg)

        if level == "debug":
            self.Log.d(self.TAG, msg)
        elif level == "info":
            self.Log.i(self.TAG, msg)
        elif level == "warning":
            self.Log.w(self.TAG, msg)
        elif level == "error":
            self.Log.e(self.TAG, msg)
        elif level == "critical":
            self.Log.wtf(self.TAG, msg)

    def debug(self, msg):
        self._log("debug", msg)

    def info(self, msg):
        self._log("info", msg)

    def warning(self, msg):
        self._log("warning", msg)

    def error(self, msg):
        self._log("error", msg)

    def critical(self, msg):
        self._log("critical", msg)

    def exception(self, msg):
        self._log("error", msg)
        self._log("error", traceback.format_exc())

    def addHandler(self, _):
        # Facade
        pass


class HandlerFacade:
    def setFormatter(self, _):
        pass


logger = logging.getLogger("android_notify") if not on_flet_app() else AndroidNotifyLogger()

# if not on flet android app use regular logger
handler = logging.StreamHandler(sys.stdout) if not on_flet_app() else HandlerFacade()
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
        logger.setLevel(getattr(logging, env_level.upper()))
    except Exception as android_notify_loglevel_error:
        android_print(f"android_notify_loglevel_error: {android_notify_loglevel_error}")
        pass

if __name__ == "__main__":
    from kivymd.app import MDApp

    logger.debug("Debug message - should not appear with INFO level")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
