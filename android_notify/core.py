""" Non-Advanced Stuff """
import random
import os

from android_notify.internal.logger import logger
from android_notify.config import get_python_activity, on_android_platform, get_python_activity_context
from android_notify.internal.permissions import has_notification_permission, ask_notification_permission
from android_notify.internal.java_classes import autoclass, BuildVersion, BitmapFactory, NotificationChannel, NotificationManagerCompat, NotificationCompat, NotificationCompatBuilder, \
    NotificationCompatBigTextStyle, NotificationCompatBigPictureStyle, NotificationCompatInboxStyle



def on_flet_app():
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")


if on_android_platform():
    PythonActivity = get_python_activity()


def get_app_root_path():
    context = get_python_activity_context()
    if on_flet_app():
        path = os.path.join(context.getFilesDir().getAbsolutePath(), 'flet')
    else:
        try:
            from android.storage import app_storage_path  # type: ignore
            path = app_storage_path()
        except Exception as error_getting_app_storage_path:
            logger.exception(f'Error getting app main path: {error_getting_app_storage_path}')
            return './'
    return os.path.join(path, 'app')


def asks_permission_if_needed(legacy=False, no_androidx=False):
    """
    Ask for permission to send notifications if needed.
    legacy parameter will replace no_androidx parameter in Future Versions
    """
    if not has_notification_permission():
        ask_notification_permission(legacy=legacy or no_androidx)


def get_image_uri(relative_path):
    """
    Get the absolute URI for an image in the app assets folder.
    :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
    :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
    """
    app_root_path = get_app_root_path()
    output_path = os.path.join(app_root_path, relative_path)
    # drint(output_path,'output_path')  # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"\nImage not found at path: {output_path}\n")

    Uri = autoclass('android.net.Uri')
    return Uri.parse(f"file://{output_path}")


def get_icon_object(uri):
    context = get_python_activity_context()
    IconCompat = autoclass('android.graphics.drawable.Icon')
    bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))
    return IconCompat.createWithBitmap(bitmap)


def insert_app_icon(builder, custom_icon_path):
    context = get_python_activity_context()

    if custom_icon_path:
        try:
            uri = get_image_uri(custom_icon_path)
            icon = get_icon_object(uri)
            builder.setSmallIcon(icon)
        except Exception as error_getting_custom_small_icon:
            logger.exception(f'Failed getting custom icon: {error_getting_custom_small_icon}')
            builder.setSmallIcon(context.getApplicationInfo().icon)
    else:
        builder.setSmallIcon(context.getApplicationInfo().icon)


def send_notification(
        title: str,
        message: str,
        style=None,
        img_path=None,
        channel_name="Default Channel",
        channel_id: str = "default_channel",
        custom_app_icon_path="",

        big_picture_path='',
        large_icon_path='',
        big_text="",
        lines=""
):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: deprecated.
    :param img_path: Path to the image resource.
    :param channel_id: Notification channel ID.(Default is lowercase channel name arg in lowercase)
    :param channel_name: Notification channel name.
    :param custom_app_icon_path: Path to the custom app icon.
    :param big_picture_path: Path to the big picture.
    :param large_icon_path: Path to the large icon.
    :param big_text: Str to the big text.
    :param lines: Str to the lines.
    """
    if not on_android_platform():
        logger.warning(
            'This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.')
        return None
    context = get_python_activity_context()

    asks_permission_if_needed(legacy=True)
    channel_id = channel_name.replace(' ', '_').lower().lower() if not channel_id else channel_id
    # Get notification manager
    notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)

    # importance= autoclass('android.app.NotificationManager').IMPORTANCE_HIGH # also works #NotificationManager.IMPORTANCE_DEFAULT
    importance = NotificationManagerCompat.IMPORTANCE_HIGH  # autoclass('android.app.NotificationManager').IMPORTANCE_HIGH also works #NotificationManager.IMPORTANCE_DEFAULT

    # Notification Channel (Required for Android 8.0+)
    if BuildVersion.SDK_INT >= 26:
        channel = NotificationChannel(channel_id, channel_name, importance)
        notification_manager.createNotificationChannel(channel)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentText(message)
    insert_app_icon(builder, custom_app_icon_path)
    builder.setDefaults(NotificationCompat.DEFAULT_ALL)
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)

    if img_path:
        logger.warning( '"img_path" arg deprecated use "large_icon_path or big_picture_path or custom_app_icon_path" instead')
    if style:
        logger.warning( '"style" arg deprecated use args "big_picture_path", "large_icon_path", "big_text", "lines" instead')

    big_picture = None
    if big_picture_path:
        try:
            big_picture = get_image_uri(big_picture_path)
        except FileNotFoundError as error_getting_img_uri_BIGPIC:
            logger.exception(f'Error Getting Uri for big_picture_path: {error_getting_img_uri_BIGPIC}')

    large_icon = None
    if large_icon_path:
        try:
            large_icon = get_image_uri(large_icon_path)
        except FileNotFoundError as error_getting_img_uri_LARGEICON:
            logger.exception(f'Error Getting Uri for large_icon_path: {error_getting_img_uri_LARGEICON}')

    # Apply notification styles
    try:
        if big_text:
            big_text_style = NotificationCompatBigTextStyle()
            big_text_style.bigText(big_text)
            builder.setStyle(big_text_style)

        elif lines:
            inbox_style = NotificationCompatInboxStyle()
            for line in lines.split("\n"):
                inbox_style.addLine(line)
            builder.setStyle(inbox_style)

        if large_icon:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(large_icon))
            builder.setLargeIcon(bitmap)

        if big_picture:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(big_picture))
            big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
            builder.setStyle(big_picture_style)

    except Exception as error_adding_style:
        logger.exception(f'Error Failed Adding Style: {error_adding_style}')
    # Display the notification
    notification_id = random.randint(0, 100)
    notification_manager.notify(notification_id, builder.build())
    return notification_id
