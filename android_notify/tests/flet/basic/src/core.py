""" Non-Advanced Stuff """
import random
import os
ON_ANDROID = False

def on_flet_app():
    return os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")

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


def get_app_root_path():
    if on_flet_app():
        return os.path.join(context.getFilesDir().getAbsolutePath(),'flet')
    else:
        from android.storage import app_storage_path # type: ignore
        return app_storage_path()
    
def asks_permission_if_needed():
    """
    Ask for permission to send notifications if needed.
    """
    if on_flet_app():
        VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        # if you get error `Failed to find class: androidx/core/app/ActivityCompat`
        #in proguard-rules.pro add `-keep class androidx.core.app.ActivityCompat { *; }`
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest$permission')
        VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')

        if BuildVersion.SDK_INT >= VERSION_CODES.TIRAMISU:
            permission = Manifest.POST_NOTIFICATIONS
            granted = ContextCompat.checkSelfPermission(context, permission)

            if granted != 0:  # PackageManager.PERMISSION_GRANTED == 0
                ActivityCompat.requestPermissions(context, [permission], 101)
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
    output_path = os.path.join(app_root_path,'app', relative_path)
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
        print('Found res icon -->',context.getApplicationInfo().icon,'<--')
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
    :param style: Style of the notification ('big_text', 'big_picture', 'inbox', 'large_icon').
    :param img_path: Path to the image resource.
    :param channel_id: Notification channel ID.(Default is lowercase channel name arg in lowercase)
    """
    if not ON_ANDROID:
        print('This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.')
        return

    asks_permission_if_needed()
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
    builder.setDefaults(NotificationCompat.DEFAULT_ALL)
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)

    if img_path:
        print('android_notify- img_path arg deprecated use "large_icon_path or big_picture_path or custom_app_icon_path"instead ')

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
            builder.setLargeIcon(bitmap)
            big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
            builder.setStyle(big_picture_style)

    except Exception as e:
        print('android_notify- Error Failed Adding Style: ',e)
    # Display the notification
    notification_id = random.randint(0, 100)
    notification_manager.notify(notification_id, builder.build())
    return notification_id

