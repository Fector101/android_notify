import os, traceback

ON_ANDROID = False
__version__ = "1.60.0"

def on_flet_app():
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")

def get_activity_class_name():
    ACTIVITY_CLASS_NAME = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME") # flet python
    if not ACTIVITY_CLASS_NAME:
        try:
            from android import config
            ACTIVITY_CLASS_NAME = config.JAVA_NAMESPACE
        except (ImportError, AttributeError):
            ACTIVITY_CLASS_NAME = 'org.kivy.android'
    return ACTIVITY_CLASS_NAME


if os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME"):
    from jnius import cast, autoclass
else:
    # print('Not on Flet android env...\n')
    try:
        import kivy #TODO find var for kivy
        from jnius import cast, autoclass
    except Exception as e:
        print('android-notify: No pjnius, not on android')
        # So commandline still works if java isn't installed and get pyjinus import error
        # print('Exception occured in __init__.py: ',e)
        cast = lambda x: x
        autoclass = lambda x: None
try:
    # Android Imports

    # Get the required Java classes needs to on android to import
    Bundle = autoclass('android.os.Bundle')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    RemoteViews = autoclass('android.widget.RemoteViews')

    ON_ANDROID = RemoteViews
except Exception as e:
    from .an_types import *
    if hasattr(e,'name') and e.name != 'android' :
        print('Exception: ',e)
        print(traceback.format_exc())


if ON_ANDROID:
    try:
        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')
        Color = autoclass('android.graphics.Color')

        # Notification Design
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
        NotificationCompatDecoratedCustomViewStyle = autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')

    except Exception as dependencies_import_error:
        print('dependencies_import_error: ',dependencies_import_error)
        print("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS
        """)

        from .an_types import *
else:
    from .an_types import *

def from_service_file():
    return 'PYTHON_SERVICE_ARGUMENT' in os.environ

run_on_ui_thread = None
if on_flet_app() or from_service_file() or not ON_ANDROID:
    def run_on_ui_thread(func):
        """Fallback for Developing on PC"""

        def wrapper(*args, **kwargs):
            # print("Simulating run on UI thread")
            return func(*args, **kwargs)

        return wrapper
else:# TODO find var for kivy
    from android.runnable import run_on_ui_thread

def get_python_activity():
    if not ON_ANDROID:
        from .an_types import PythonActivity
        return PythonActivity
    ACTIVITY_CLASS_NAME = get_activity_class_name()
    if from_service_file():
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME + '.PythonService')
    elif on_flet_app():
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
    else:
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME + '.PythonActivity')
    return PythonActivity

def get_python_activity_context():
    if not ON_ANDROID:
        from .an_types import Context
        return Context

    PythonActivity = get_python_activity()
    if from_service_file():
        service = PythonActivity.mService
        context = service.getApplication().getApplicationContext()
        # context = PythonActivity.mService
    else:
        context = PythonActivity.mActivity
    return context


if ON_ANDROID:
    context = get_python_activity_context()
else:
    context = None

def get_notification_manager():
    if not ON_ANDROID:
        return None
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    return cast(NotificationManager, notification_service)

def app_storage_path():
    if on_flet_app():
        return os.path.join(context.getFilesDir().getAbsolutePath(), 'flet')
    else:
        try:
            from android.storage import app_storage_path as kivy_app_storage_path  # type: ignore
            return kivy_app_storage_path()
        except Exception as e:
            return './'  # TODO return file main.py path (not android)
