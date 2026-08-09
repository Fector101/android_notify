
import importlib
import threading

from android_notify.config import has_androidx_dependency, on_pydroid_app, on_android_platform, on_flet_app
from .logger import logger

if on_android_platform():
    try:
        from jnius import cast, autoclass
    except ModuleNotFoundError:
        cast = lambda x, y: x
        autoclass = lambda x: None
        logger.exception("add pyjnius to dependencies list")

    # Java classes are loaded lazily (only on first use) instead of eagerly at
    # import time. Each `autoclass()` call finds the class on the JVM and
    # enumerates ALL of its methods/fields, which is expensive at startup. By
    # deferring that to the moment a class is actually used we only pay for the
    # classes the app really touches. The fallback (.facade) is used if a class
    # can't be loaded.
    #
    # NOTE: these are module-level _LazyJavaClass instances (NOT a module-level
    # __getattr__). A module __getattr__ here made importlib's _handle_fromlist
    # probe `module.__path__` on deferred imports and crash the app (SIGABRT).
    _ANDROID_NOTIFICATION_CLASSES = {
        "IconClass": "android.graphics.drawable.Icon",
        "NotificationCompat": "android.app.Notification",
        "NotificationManagerCompat": "android.app.NotificationManager",
        "NotificationCompatBuilder": "android.app.Notification$Builder",
        "NotificationCompatBigTextStyle": "android.app.Notification$BigTextStyle",
        "NotificationCompatBigPictureStyle": "android.app.Notification$BigPictureStyle",
        "NotificationCompatInboxStyle": "android.app.Notification$InboxStyle",
        "NotificationCompatDecoratedCustomViewStyle": "android.app.Notification$DecoratedCustomViewStyle",
    }

    _ANDROIDX_NOTIFICATION_CLASSES = {
        "IconClass": "androidx.core.graphics.drawable.IconCompat",
        "NotificationCompat": "androidx.core.app.NotificationCompat",
        "NotificationManagerCompat": "androidx.core.app.NotificationManagerCompat",
        "NotificationCompatBuilder": "androidx.core.app.NotificationCompat$Builder",
        "NotificationCompatBigTextStyle": "androidx.core.app.NotificationCompat$BigTextStyle",
        "NotificationCompatBigPictureStyle": "androidx.core.app.NotificationCompat$BigPictureStyle",
        "NotificationCompatInboxStyle": "androidx.core.app.NotificationCompat$InboxStyle",
        "NotificationCompatDecoratedCustomViewStyle": "androidx.core.app.NotificationCompat$DecoratedCustomViewStyle",
    }

    _notification_class_map = None
    _lock = threading.Lock()
    _cache = {}

    def _get_notification_class_map():
        global _notification_class_map
        if _notification_class_map is None:
            if on_flet_app() or on_pydroid_app() or not has_androidx_dependency():
                _notification_class_map = _ANDROID_NOTIFICATION_CLASSES
            else:
                _notification_class_map = _ANDROIDX_NOTIFICATION_CLASSES
        return _notification_class_map

    class _LazyJavaClass:
        __slots__ = ("_python_name", "_java_name")

        def __init__(self, python_name, java_name=None):
            self._python_name = python_name
            self._java_name = java_name

        def _resolve_name(self):
            if self._java_name is not None:
                return self._java_name
            return _get_notification_class_map()[self._python_name]

        def _get(self):
            with _lock:
                name = self._python_name
                if name not in _cache:
                    _cache[name] = self._autoclass_or_facade()
                return _cache[name]

        def _autoclass_or_facade(self):
            try:
                return autoclass(self._resolve_name())
            except Exception:
                facade = importlib.import_module(".facade", package=__package__)
                return getattr(facade, self._python_name, None)

        def __getattr__(self, item):
            return getattr(self._get(), item)

        def __call__(self, *args, **kwargs):
            return self._get()(*args, **kwargs)

        def __repr__(self):
            return repr(self._get())

        def __bool__(self):
            return bool(self._get())

        def __eq__(self, other):
            if isinstance(other, _LazyJavaClass):
                return self._get() is other._get() or self._get() == other._get()
            return self._get() == other

        def __hash__(self):
            return hash(self._get())

    Bundle = _LazyJavaClass("Bundle", "android.os.Bundle")
    String = _LazyJavaClass("String", "java.lang.String")
    Intent = _LazyJavaClass("Intent", "android.content.Intent")
    PendingIntent = _LazyJavaClass("PendingIntent", "android.app.PendingIntent")
    BitmapFactory = _LazyJavaClass("BitmapFactory", "android.graphics.BitmapFactory")
    BuildVersion = _LazyJavaClass("BuildVersion", "android.os.Build$VERSION")
    NotificationManager = _LazyJavaClass("NotificationManager", "android.app.NotificationManager")
    NotificationChannel = _LazyJavaClass("NotificationChannel", "android.app.NotificationChannel")
    RemoteViews = _LazyJavaClass("RemoteViews", "android.widget.RemoteViews")
    Settings = _LazyJavaClass("Settings", "android.provider.Settings")
    Uri = _LazyJavaClass("Uri", "android.net.Uri")
    Manifest = _LazyJavaClass("Manifest", "android.Manifest$permission")
    Context = _LazyJavaClass("Context", "android.content.Context")
    PackageManager = _LazyJavaClass("PackageManager", "android.content.pm.PackageManager")
    AudioAttributes = _LazyJavaClass("AudioAttributes", "android.media.AudioAttributes")
    AudioAttributesBuilder = _LazyJavaClass("AudioAttributesBuilder", "android.media.AudioAttributes$Builder")
    File = _LazyJavaClass("File", "java.io.File")
    Color = _LazyJavaClass("Color", "android.graphics.Color")

    IconClass = _LazyJavaClass("IconClass")
    NotificationCompat = _LazyJavaClass("NotificationCompat")
    NotificationManagerCompat = _LazyJavaClass("NotificationManagerCompat")
    NotificationCompatBuilder = _LazyJavaClass("NotificationCompatBuilder")
    NotificationCompatBigTextStyle = _LazyJavaClass("NotificationCompatBigTextStyle")
    NotificationCompatBigPictureStyle = _LazyJavaClass("NotificationCompatBigPictureStyle")
    NotificationCompatInboxStyle = _LazyJavaClass("NotificationCompatInboxStyle")
    NotificationCompatDecoratedCustomViewStyle = _LazyJavaClass("NotificationCompatDecoratedCustomViewStyle")
else:
    cast = lambda x, y: x
    autoclass = lambda x: None

    class _LazyJavaClass:
        __slots__ = ("_python_name", "_java_name")

        def __init__(self, python_name, java_name=None):
            self._python_name = python_name
            self._java_name = java_name

        def _get(self):
            facade = importlib.import_module(".facade", package=__package__)
            return getattr(facade, self._python_name, None)

        def __getattr__(self, item):
            return getattr(self._get(), item)

        def __call__(self, *args, **kwargs):
            return self._get()(*args, **kwargs)

        def __repr__(self):
            return repr(self._get())

        def __bool__(self):
            return bool(self._get())

    # noinspection PyUnresolvedReferences
    from .facade import *
    logger.warning("Did not initialize java classes, Not on Android")
