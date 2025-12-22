"""Collection of useful functions"""

import inspect, os, re, traceback
from .config import autoclass
from .an_types import Importance
from .config import (
                     get_python_activity_context, app_storage_path,ON_ANDROID,
                     BitmapFactory, BuildVersion, Bundle,
                     NotificationManagerCompat,NotificationCompat,
                     Intent, Settings, Uri, String, Manifest
                    )

if ON_ANDROID:
    Color = autoclass('android.graphics.Color')
else:
    from .an_types import Color

def can_accept_arguments(func, *args, **kwargs):
    try:
        sig = inspect.signature(func)
        sig.bind(*args, **kwargs)
        return True
    except TypeError:
        return False

if ON_ANDROID:
    context = get_python_activity_context()
else:
    context = None

def get_android_importance(importance: Importance):
    """
    Returns Android Importance Values
    :param importance: ['urgent','high','medium','low','none']
    :return: Android equivalent int or empty str
    """
    if not ON_ANDROID:
        return None
    value = ''
    if importance == 'urgent':
        value = NotificationCompat.PRIORITY_HIGH if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_HIGH
    elif importance == 'high':
        value = NotificationCompat.PRIORITY_DEFAULT if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_DEFAULT
    elif importance == 'medium':
        value = NotificationCompat.PRIORITY_LOW if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_LOW
    elif importance == 'low':
        value = NotificationCompat.PRIORITY_MIN if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_MIN
    elif importance == 'none':
        value = '' if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_NONE

    return value
    # side-note 'medium' = NotificationCompat.PRIORITY_LOW and 'low' = NotificationCompat.PRIORITY_MIN # weird but from docs

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

def get_img_from_path(relative_path):
    app_folder = os.path.join(app_storage_path(), 'app')
    output_path = os.path.join(app_folder, relative_path)
    if not os.path.exists(output_path):
        print(f"\nImage not found at path: {app_folder}, (Local images gotten from App Path)")
        try:
            print("- These are the existing files in your app Folder:")
            print('[' + ', '.join(os.listdir(app_folder)) + ']')
        except Exception as could_not_get_files_in_path_error:
            print('Exception: ', could_not_get_files_in_path_error)
            print("Couldn't get Files in App Folder")
        return None
    # TODO test with a badly written Image and catch error
    uri = Uri.parse(f"file://{output_path}")
    return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))

def setLayoutText(layout, id, text, color):
    # checked if self.title_color available before entering method
    if id and text:
        layout.setTextViewText(id, text)
        if color:
            layout.setTextColor(id, Color.parseColor(color))

def get_bitmap_from_url(url, callback, logs):
    """Gets Bitmap from url

    Args:
        :param url: img url
        :param callback: function to be called after thread done, callback receives bitmap data as argument
        :param logs:
    """
    if logs:
        print("getting Bitmap from URL---")
    try:
        URL = autoclass('java.net.URL')
        url = URL(url)
        connection = url.openConnection()
        connection.connect()
        input_stream = connection.getInputStream()
        bitmap = BitmapFactory.decodeStream(input_stream)
        input_stream.close()
        if bitmap:
            callback(bitmap)
        else:
            print('Error No Bitmap for small icon ------------')
    except Exception as extracting_bitmap_frm_URL_error:
        callback(None)
        # TODO get all types of JAVA Error that can fail here
        print('Error Type ', extracting_bitmap_frm_URL_error)
        print('Failed to get Bitmap from URL ', traceback.format_exc())

def add_data_to_intent(intent, title):
    """Persist Some data to notification object for later use"""
    bundle = Bundle()
    bundle.putString("title", title or 'Title Placeholder')
    # bundle.putInt("notify_id", self.__id)
    bundle.putInt("notify_id", 101)
    intent.putExtras(bundle)


def get_sound_uri(res_sound_name):
  if not res_sound_name: # Incase it's None
    return None

  package_name = context.getPackageName()
  return Uri.parse(f"android.resource://{package_name}/raw/{res_sound_name}")

def can_show_permission_request_popup():
    """
    Check if we can show permission request popup for POST_NOTIFICATIONS
    :return: bool
    """
    if not ON_ANDROID:
        return False
    
    if BuildVersion.SDK_INT < 33:
        return False

    return context.shouldShowRequestPermissionRationale(Manifest.POST_NOTIFICATIONS)


def open_settings_screen():
    if not context:
        print("android_notify - Can't open settings screen, No context [not On Android]")
        return None
    intent = Intent()
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    package_name = String(context.getPackageName())    # String() is very important else fails silently with a toast
    # saying "The app wasn't found in the list of installed apps" - Xiaomi or "unable to find application to perform this action" - Samsung and Techno

    if BuildVersion.SDK_INT >= 26:    # Android 8.0 - android.os.Build.VERSION_CODES.O
        intent.setAction(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
        intent.putExtra(Settings.EXTRA_APP_PACKAGE, package_name)
    elif BuildVersion.SDK_INT >= 22:    # Android 5.0 - Build.VERSION_CODES.LOLLIPOP
        intent.setAction("android.settings.APP_NOTIFICATION_SETTINGS")
        intent.putExtra("app_package", package_name)
        intent.putExtra("app_uid", context.getApplicationInfo().uid)
    else:    # Last Retort is to open App Settings Screen
        intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.addCategory(Intent.CATEGORY_DEFAULT)
        intent.setData(Uri.parse("package:" + package_name))

    context.startActivity(intent)
    return None

    # https://stackoverflow.com/a/45192258/19961621
