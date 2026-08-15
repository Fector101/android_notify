import os
from functools import wraps

from .internal.logger import logger


__version__ = "1.61.6"


# ---------------------------------------------------------------------------
# Cached platform/environment state
# ---------------------------------------------------------------------------

_KIVY_ANDROID = (
    os.environ.get("KIVY_BUILD") == "android"
    or "P4A_BOOTSTRAP" in os.environ
    or "ANDROID_ARGUMENT" in os.environ
)

_FLET_ACTIVITY_CLASS_NAME = os.environ.get("MAIN_ACTIVITY_HOST_CLASS_NAME")

_ANDROID_PLATFORM = _KIVY_ANDROID or bool(_FLET_ACTIVITY_CLASS_NAME)

_FROM_SERVICE_FILE = "PYTHON_SERVICE_ARGUMENT" in os.environ


# ---------------------------------------------------------------------------
# Lazy JNI imports
# ---------------------------------------------------------------------------

_cast = None
_autoclass = None


def _load_jnius():
    """Load pyjnius lazily.

    Importing pyjnius can be relatively expensive, so don't do it during
    module import unless it is actually needed.
    """
    global _cast, _autoclass

    if _cast is not None:
        return _cast, _autoclass

    try:
        from jnius import cast, autoclass
    except ModuleNotFoundError:
        # Preserve the old fallback behavior.
        _cast = lambda obj, cls: obj
        _autoclass = lambda cls: None
    else:
        _cast = cast
        _autoclass = autoclass

    return _cast, _autoclass


# ---------------------------------------------------------------------------
# Java object caches
# ---------------------------------------------------------------------------

_activity_class_name = None
_python_activity_class = None
_python_service_class = None
_activity_context = None
_notification_manager = None


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def on_kivy_android():
    return _KIVY_ANDROID


def on_flet_app():
    return _FLET_ACTIVITY_CLASS_NAME


def on_android_platform():
    return _ANDROID_PLATFORM


def from_service_file():
    return _FROM_SERVICE_FILE


def on_pydroid_app():
    package_name = "ru.iiec.pydroid3"

    python_home = os.environ.get("PYTHONHOME", "")

    if package_name in python_home:
        return True

    if package_name in os.path.dirname(os.path.abspath(__file__)):
        return True

    if on_android_platform():
        return package_name == get_package_name()

    return False


# ---------------------------------------------------------------------------
# Android helpers
# ---------------------------------------------------------------------------

def get_activity_class_name():
    global _activity_class_name

    if _activity_class_name is not None:
        return _activity_class_name

    if _FLET_ACTIVITY_CLASS_NAME:
        _activity_class_name = _FLET_ACTIVITY_CLASS_NAME
        return _activity_class_name

    try:
        # noinspection PyPackageRequirements
        from android import config  # type: ignore

        _activity_class_name = config.JAVA_NAMESPACE
    except (ImportError, AttributeError):
        _activity_class_name = "org.kivy.android"

    return _activity_class_name


def get_python_activity():
    """Return the PythonActivity Java class.

    The Java class is resolved only on the first call and then cached.
    """
    global _python_activity_class

    if _python_activity_class is not None:
        return _python_activity_class

    if not on_android_platform():
        logger.warning("Can't get python activity, Not on Android.")
        from .internal.facade import PythonActivity

        _python_activity_class = PythonActivity
        return _python_activity_class

    _, autoclass = _load_jnius()

    activity_class_name = get_activity_class_name()

    if on_flet_app():
        class_name = activity_class_name
    else:
        class_name = activity_class_name + ".PythonActivity"

    _python_activity_class = autoclass(class_name)

    return _python_activity_class


def get_python_service():
    """Return the PythonService.mService instance.

    The service class and service instance are resolved lazily.
    """
    global _python_service_class

    if _python_service_class is not None:
        return _python_service_class

    if not on_android_platform():
        logger.warning("Can't get python service, Not on Android.")
        from .internal.facade import PythonActivity

        _python_service_class = PythonActivity
        return _python_service_class

    _, autoclass = _load_jnius()

    class_name = get_activity_class_name() + ".PythonService"
    service_class = autoclass(class_name)

    _python_service_class = service_class.mService

    return _python_service_class


def get_python_activity_context():
    """Return the Android activity/application context.

    The resulting context is cached because it does not need to be resolved
    repeatedly during the lifetime of the Python process.
    """
    global _activity_context

    if _activity_context is not None:
        return _activity_context

    if not on_android_platform():
        logger.warning("Can't get python context, Not on Android.")
        from .internal.facade import Context

        _activity_context = Context
        return _activity_context

    if from_service_file():
        service = get_python_service()
        _activity_context = (
            service
            .getApplication()
            .getApplicationContext()
        )
    else:
        PythonActivity = get_python_activity()
        _activity_context = PythonActivity.mActivity

    return _activity_context


# ---------------------------------------------------------------------------
# Android services
# ---------------------------------------------------------------------------

def get_notification_manager():
    global _notification_manager

    if _notification_manager is not None:
        return _notification_manager

    if not on_android_platform():
        logger.warning("Can't get notification manager, Not on Android.")
        return None

    cast, autoclass = _load_jnius()

    NotificationManager = autoclass("android.app.NotificationManager")

    context = get_python_activity_context()

    notification_service = context.getSystemService(
        context.NOTIFICATION_SERVICE
    )

    _notification_manager = cast(
        NotificationManager,
        notification_service,
    )

    return _notification_manager


def has_androidx_dependency():
    """Check whether AndroidX NotificationCompat is available."""
    try:
        _, autoclass = _load_jnius()
        autoclass("androidx.core.app.NotificationCompat")
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

_app_storage_path = None


def app_storage_path():
    """Return the application-specific storage path.

    The result is cached because the application storage location does not
    normally change during a process lifetime.
    """
    global _app_storage_path

    if _app_storage_path is not None:
        return _app_storage_path

    if on_flet_app():
        context = get_python_activity_context()

        _app_storage_path = os.path.join(
            context.getFilesDir().getAbsolutePath(),
            "flet",
        )

    elif on_kivy_android():
        # noinspection PyPackageRequirements
        from android.storage import (
            app_storage_path as kivy_app_storage_path,
        )

        _app_storage_path = kivy_app_storage_path()

    else:
        _app_storage_path = os.getcwd()

    return _app_storage_path


# ---------------------------------------------------------------------------
# Package information
# ---------------------------------------------------------------------------

_package_name = None


def get_package_name():
    global _package_name

    if _package_name is not None:
        return _package_name

    _package_name = get_python_activity_context().getPackageName()

    return _package_name


# ---------------------------------------------------------------------------
# UI-thread decorator
# ---------------------------------------------------------------------------

if on_flet_app() or from_service_file() or not on_android_platform():

    def run_on_ui_thread(func):
        """Fallback implementation for non-Kivy environments."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning("Simulating run on UI thread")
            return func(*args, **kwargs)

        return wrapper

elif on_kivy_android():

    # noinspection PyPackageRequirements
    from android.runnable import run_on_ui_thread  # type: ignore
