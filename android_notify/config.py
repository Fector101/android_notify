import os, traceback
from jnius import cast, autoclass

ON_ANDROID = False

try:
    from android import config
    ACTIVITY_CLASS_NAME = config.JAVA_NAMESPACE
except (ImportError, AttributeError):
    ACTIVITY_CLASS_NAME = 'org.kivy.android'


try:
    # Android Imports
    from android import activity as android_activity
    from jnius import autoclass,cast

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

    ON_ANDROID = True
except Exception as e:
    from .an_types import *
    if hasattr(e,'name') and e.name != 'android' :
        print('Exception: ',e)
        print(traceback.format_exc())

if ON_ANDROID:
    try:
        from android.permissions import request_permissions, Permission, check_permission
        from android.storage import app_storage_path

        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')

        # Notification Design
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
        NotificationCompatDecoratedCustomViewStyle = autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')
        Color = autoclass('android.graphics.Color')

    except Exception as dependencies_import_error:
        print('dependencies_import_error: ',dependencies_import_error)
        print("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS
        """)
        def app_storage_path():
            return './'
        from .an_types import *
        from .an_types import AndroidActivity as android_activity
else:
    def app_storage_path():
        return './'
    from .an_types import *
    from  .an_types import AndroidActivity as android_activity



def from_service_file():
    return 'PYTHON_SERVICE_ARGUMENT' in os.environ

run_on_ui_thread = None
if from_service_file() or not ON_ANDROID:
    def run_on_ui_thread(func):
        """Fallback for Developing on PC"""

        def wrapper(*args, **kwargs):
            # print("Simulating run on UI thread")
            return func(*args, **kwargs)

        return wrapper
else:
    from android.runnable import run_on_ui_thread

def get_python_activity():
    if not ON_ANDROID:
        from .an_types import PythonActivity
        return PythonActivity
    if from_service_file():
        # PythonService = autoclass(ACTIVITY_CLASS_NAME + '.PythonService')
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME + '.PythonService')
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
