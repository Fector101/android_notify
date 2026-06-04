"""Collection of useful functions"""

import inspect, os, re
from .logger import logger, on_android_platform

def can_accept_arguments(func, *args, **kwargs):
    try:
        sig = inspect.signature(func)
        sig.bind(*args, **kwargs)
        return True
    except TypeError:
        return False


def generate_channel_id(channel_name: str) -> str:
    """
    Generate a readable and consistent channel ID from a channel name.

    Args:
        channel_name (str): The name of the notification channel.

    Returns:
        str: A sanitized channel ID.
    """
    # Normalize the channel name
    channel_id = channel_name.strip().lower()
    # Replace spaces and special characters with underscores
    channel_id = re.sub(r'[^a-z0-9]+', '_', channel_id)
    # Remove leading/trailing underscores
    channel_id = channel_id.strip('_')
    return channel_id[:50]


def get_package_path():
    """
    Returns the directory path of this Python package.
    Works on Android, Windows, Linux, macOS.
    """
    return os.path.dirname(os.path.abspath(__file__))


def execute_callback(callback,arg, from_who="user"):
    """
    Executing Callbacks Safely
    """
    if not callback:
        return None
    if from_who == "user":
        logger.info(f"Executing On Permission Result Callback...")
    try:
        if can_accept_arguments(callback, arg):
            callback(arg)
        else:
            callback()
    except Exception as on_permissions_result_callback_error:
        logger.exception(on_permissions_result_callback_error)

def on_pydroid_app():
    package_name = "ru.iiec.pydroid3"
    if package_name in os.environ.get("PYTHONHOME",""):
        return True
    elif package_name in os.path.dirname(os.path.abspath(__file__)):
        return True
    elif on_android_platform():
        from android_notify.config import get_package_name
        return package_name == get_package_name()
    return False


def has_androidx_dependency():
    """Check if androidx dependencies are available"""
    try:
        from jnius import autoclass
        autoclass('androidx.core.app.NotificationCompat')
        return True
    except Exception:
        return False