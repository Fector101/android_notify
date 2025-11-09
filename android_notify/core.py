""" Non-Advanced Stuff """
import random
import os, traceback
from .config import get_python_activity
ON_ANDROID = False

def on_flet_app():
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")


try:

    from jnius import autoclass # Needs Java to be installed
    PythonActivity = get_python_activity()
    context = PythonActivity.mActivity # Get the app's context 
    NotificationChannel = autoclass('android.app.NotificationChannel')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    Notification = autoclass("android.app.Notification")
    ON_ANDROID=True
except Exception as e:
    traceback.print_exc()
    print(e,'\nThis Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.\n')

if ON_ANDROID:
    try:
        NotificationManagerCompat = autoclass('android.app.NotificationManager')                                       
        # Notification Design
        NotificationCompatBuilder = autoclass('android.app.Notification$Builder')
        NotificationCompatBigTextStyle = autoclass('android.app.Notification$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('android.app.Notification$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('android.app.Notification$InboxStyle')
    except Exception as e:
        traceback.print_exc()
        print("Error importing notification styles")


def get_app_root_path():
    path = ''
    if on_flet_app():
        path= os.path.join(context.getFilesDir().getAbsolutePath(),'flet')
    else:
        try:
            from android.storage import app_storage_path # type: ignore
            path = app_storage_path()
        except Exception as e:
            print('android-notify- Error getting apk main file path: ',e)
            return './'
    return os.path.join(path,'app')

def asks_permission_if_needed(no_androidx=False):
    """
    Ask for permission to send notifications if needed.
    """
    if on_flet_app() or no_androidx:
        Activity = autoclass("android.app.Activity")
        Manifest = autoclass("android.Manifest$permission")
        PackageManager = autoclass("android.content.pm.PackageManager")
        VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')

        if BuildVersion.SDK_INT >= VERSION_CODES.TIRAMISU:
            permission = Manifest.POST_NOTIFICATIONS
            granted = context.checkSelfPermission(permission)

            if granted != PackageManager.PERMISSION_GRANTED:
                context.requestPermissions([permission], 101)
    else: # android package is from p4a which is for kivy
        try:
            from android.permissions import request_permissions, Permission,check_permission # type: ignore
            permissions=[Permission.POST_NOTIFICATIONS]
            if not all(check_permission(p) for p in permissions):
                request_permissions(permissions)
        except Exception as e:
            print("android_notify- error trying to request notification access: ", e)

def get_image_uri(relative_path):
    """
    Get the absolute URI for an image in the assets folder.
    :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
    :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
    """
    app_root_path = get_app_root_path() 
    output_path = os.path.join(app_root_path, relative_path)
    # print(output_path,'output_path')  # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png
    
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"\nImage not found at path: {output_path}\n")
    
    Uri = autoclass('android.net.Uri')
    return Uri.parse(f"file://{output_path}")

def get_icon_object(uri):
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')

    bitmap= BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))
    return IconCompat.createWithBitmap(bitmap)

def insert_app_icon(builder,custom_icon_path):
    if custom_icon_path:
        try:
            uri = get_image_uri(custom_icon_path)
            icon = get_icon_object(uri)
            builder.setSmallIcon(icon)
        except Exception as e:
            print('android_notify- error: ',e)
            builder.setSmallIcon(context.getApplicationInfo().icon)
    else:
        # print('Found res icon -->',context.getApplicationInfo().icon,'<--')
        builder.setSmallIcon(context.getApplicationInfo().icon)

def send_notification(
    title:str,
    message:str,
    style=None,
    img_path=None,
    channel_name="Default Channel",
    channel_id:str="default_channel",
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
    """
    if not ON_ANDROID:
        print('This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.')
        return

    asks_permission_if_needed(no_androidx=True)
    channel_id=channel_name.replace(' ','_').lower().lower() if not channel_id else channel_id
    # Get notification manager
    notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)

    # importance= autoclass('android.app.NotificationManager').IMPORTANCE_HIGH # also works #NotificationManager.IMPORTANCE_DEFAULT
    importance= NotificationManagerCompat.IMPORTANCE_HIGH #autoclass('android.app.NotificationManager').IMPORTANCE_HIGH also works #NotificationManager.IMPORTANCE_DEFAULT

    # Notification Channel (Required for Android 8.0+)
    if BuildVersion.SDK_INT >= 26:
        channel = NotificationChannel(channel_id, channel_name,importance)
        notification_manager.createNotificationChannel(channel)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentText(message)
    insert_app_icon(builder,custom_app_icon_path)
    builder.setDefaults(Notification.DEFAULT_ALL)
    builder.setPriority(Notification.PRIORITY_HIGH)

    if img_path:
        print('android_notify- img_path arg deprecated use "large_icon_path or big_picture_path or custom_app_icon_path" instead')
    if style:
        print('android_notify- "style" arg deprecated use args "big_picture_path", "large_icon_path", "big_text", "lines" instead')

    big_picture = None
    if big_picture_path:
        try:
            big_picture = get_image_uri(big_picture_path)
        except FileNotFoundError as e:
            print('android_notify- Error Getting Uri for big_picture_path: ',e)

    large_icon = None
    if large_icon_path:
        try:
            large_icon = get_image_uri(large_icon_path)
        except FileNotFoundError as e:
            print('android_notify- Error Getting Uri for large_icon_path: ',e)


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

    except Exception as e:
        print('android_notify- Error Failed Adding Style: ',e)
    # Display the notification
    notification_id = random.randint(0, 100)
    notification_manager.notify(notification_id, builder.build())
    return notification_id

