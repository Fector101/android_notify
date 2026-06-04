import os

__version__ = "1.61.3"

from .internal.logger import logger

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


if on_android_platform():
    try:
        from jnius import cast, autoclass
    except ModuleNotFoundError:
        cast = lambda x, y: x
        autoclass = lambda x: None
else:
    cast = lambda x, y: x
    autoclass = lambda x: None


def on_pydroid_app():
    package_name = "ru.iiec.pydroid3"
    if package_name in os.environ.get("PYTHONHOME",""):
        return True
    elif package_name in os.path.dirname(os.path.abspath(__file__)):
        return True
    elif on_android_platform():
        return package_name == get_package_name()
    return False


def has_androidx_dependency():
    """Check if androidx dependencies are available"""
    try:
        _=autoclass('androidx.core.app.NotificationCompat')
        return True
    except Exception:
        return False


def get_activity_class_name():
    ACTIVITY_CLASS_NAME = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")  # flet python
    if not ACTIVITY_CLASS_NAME:
        try:
            # noinspection PyPackageRequirements
            from android import config  # type: ignore
            ACTIVITY_CLASS_NAME = config.JAVA_NAMESPACE
        except (ImportError, AttributeError):
            ACTIVITY_CLASS_NAME = 'org.kivy.android'
    return ACTIVITY_CLASS_NAME


def from_service_file():
    return 'PYTHON_SERVICE_ARGUMENT' in os.environ


run_on_ui_thread = None
if on_flet_app() or from_service_file() or not on_android_platform():
    def run_on_ui_thread(func):
        """Fallback for Developing on PC"""

        def wrapper(*args, **kwargs):
            logger.warning("Simulating run on UI thread")
            return func(*args, **kwargs)

        return wrapper
elif on_kivy_android():
    # noinspection PyPackageRequirements
    from android.runnable import run_on_ui_thread  # type: ignore


def get_python_activity():
    if not on_android_platform():
        logger.warning("Can't get python activity, Not on Android.")
        from .internal.facade import PythonActivity
        return PythonActivity
    ACTIVITY_CLASS_NAME = get_activity_class_name()
    if on_flet_app():
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
    else:
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME + '.PythonActivity')
    return PythonActivity


def get_python_service():
    if not on_android_platform():
        from .internal.facade import PythonActivity
        logger.warning("Can't get python service, Not on Android.")
        return PythonActivity
    PythonService = autoclass(get_activity_class_name() + '.PythonService')
    return PythonService.mService


def get_python_activity_context():
    if not on_android_platform():
        logger.warning("Can't get python context, Not on Android.")
        from .internal.facade import Context
        return Context

    PythonActivity = get_python_activity()
    if from_service_file():
        service = get_python_service()
        context = service.getApplication().getApplicationContext()
    else:
        context = PythonActivity.mActivity
    return context


def get_notification_manager():
    if not on_android_platform():
        logger.warning("Can't get notification manager, Not on Android.")
        return None
    NotificationManager = autoclass('android.app.NotificationManager')

    context = get_python_activity_context()
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    return cast(NotificationManager, notification_service)


def app_storage_path():
    if on_flet_app():
        context = get_python_activity_context()
        return os.path.join(context.getFilesDir().getAbsolutePath(), 'flet')
    elif on_kivy_android():
        # noinspection PyPackageRequirements
        from android.storage import app_storage_path as kivy_app_storage_path  # type: ignore
        return kivy_app_storage_path()
    else:
        return os.getcwd()  # TODO return file main.py path (not android)


def get_package_name():
    return get_python_activity_context().getPackageName()  # package.domain + "." + package.name
