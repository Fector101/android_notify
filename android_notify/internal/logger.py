import logging
import sys
import os

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


def kivy_logger_patch():
    if not on_kivy_android():
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = KivyColorFormatter()
    handler.setFormatter(formatter)

    # Avoid duplicate logs if root logger is configured
    logger.propagate = False
    logger.addHandler(handler)
    logger._configured = True


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


logger = logging.getLogger("android_notify")
kivy_logger_patch()

env_level = os.getenv("ANDROID_NOTIFY_LOGLEVEL")
if env_level:
    try:
        logging.getLogger("android_notify").setLevel(getattr(logging, env_level.upper()))
    except Exception as android_notify_loglevel_error:
        android_print(f"android_notify_loglevel_error: {android_notify_loglevel_error}")

if __name__ == "__main__":
    # from kivymd.app import MDApp

    logger.debug("Debug message - should not appear with INFO level")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
