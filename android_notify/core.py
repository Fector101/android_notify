
from jnius import autoclass,cast
import random
import os

ON_ANDROID = False
try:
    # Get the required Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    context = PythonActivity.mActivity # Get the app's context 
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')    
    ON_ANDROID=True
except Exception as e:
    print('This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.')

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
        print("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS
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


def send_notification(title:str, message:str, style=None, img_path=None, channel_id:str="default_channel"):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: Style of the notification ('big_text', 'big_picture', 'inbox', 'large_icon').
    :param img_path: Path to the image resource.
    :param channel_id: Notification channel ID.
    """
    if not ON_ANDROID:
        print('This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.')
        return
    asks_permission_if_needed()
    
    # Get notification manager
    notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)

    # importance= autoclass('android.app.NotificationManager').IMPORTANCE_HIGH # also works #NotificationManager.IMPORTANCE_DEFAULT
    importance= NotificationManagerCompat.IMPORTANCE_HIGH #autoclass('android.app.NotificationManager').IMPORTANCE_HIGH also works #NotificationManager.IMPORTANCE_DEFAULT
    
    # Notification Channel (Required for Android 8.0+)
    if BuildVersion.SDK_INT >= 26:
        channel = NotificationChannel(channel_id, "Default Channel",importance)
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


class NotificationManager:
    notification_ids=[]
    def __init__(self, channel_id='',channel_name="Default Channel",importance_level=NotificationManagerCompat.IMPORTANCE_HIGH):
        if not ON_ANDROID:
            raise RuntimeError("This package only runs on Android!")
        self.channel_name = channel_name
        self.channel_id=channel_name.replace(' ','_').lower().lower() if not channel_id else channel_id
        self.notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)
        self.builder = NotificationCompatBuilder(context, self.channel_id)
        self.notification_id = self.__getUniqueID()
        
        # Setup Channel (For Android 8.0+)
        if BuildVersion.SDK_INT >= 26:
            channel = NotificationChannel(self.channel_id, channel_name, importance_level)
            self.notification_manager.createNotificationChannel(channel)
        
    def set_title(self, title: str):
        """Set the title of the notification."""
        self.builder.setContentTitle(title)
    def set_message(self, message: str):
        """Set the message of the notification."""
        self.builder.setContentText(message)
    def set_style(self, style: str, img_path=None):
        """Set the style of the notification."""
        try:
            if style == "big_text":
                big_text_style = NotificationCompatBigTextStyle()
                big_text_style.bigText(self.builder.mContentText)
                self.builder.setStyle(big_text_style)
            elif style == "big_picture" and img_path:
                img = get_image_uri(img_path)
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(img)
                self.builder.setStyle(big_picture_style)
            elif style == "inbox":
                inbox_style = NotificationCompatInboxStyle()
                for line in self.builder.mContentText.split("\n"):
                    inbox_style.addLine(line)
                self.builder.setStyle(inbox_style)
        except Exception as e:
            print('Failed Adding Style:', e)
    
    def add_button(self, action_name: str, action_intent: str):
        """Add a button to the notification."""
        try:
            intent = Intent(context, PythonActivity)
            intent.setAction(action_intent)
            pending_intent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_IMMUTABLE
            )
            action_text = cast('java.lang.CharSequence', String(action_name))
            self.builder.addAction(
                int(context.getApplicationInfo().icon),
                action_text,
                pending_intent
            )
        except Exception as e:
            print('Failed adding button:', e)
    def set_icon(self, img_path: str):
        """Set the icon of the notification."""
        try:
            img = get_image_uri(img_path)
            self.builder.setLargeIcon(BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img)))
        except Exception as e:
            print('Failed Adding Bitmap:', e)
    
    def send(self):
        """Send the notification."""
        self.builder.setSmallIcon(context.getApplicationInfo().icon)
        self.builder.setDefaults(NotificationCompat.DEFAULT_ALL)
        self.builder.setPriority(NotificationCompat.PRIORITY_HIGH)
        self.notification_manager.notify(self.notification_id, self.builder.build())
        return self.notification_id
    
    def update(self, title=None, message=None):
        """Update the notification."""
        if title:
            self.builder.setContentTitle(title)
        if message:
            self.builder.setContentText(message)
        self.notification_manager.notify(self.notification_id, self.builder.build())
    def __get_image(self, img_path):
        """Get the image from the app Relative path."""
        from android.storage import app_storage_path
        output_path = os.path.join(app_storage_path(), 'app', img_path)
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Image not found at path: {output_path}")
        Uri = autoclass('android.net.Uri')
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(Uri.parse(f"file://{output_path}")))
        # return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(get_image_uri(img_path)))
    def cancel(self):
        """Cancel the notification."""
        self.notification_manager.cancel(self.notification_id)
        self.__del__()
    def cancel_all(self):
        """Cancel all notifications."""
        self.notification_manager.cancelAll()
    def __del__(self):
        """Delete the notification id."""
        self.notification_ids.remove(self.notification_id)        
    def __getUniqueID(self):
        notification_id = random.randint(1, 100)
        while notification_id in self.notification_ids:
            notification_id = random.randint(1, 100)
        self.notification_ids.append(notification_id)
        return notification_id

# notification_manager=NotificationManager()
# notification_manager.s