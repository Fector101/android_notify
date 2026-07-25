"""
This module provides properly formatting for logs.
Do not import anything from other modules in this module, as it is used by other modules and may cause circular imports.
"""

import logging
import sys
import os


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

def on_pydroid_app():
    package_name = "ru.iiec.pydroid3"
    if package_name in os.environ.get("PYTHONHOME",""):
        return True
    elif package_name in os.path.dirname(os.path.abspath(__file__)):
        return True
    # elif on_android_platform(): needs pyjnius to check
        # return package_name == get_package_name()
    return False

try:
    try:
        if on_pydroid_app():
            print("Pydroid3 Mobile detected, patching kivy no sketlon app issue")
            from kivy.app import App
    except Exception as error_importing_kivy_on_pydroid:
        print(f"On Pydroid App from PlayStore: Error importing kivy, when No Running App: {error_importing_kivy_on_pydroid}")
    from jnius import autoclass
except ModuleNotFoundError:
    autoclass = lambda x: None



def kivy_logger_patch():
    if on_flet_app():
        return

    # logs got weird in kivy app (duplicates logs)
    # Avoid duplicate logs if root logger is configured
    logger.propagate = False


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

handler = logging.StreamHandler(sys.stdout)
formatter = KivyColorFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger._configured = True

kivy_logger_patch()

env_level = os.getenv("ANDROID_NOTIFY_LOGLEVEL")
if env_level:
    try:
        logging.getLogger("android_notify").setLevel(getattr(logging, env_level.upper()))
    except Exception as android_notify_loglevel_error:
        android_print(f"android_notify_loglevel_error: {android_notify_loglevel_error}")



if __name__ == "__main__":
    logger.debug("Debug message - should not appear with INFO level")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
