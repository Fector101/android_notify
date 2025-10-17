""" Non-Advanced Stuff """
import random
import os
ON_ANDROID = False

def get_activity_class_name():
    ACTIVITY_CLASS_NAME = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME") # flet python
    if not ACTIVITY_CLASS_NAME:
        try:
            from android import config
            ACTIVITY_CLASS_NAME = getattr(config, "JAVA_NAMESPACE", None)
        except (ImportError, AttributeError):
            ACTIVITY_CLASS_NAME = 'org.kivy.android'
    return ACTIVITY_CLASS_NAME

try:

    from jnius import autoclass # Needs Java to be installed
    # Get the required Java classes
    ACTIVITY_CLASS_NAME = get_activity_class_name()
    PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
    context = PythonActivity.mActivity # Get the app's context 
    NotificationChannel = autoclass('android.app.NotificationChannel')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')    
    ON_ANDROID=True
except Exception as e:
    print('\nThis Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.\n')

if ON_ANDROID:
    try:
        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')                                       
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')

        # Notification Design
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
    except Exception as e:
        print("""\n
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS\n
        """)

def asks_permission_if_needed():
    """
    Ask for permission to send notifications if needed.
    """
    from android.permissions import request_permissions, Permission,check_permission # type: ignore

    permissions=[Permission.POST_NOTIFICATIONS]
    if not all(check_permission(p) for p in permissions):
        request_permissions(permissions)

def get_image_uri(relative_path):
    """
    Get the absolute URI for an image in the assets folder.
    :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
    :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
    """
    from android.storage import app_storage_path # type: ignore

    output_path = os.path.join(app_storage_path(),'app', relative_path)
    # print(output_path,'output_path')  # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png
    
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Image not found at path: {output_path}")
    
    Uri = autoclass('android.net.Uri')
    return Uri.parse(f"file://{output_path}")


def send_notification(
    title:str,
    message:str,
    style=None,
    img_path=None,
    channel_name="Default Channel",
    channel_id:str="default_channel"
    ):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: Style of the notification ('big_text', 'big_picture', 'inbox', 'large_icon').
    :param img_path: Path to the image resource.
    :param channel_id: Notification channel ID.(Default is lowercase channel name arg in lowercase)
    """
    if not ON_ANDROID:
        print('This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.')
        return
    
    if not ("MAIN_ACTIVITY_HOST_CLASS_NAME" in os.environ):
        asks_permission_if_needed() # android package is from p4a which is for kivy
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
    builder.setSmallIcon(context.getApplicationInfo().icon)
    builder.setDefaults(NotificationCompat.DEFAULT_ALL)
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)
    
    img=None
    if img_path:
        try:
            img = get_image_uri(img_path)
        except FileNotFoundError as e:
            print('Failed Adding Bitmap: ',e)
    
    # Apply notification styles
    try:
        if style == "big_text":
            big_text_style = NotificationCompatBigTextStyle()
            big_text_style.bigText(message)
            builder.setStyle(big_text_style)
        elif style == "big_picture" and img_path:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img))
            builder.setLargeIcon(bitmap)
            big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
            builder.setStyle(big_picture_style)
        elif style == "inbox":
            inbox_style = NotificationCompatInboxStyle()
            for line in message.split("\n"):
                inbox_style.addLine(line)
            builder.setStyle(inbox_style)
        elif style == "large_icon" and img_path:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img))
            builder.setLargeIcon(bitmap)
    except Exception as e:
        print('Failed Adding Style: ',e)
    # Display the notification
    notification_id = random.randint(0, 100)
    notification_manager.notify(notification_id, builder.build())
    return notification_id

