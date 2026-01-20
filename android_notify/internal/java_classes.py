import os

from .logger import logger

def on_android_platform():
    kivy_build = os.environ.get('KIVY_BUILD', '')
    if kivy_build in {'android'}:
        return True
    elif 'P4A_BOOTSTRAP' in os.environ:
        return True
    elif 'ANDROID_ARGUMENT' in os.environ:
        return True
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")


if on_android_platform():
    try:
        from jnius import cast, autoclass
    except ModuleNotFoundError:
        cast = lambda x, y: x
        autoclass = lambda x: None
        logger.exception("run pip install pyjnius")

    # Leaving this as a broad Exception for unforeseen case so apps don't crash
    # noinspection PyBroadException
    try:
        # Get the required Java classes needs to run on android to import
        Bundle = autoclass('android.os.Bundle')
        String = autoclass('java.lang.String')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        BitmapFactory = autoclass('android.graphics.BitmapFactory')
        BuildVersion = autoclass('android.os.Build$VERSION')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        RemoteViews = autoclass('android.widget.RemoteViews')
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        Manifest = autoclass('android.Manifest$permission')
        Color = autoclass('android.graphics.Color')
        Context = autoclass('android.content.Context')
    except Exception as e:
        from .facade import *
        logger.exception("Didn't get Basic Java Classes")

    # noinspection PyBroadException
    try:
        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
        IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')

        # Notification Design
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
        NotificationCompatDecoratedCustomViewStyle = autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')

    except Exception as dependencies_import_error:
        logger.exception("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        """)

        from .facade import *
else:
    cast = lambda x, y: x
    autoclass = lambda x: None
    # noinspection PyUnresolvedReferences
    from .facade import *
    logger.warning("Did not initialize java classes, Not on Android")

