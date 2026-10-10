"""
For Permission Related Blocks
"""
import os.path
import traceback

from .logger import logger
from android_notify.config import on_android_platform, on_flet_app, get_python_activity_context, on_pydroid_app, \
    has_androidx_dependency, get_package_name
from android_notify.internal.java_classes import autoclass, BuildVersion, Manifest, Intent, String, Settings, Uri, PackageManager, NotificationManagerCompat, Context
from android_notify.internal.helper import execute_callback


def check_notification_permission_legacy_android12_below():
    # Below Android 13 there is no POST_NOTIFICATIONS runtime permission
    # so check the per-app notification enabled state instead.
    if BuildVersion.SDK_INT < 24:
        # NotificationManager.areNotificationsEnabled() only exists on API 24+
        # (before that there is no per-app notification toggle -> always on).
        return True
    context = get_python_activity_context()
    notification_service = context.getSystemService(Context.NOTIFICATION_SERVICE)
    return notification_service.areNotificationsEnabled()

def check_notification_permission_androidx_android12_below():
    if BuildVersion.SDK_INT < 24:
        # NotificationManagerCompat.areNotificationsEnabled() delegates to the
        # platform API-24+ method; before that notifications are always enabled.
        return True
    context = get_python_activity_context()
    func_from = getattr(NotificationManagerCompat, "from")
    compat_manager = func_from(context)
    return compat_manager.areNotificationsEnabled()

def check_notification_permission_legacy_android12_above():
    # NotificationManagerCompat is actually NotificationManager from android_notify.internal.java_classes
    context = get_python_activity_context()
    permission = Manifest.POST_NOTIFICATIONS
    return PackageManager.PERMISSION_GRANTED == context.checkSelfPermission(permission)

def check_notification_permission_androidx_android12_above():
    # Unused keeping for future reference
    context = get_python_activity_context()
    permission = Manifest.POST_NOTIFICATIONS
    ContextCompat = autoclass('androidx.core.content.ContextCompat')
    # For flet
    # if you get error `Failed to find class: androidx/core/app/ActivityCompat`
    # in proguard-rules.pro add `-keep class androidx.core.app.ActivityCompat { *; }`
    return ContextCompat.checkSelfPermission(context, permission)

def ask_notification_permission_androidx():
    # Unused keeping for future reference
    # TODO Callback when user answers request question
    # Can't bind activity result method is from p4a which is only on kivy
    context = get_python_activity_context()
    ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
    permission = Manifest.POST_NOTIFICATIONS
    ActivityCompat.requestPermissions(context, [permission], 101)
    return None

def has_notification_permission():
    """
    Checks if device has permission to send notifications
    returns True if device has permission
    """
    if not on_android_platform():
        return True

    if BuildVersion.SDK_INT < 33:  # Android 12 and below
        try:
            if on_flet_app() or on_pydroid_app() or not has_androidx_dependency():
                return check_notification_permission_legacy_android12_below()
            elif has_androidx_dependency():
                return check_notification_permission_androidx_android12_below()
        except Exception as error_checking_permission:
            logger.exception(f"On Android 12 and below Error checking permission: {error_checking_permission}")
            traceback.print_exc()
            return True  # Assuming permission is granted if error occurs

    # if on_flet_app() or on_pydroid_app() or not has_androidx_dependency():
    return check_notification_permission_legacy_android12_above()
    # else:
        # from android.permissions import Permission # type: ignore
        # return check_permission(Permission.POST_NOTIFICATIONS) # failed in kivy service file: AttributeError: 'NoneType' object has no attribute 'checkCurrentPermission'

def ask_notification_permission(callback=None, set_requesting_state=None, legacy=False):
    if not on_android_platform():
        logger.warning("Can't ask permission when not on android")
        execute_callback(callback, True)
        return None

    if has_notification_permission():
        execute_callback(callback, True)
        logger.warning("Already have permission to send notifications")
        return None

    if BuildVersion.SDK_INT < 33:  # Android 12 and below
        logger.warning("""
        Can't show popup below Android 13, Opening Notification setting...
        
        Add in App().on_resume():
        >> if NotificationHandler.has_permission() and self.screen_manager:
        >>      self.screen_manager.current = "home_screen"
        """)
        open_notification_settings_screen()
        return None

    if not is_first_permission_ask() and not can_show_permission_request_popup(Manifest.POST_NOTIFICATIONS):
        logger.warning("""Permission to send notifications has been denied permanently.
        This can happen when the user denies permission twice from the popup.
        
        Opening notification settings...
        
        Add in App().on_resume():
        >> if NotificationHandler.has_permission() and self.screen_manager:
        >>      self.screen_manager.current = "home_screen"
        """)
        open_notification_settings_screen()
        return None

    context = get_python_activity_context()

    def on_permissions_result(_, grants):
        # _ is permissions, note: grants was empty in cli test
        execute_callback(callback, grants[0] if len(grants) else True)
        execute_callback(set_requesting_state, False,from_who="package")

    if legacy or on_flet_app() or on_pydroid_app():
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
    """In App().on_resume()

    Example:
        >>> if NotificationHandler.has_permission() and screen_manager:
        >>>     # navigate to another screen in your app, if showing your-self designed request screen
    """
    context = get_python_activity_context()

    if not context:
        logger.warning("Can't open settings screen, No context [not On Android]")
        return None
    intent = Intent()
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    package_name = String(get_package_name())  # String() is very important else fails silently with a toast
    # saying "The app wasn't found in the list of installed apps" - Xiaomi or "unable to find application to perform this action" - Samsung and Techno

    if BuildVersion.SDK_INT >= 26:  # Android 8.0 - android.os.Build.VERSION_CODES.O
        intent.setAction(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
        intent.putExtra(Settings.EXTRA_APP_PACKAGE, package_name)
    elif BuildVersion.SDK_INT >= 22:  # Android 5.0 - Build.VERSION_CODES.LOLLIPOP
        intent.setAction(String("android.settings.APP_NOTIFICATION_SETTINGS"))
        intent.putExtra(String("app_package"), package_name)
        intent.putExtra(String("app_uid"), context.getApplicationInfo().uid)
    else:  # Last Retort is to open App Settings Screen
        intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.addCategory(Intent.CATEGORY_DEFAULT)
        intent.setData(Uri.parse("package:" + get_package_name()))

    context.startActivity(intent)
    return None

    # https://stackoverflow.com/a/45192258/19961621

def open_audio_settings_screen():
    """In App().on_resume()

    Example:
        >>> if MediaPermissionHandler.has_permission_to_access_audio_files() and screen_manager:
        >>      # navigate to another screen in your app, if showing your-self designed request screen
    """
    context = get_python_activity_context()
    package_name = String(get_package_name()) # needed for android to understand str

    if not context:
        logger.warning("Can't open settings screen, No context [not On Android]")
        return None
    intent = Intent()
    intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    intent.putExtra(Settings.EXTRA_APP_PACKAGE, package_name)
    intent.setData(Uri.parse("package:" + get_package_name()))

    context.startActivity(intent)
    return None

def can_show_permission_request_popup(permission):
    """
    Check if we can show permission request popup for POST_NOTIFICATIONS
    :return: bool
    """

    context = get_python_activity_context()
    if not on_android_platform():
        return False

    if BuildVersion.SDK_INT < 33 and permission == Manifest.POST_NOTIFICATIONS:
        logger.warning("On android 12 or less, Can't show permission request popup")
        return False

    return context.shouldShowRequestPermissionRationale(permission)

def is_first_permission_ask(base="ASKED_PERMISSION.txt"):
    buffer_file_name = base # "ASKED_PERMISSION.txt" is for general notification permission, base can be for audio files,...

    context = get_python_activity_context()
    if not context:
        logger.warning("Can't check permission ask state, no Android context")
        return True

    files_dir = str(context.getFilesDir().getAbsolutePath())
    absolute_buffer_file_path = os.path.join(
        files_dir,
        "android_notify",
        buffer_file_name,
    )

    os.makedirs(os.path.dirname(absolute_buffer_file_path), exist_ok=True)

    if os.path.exists(absolute_buffer_file_path):
        return False

    open(absolute_buffer_file_path, "w").close()
    return True

def is_permission_in_manifest(permission_name)->bool:
    """
    Checks if permission is in AndroidManifest.xml, to avoid errors and provide better logging
    :param permission_name: android permission name
    :return: true if permission is in AndroidManifest.xml
    """
    # Assuming True on failure, package worked flawlessly without this function, I'm adding it for better logging
    context = get_python_activity_context()
    if not context:
        logger.warning("Can't check permission ask state, no Android context")
        return True # Assuming user is on desktop
    try:
        package_info = context.getPackageManager().getPackageInfo(
            get_package_name(), PackageManager.GET_PERMISSIONS
        )
    except Exception as error_getting_package_info:
        logger.error(error_getting_package_info)
        return True
    requested_permissions = package_info.requestedPermissions
    if requested_permissions is None:
        return True

    state = any(str(p) == permission_name for p in requested_permissions)
    logger.info(f"In manifest state: {state}, permission: {permission_name}")
    return state

def is_music_permission_in_manifest() -> bool:
    """
    Checks if READ_EXTERNAL_STORAGE in manifest on android 12 and below or
    Checks if READ_MEDIA_AUDIO in manifest on android 13 and higher
    :return: True if it exists, False otherwise
    """
    # Assuming True on failure, I'm adding it for better logging
    state = True
    try:
        if BuildVersion.SDK_INT < 33: # Less than Android 13
            state = is_permission_in_manifest(Manifest.READ_EXTERNAL_STORAGE)
            logger.debug("READ_EXTERNAL_STORAGE state: " + str(state))
        else:
            state = is_permission_in_manifest(Manifest.READ_MEDIA_AUDIO)
            logger.debug("READ_MEDIA_AUDIO state: " + str(state))
    except Exception as error_getting_audio_permission_in_manifest:
        logger.error(error_getting_audio_permission_in_manifest)

    if not state:
        logger.warning("Add Permissions to buildozer.spec, android.permissions = (name=android.permission.READ_EXTERNAL_STORAGE;maxSdkVersion=32), READ_MEDIA_AUDIO")
    return state

def has_permission_to_read_audio() -> bool:
    """
    Checks if app has permission to read the audio files
    :return: True if it's allowed, False otherwise
    """
    if not on_android_platform():
        return True
    context = get_python_activity_context()
    if BuildVersion.SDK_INT < 33: # Less than Android 13
        permission = Manifest.READ_EXTERNAL_STORAGE
    else:
        permission = Manifest.READ_MEDIA_AUDIO
    return PackageManager.PERMISSION_GRANTED == context.checkSelfPermission(permission)

def ask_audio_permission(callback=None, set_requesting_state=None):
    """
    Asks permission to read the audio files, using right pattern for android versions
    """
    if not on_android_platform():
        logger.warning("Can't ask permission when not on android")
        execute_callback(callback, True)
        return None

    if has_permission_to_read_audio():
        execute_callback(callback, True)
        logger.warning("App already has permission to read audio")
        return None


    if BuildVersion.SDK_INT < 33: # Less than Android 13
        permissions = [Manifest.READ_EXTERNAL_STORAGE]
    else:
        permissions = [Manifest.READ_MEDIA_AUDIO]

    if not is_first_permission_ask("AUDIO_PERMISSION.txt") and not can_show_permission_request_popup(permissions[0]):
        logger.warning("""
        Permission to access audio has been denied permanently.
        This can happen when the user denies permission twice from the popup.

        Opening audio access settings...

        Add in App().on_resume():
        >> if MediaPermissionHandler.has_permission_to_access_audio_files() and screen_manager:
        >>      # navigate to another screen in your app, if showing your-self designed request screen
        """)
        open_audio_settings_screen()
        return None

    context = get_python_activity_context()

    def on_permissions_result(_, grants):
        # _ is permissions, note: grants was empty in cli test
        execute_callback(callback, grants[0] if len(grants) else True)
        execute_callback(set_requesting_state, False, from_who="package")

    if on_flet_app() or on_pydroid_app():
        # # TODO Handle activity with request code
        context.requestPermissions(permissions, 101)
        return None
    else:
        from android.permissions import request_permissions  # type: ignore
        execute_callback(set_requesting_state, True, from_who="package")
        request_permissions(permissions, on_permissions_result)
        return None



# TODO: Experiment with this data from google
# | Method Name | Targets Self? | Targets External Caller? | Best Used For |
# |---|---|---|---|
# | ContextCompat.checkSelfPermission | Yes | No | Standard internal features (Local Service/Activity). |
# | checkCallingPermission | No | Yes | Remote Service endpoints / AIDL binders. |
# | checkCallingOrSelfPermission | Yes (as fallback) | Yes (during IPC) | Dual-purpose local/remote operations (Use with caution). |

