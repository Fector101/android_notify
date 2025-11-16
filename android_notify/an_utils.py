"""Collection of useful functions"""

import inspect, os, re, traceback
from .config import autoclass
from .an_types import Importance
from .config import (
                     get_python_activity_context, app_storage_path,ON_ANDROID,
                     BitmapFactory, BuildVersion, Bundle,
                     NotificationManagerClass,AndroidNotification
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
        value = AndroidNotification.PRIORITY_HIGH if BuildVersion.SDK_INT <= 25 else NotificationManagerClass.IMPORTANCE_HIGH
    elif importance == 'high':
        value = AndroidNotification.PRIORITY_DEFAULT if BuildVersion.SDK_INT <= 25 else NotificationManagerClass.IMPORTANCE_DEFAULT
    elif importance == 'medium':
        value = AndroidNotification.PRIORITY_LOW if BuildVersion.SDK_INT <= 25 else NotificationManagerClass.IMPORTANCE_LOW
    elif importance == 'low':
        value = AndroidNotification.PRIORITY_MIN if BuildVersion.SDK_INT <= 25 else NotificationManagerClass.IMPORTANCE_MIN
    elif importance == 'none':
        value = '' if BuildVersion.SDK_INT <= 25 else NotificationManagerClass.IMPORTANCE_NONE

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
    img_full_path = os.path.join(app_folder, relative_path)
    img_name = os.path.basename(img_full_path)
    if not os.path.exists(img_full_path):
        print(f"\nImage - {img_name} not found at path: {app_folder}, (Local images gotten from App Path)")
        try:
            print("- These are the existing files in your app Folder:")
            print('[' + ', '.join(os.listdir(app_folder)) + ']')
        except Exception as could_not_get_files_in_path_error:
            print('Exception: ', could_not_get_files_in_path_error)
            print("Couldn't get Files in App Folder")
        return None
    return get_bitmap_from_path(img_full_path)
    # TODO test with a badly written Image and catch error

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
  if not res_sound_name:
    return None

  package_name = context.getPackageName()
  Uri = autoclass('android.net.Uri')
  return Uri.parse(f"android.resource://{package_name}/raw/{res_sound_name}")

def get_package_path():
    """
    Returns the directory path of this Python package.
    Works on Android, Windows, Linux, macOS.
    """
    return os.path.dirname(os.path.abspath(__file__))

def get_flet_fallback_icon_path():
    """
    Returns the full path to the fallback Flet icon:
    fallback-icons/flet-appicon.png
    """
    package_dir = get_package_path()
    return os.path.join(package_dir, "fallback-icons", "flet-appicon.png")

def get_bitmap_from_path(img_full_path):
  Uri = autoclass('android.net.Uri')
  uri = Uri.parse(f"file://{img_full_path}")
  return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))

def backup_icon_finder(icon_name):
    """Get the full path to an icon file"""
    import pkg_resources
    return pkg_resources.resource_filename(__name__, f'fallback-icons/{icon_name}')
