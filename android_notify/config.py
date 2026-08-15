import os
from functools import wraps

from .internal.logger import logger


__version__ = "1.61.6"


# ============================================================================
# Lazy cached state
# ============================================================================

_kivy_android = None
_flet_app = None
_android_platform = None
_from_service_file = None

_activity_class_name = None

_jnius = None
_python_activity = None
_python_service = None
_activity_context = None
_notification_manager = None
_app_storage_path = None
_package_name = None


# ============================================================================
# Platform detection
# ============================================================================

def on_kivy_android():
    global _kivy_android

    if _kivy_android is None:
        _kivy_android = (
            os.environ.get("KIVY_BUILD") == "android"
            or "P4A_BOOTSTRAP" in os.environ
            or "ANDROID_ARGUMENT" in os.environ
        )

    return _kivy_android


def on_flet_app():
    global _flet_app

    if _flet_app is None:
        _flet_app = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")

    return _flet_app


def on_android_platform():
    global _android_platform

    if _android_platform is None:
        _android_platform = (
            on_kivy_android() or bool(on_flet_app())
        )

    return _android_platform


def from_service_file():
    global _from_service_file

    if _from_service_file is None:
        _from_service_file = (
            "PYTHON_SERVICE_ARGUMENT" in os.environ
        )

    return _from_service_file


# ============================================================================
# Lazy pyjnius loading
# ============================================================================

def _get_jnius():
    global _jnius

    if _jnius is None:
        try:
            from jnius import cast, autoclass
        except ModuleNotFoundError:
            cast = lambda obj, cls: obj
            autoclass = lambda cls: None

        _jnius = (cast, autoclass)

    return _jnius


# ============================================================================
# Pydroid
# ============================================================================

def on_pydroid_app():
    package_name = "ru.iiec.pydroid3"

    if package_name in os.environ.get("PYTHONHOME", ""):
        return True

    if package_name in os.path.dirname(os.path.abspath(__file__)):
        return True

    if on_android_platform():
        return package_name == get_package_name()

    return False


# ============================================================================
# Android class information
# ============================================================================

def get_activity_class_name():
    global _activity_class_name

    if _activity_class_name is not None:
        return _activity_class_name

    activity_class_name = os.getenv(
        "MAIN_ACTIVITY_HOST_CLASS_NAME"
    )

    if not activity_class_name:
        try:
            # noinspection PyPackageRequirements
            from android import config  # type: ignore

            activity_class_name = config.JAVA_NAMESPACE

        except (ImportError, AttributeError):
            activity_class_name = "org.kivy.android"

    _activity_class_name = activity_class_name

    return _activity_class_name


# ============================================================================
# UI thread
# ============================================================================

if on_flet_app() or from_service_file() or not on_android_platform():

    def run_on_ui_thread(func):
        """Fallback for development/non-Kivy environments."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning("Simulating run on UI thread")
            return func(*args, **kwargs)

        return wrapper

elif on_kivy_android():

    # noinspection PyPackageRequirements
    from android.runnable import run_on_ui_thread  # type: ignore


# ============================================================================
# Python Activity
# ============================================================================

def get_python_activity():
    global _python_activity

    if _python_activity is not None:
        return _python_activity

    if not on_android_platform():
        logger.warning("Can't get python activity, Not on Android.")

        from .internal.facade import PythonActivity

        _python_activity = PythonActivity
        return _python_activity

    _, autoclass = _get_jnius()

    activity_class_name = get_activity_class_name()

    if on_flet_app():
        class_name = activity_class_name
    else:
        class_name = activity_class_name + ".PythonActivity"

    _python_activity = autoclass(class_name)

    return _python_activity


# ============================================================================
# Python Service
# ============================================================================

def get_python_service():
    global _python_service

    if _python_service is not None:
        return _python_service

    if not on_android_platform():
        logger.warning("Can't get python service, Not on Android.")

        from .internal.facade import PythonActivity

        _python_service = PythonActivity
        return _python_service

    _, autoclass = _get_jnius()

    class_name = get_activity_class_name() + ".PythonService"

    PythonService = autoclass(class_name)

    _python_service = PythonService.mService

    return _python_service


# ============================================================================
# Activity Context
# ============================================================================

def get_python_activity_context():
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


# ============================================================================
# Notification Manager
# ============================================================================

def get_notification_manager():
    global _notification_manager

    if _notification_manager is not None:
        return _notification_manager

    if not on_android_platform():
        logger.warning("Can't get notification manager, Not on Android.")
        return None

    cast, autoclass = _get_jnius()

    NotificationManager = autoclass(
        "android.app.NotificationManager"
    )

    context = get_python_activity_context()

    notification_service = context.getSystemService(
        context.NOTIFICATION_SERVICE
    )

    _notification_manager = cast(
        NotificationManager,
        notification_service,
    )

    return _notification_manager


# ============================================================================
# AndroidX
# ============================================================================

def has_androidx_dependency():
    """Check if AndroidX dependencies are available."""
    try:
        _, autoclass = _get_jnius()

        autoclass(
            "androidx.core.app.NotificationCompat"
        )

        return True

    except Exception:
        return False


# ============================================================================
# Application storage
# ============================================================================

def app_storage_path():
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


# ============================================================================
# Package name
# ============================================================================

def get_package_name():
    global _package_name

    if _package_name is not None:
        return _package_name

    _package_name = (
        get_python_activity_context()
        .getPackageName()
    )

    return _package_name