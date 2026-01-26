"""
For image related things
"""
import os

from android_notify.config import app_storage_path, on_flet_app, on_android_platform, get_python_activity_context
from android_notify.internal.java_classes import autoclass, BitmapFactory, Uri, BuildVersion, Color
from android_notify.internal.helper import get_package_path
from android_notify.internal.logger import logger


def get_img_absolute_path(relative_path):
    app_folder = os.path.join(app_storage_path(), 'app')
    img_full_path = os.path.join(app_folder, relative_path) # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png
    if not os.path.exists(img_full_path):
        logger.warning(f'Image: "{img_full_path}" Not Found, (Local images gotten from App Path)')
        try:
            logger.warning("These are the existing files in your app Folder:")
            print('[' + ', '.join(os.listdir(app_folder)) + ']')
        except Exception as could_not_get_files_in_path_error:
            logger.warning("Couldn't get Files in App Folder")
            logger.exception(f'Exception: {could_not_get_files_in_path_error}')
        return None
    return img_full_path
    # return get_bitmap_from_path(img_full_path)
    # TODO test with a badly written Image and catch error


def get_bitmap_from_url(url, callback):
    """Gets Bitmap from url

    Args:
        :param url: img url
        :param callback: function to be called after thread done, callback receives bitmap data as argument
    """
    logger.info("getting Bitmap from URL")
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
            callback(None)
            logger.error('No Bitmap gotten from URL')
    except Exception as failed_to_get_bitmap_from_url:
        callback(None)
        # TODO get all types of JAVA Error that can fail here
        logger.exception(failed_to_get_bitmap_from_url)


def get_bitmap_from_path(img_full_path):
    """
    Gets bitmap from path
    :return: Bitmap if successful, else False
    """
    context = get_python_activity_context()
    try:
        uri = Uri.parse(f"file://{img_full_path}")
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))
    except Exception as extracting_bitmap_frm_path_error:
        logger.exception(extracting_bitmap_frm_path_error)
        return False


def icon_finder(icon_name):
    """Get the full path to an icon file."""
    # Leaving this as a broad Exception for unforeseen case so apps don't crash
    # noinspection PyBroadException
    try:
        # noinspection PyPackageRequirements
        from importlib.resources import files
        return str(files("android_notify")/"fallback-icons"/icon_name)
    except Exception:
        # Fallback if pkg_resources not available
        package_dir = get_package_path()
        return os.path.join(package_dir, "fallback-icons", icon_name)


def set_default_small_icon(builder):
    context = get_python_activity_context()
    builder.setSmallIcon(context.getApplicationInfo().icon)


def find_and_set_default_icon(builder):
    """
    Logic for finding small icon
    """

    fallback_icon_path = None
    if on_flet_app():
        fallback_icon_path = icon_finder("flet-appicon.png")
    elif "ru.iiec.pydroid3" in os.path.dirname(os.path.abspath(__file__)):
        fallback_icon_path = icon_finder("pydroid3-appicon.png")

    if fallback_icon_path:
        successful = set_small_icon_from_path(image_absolute_path=fallback_icon_path, builder=builder)
        if not successful:
            logger.warning("issue using fallback_appicon, using default icon...")
            set_default_small_icon(builder)

    else:
        set_default_small_icon(builder)


def set_small_icon_from_path(image_absolute_path, builder):
    """
    Uses Image Absolute path to set small icon
    :return: Boolean if icon was successfully set
    """
    bitmap = get_bitmap_from_path(image_absolute_path)
    if bitmap:
        result = set_small_icon_with_bitmap(bitmap, builder)
        return result
    return False


def set_small_icon_with_bitmap(bitmap, builder):
    """
    Uses Bitmap to set small icon
    :return: Boolean if icon was successfully set
    """
    if BuildVersion.SDK_INT < 23:
        logger.warning("Bitmap Insert as Icon Not available below Android 6")
        return False
    try:
        IconCompat = autoclass('android.graphics.drawable.Icon')
        icon = IconCompat.createWithBitmap(bitmap)
        builder.setSmallIcon(icon)
        return True
    except Exception as autoclass_icon_error:
        logger.exception(f"Couldn't find class to set custom icon: {autoclass_icon_error}")
        set_default_small_icon(builder)
        return False


def set_small_icon_color(builder, color: str):
    """
    Sets Notification accent color, visible change in SmallIcon color
    :param builder: Builder instance
    :param color:  str - red,pink,... (to be safe use hex code)
    """
    if on_android_platform():
        builder.setColor(Color.parseColor(color))
    logger.info(f'new notification icon color: {color}')
