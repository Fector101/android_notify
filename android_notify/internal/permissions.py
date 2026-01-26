"""
For Permission Related Blocks
"""
import os.path

from .logger import logger
from android_notify.config import on_android_platform, on_flet_app, get_python_activity_context
from android_notify.internal.java_classes import autoclass, BuildVersion, Manifest, Intent, String, Settings, Uri, PackageManager
from android_notify.internal.helper import execute_callback


def has_notification_permission():
    """
    Checks if device has permission to send notifications
    returns True if device has permission
    """
    if not on_android_platform():
        return True

    if BuildVersion.SDK_INT < 33:  # Android 12 below
        return True

    if on_flet_app():
        context = get_python_activity_context()
        permission = Manifest.POST_NOTIFICATIONS

        return PackageManager.PERMISSION_GRANTED == context.checkSelfPermission(permission)
    else:
        from android.permissions import Permission, check_permission  # type: ignore
        return check_permission(Permission.POST_NOTIFICATIONS)


def ask_notification_permission(callback=None, set_requesting_state=None, legacy=False):
    if not on_android_platform():
        logger.warning("Can't ask permission when not on android")
        execute_callback(callback, True)
        return None

    if BuildVersion.SDK_INT < 33:  # Android 12 below
        execute_callback(callback, True)
        logger.warning("On android 12 or less don't need permission")
        return None

    if has_notification_permission():
        execute_callback(callback, True)
        logger.warning("Already have permission to send notifications")
        return None

    if not is_first_permission_ask() and not can_show_permission_request_popup():
        logger.warning("""Permission to send notifications has been denied permanently.
        This can happen when the user denies permission twice from the popup.
        
        Opening notification settings...
        
        Add in MDApp().on_resume():
        >> if NotificationHandler.has_permission() and self.screen_manager:
        >>      self.screen_manager.current = "home_screen"
        """)
        open_notification_settings_screen()
        return None

    context = get_python_activity_context()

    def on_permissions_result(_, grants):
        # _ is permissions
        execute_callback(callback, grants[0])
        execute_callback(set_requesting_state, False,from_who="package")

    if legacy or on_flet_app():
        # TODO Handle activity with request code
        permission = Manifest.POST_NOTIFICATIONS
        context.requestPermissions([permission], 101)
        return None
    else:
        from android.permissions import request_permissions, Permission  # type: ignore
        execute_callback(set_requesting_state, True,from_who="package")
        request_permissions([Permission.POST_NOTIFICATIONS], on_permissions_result)
        return None


def open_notification_settings_screen():
    """In MDApp().on_resume()

    Example:
        >>> if NotificationHandler.has_permission() and self.screen_manager:
        >>>     self.screen_manager.current = "home_screen"
    """
    context = get_python_activity_context()

    if not context:
        logger.warning("Can't open settings screen, No context [not On Android]")
        return None
    intent = Intent()
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    package_name = String(context.getPackageName())  # String() is very important else fails silently with a toast
    # saying "The app wasn't found in the list of installed apps" - Xiaomi or "unable to find application to perform this action" - Samsung and Techno

    if BuildVersion.SDK_INT >= 26:  # Android 8.0 - android.os.Build.VERSION_CODES.O
        intent.setAction(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
        intent.putExtra(Settings.EXTRA_APP_PACKAGE, package_name)
    elif BuildVersion.SDK_INT >= 22:  # Android 5.0 - Build.VERSION_CODES.LOLLIPOP
        intent.setAction("android.settings.APP_NOTIFICATION_SETTINGS")
        intent.putExtra("app_package", package_name)
        intent.putExtra("app_uid", context.getApplicationInfo().uid)
    else:  # Last Retort is to open App Settings Screen
        intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.addCategory(Intent.CATEGORY_DEFAULT)
        intent.setData(Uri.parse("package:" + package_name))

    context.startActivity(intent)
    return None

    # https://stackoverflow.com/a/45192258/19961621


def can_show_permission_request_popup():
    """
    Check if we can show permission request popup for POST_NOTIFICATIONS
    :return: bool
    """

    context = get_python_activity_context()
    if not on_android_platform():
        return False

    if BuildVersion.SDK_INT < 33:
        return False

    return context.shouldShowRequestPermissionRationale(Manifest.POST_NOTIFICATIONS)


def is_first_permission_ask():
    from importlib.resources import files
    buffer_file_name = "ASKED_PERMISSION.txt"
    absolute_buffer_file_path = str(files("android_notify") / buffer_file_name) # Making sure one path is always used

    if os.path.exists(absolute_buffer_file_path):
        return False
    open(absolute_buffer_file_path,'w').close()
    return True
