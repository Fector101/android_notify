
from jnius import autoclass,cast
import random
import os


def asks_permission_if_needed():
    """
    Ask for permission to send notifications if needed.
    """
    # Get the required Java classes
    from android.permissions import request_permissions, Permission,check_permission # type: ignore
    
    def check_permissions(permissions):
        for permission in permissions:
            if check_permission(permission) != True:
                return False
        return True

    permissions=[Permission.POST_NOTIFICATIONS]
    if check_permissions(permissions):
        request_permissions(permissions)

def get_image_uri(relative_path):
    """
    Get the absolute URI for an image in the assets folder.
    :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
    :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
    """
    from android.storage import app_storage_path # type: ignore
    # print("app_storage_path()",app_storage_path())

    output_path = os.path.join(app_storage_path(),'app', relative_path)
    # print(output_path,'output_path')  # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png

    Uri = autoclass('android.net.Uri')
    return Uri.parse(f"file://{output_path}")

def send_notification(title, message, style=None, img_path=None, channel_id="default_channel"):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: Style of the notification ('big_text', 'big_picture', 'inbox').
    :param image: Image URL or drawable for 'big_picture' style.
    :param channel_id: Notification channel ID.
    """
    # TODO check if running on android short circuit and return message if not
    
    # Get the required Java classes
    # Notification Base
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    String = autoclass('java.lang.String')
    
    
    NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
    NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
    
    # Notification Design
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
    # NotificationCompatBigTextStyle = autoclass('android.app.Notification$BigTextStyle')
    
    NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
    NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    PendingIntent = autoclass('android.app.PendingIntent')
    Intent = autoclass('android.content.Intent')
    
    # Get the app's context and notification manager
    context = PythonActivity.mActivity
    notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)

    importance= NotificationManagerCompat.IMPORTANCE_HIGH #autoclass('android.app.NotificationManager').IMPORTANCE_HIGH also works #NotificationManager.IMPORTANCE_DEFAULT
    
    # Notification Channel (Required for Android 8.0+)
    if BuildVersion.SDK_INT >= 26:
        print('entered....')
        channel = NotificationChannel(
            channel_id,
            "Default Channel",
            importance
        )
        notification_manager.createNotificationChannel(channel)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentText(message)
    builder.setSmallIcon(context.getApplicationInfo().icon)
    builder.setDefaults(NotificationCompat.DEFAULT_ALL) 
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)
    
    # Get Image
    img=img_path
    if img_path:
        try:
            img = get_image_uri(img_path)
        except Exception as e:
            print('Failed getting Image path',e)
    
     # Add Actions (Buttons)
    
    # add Action 1 Button
    try:
        # Create Action 1
        action_intent = Intent(context, PythonActivity)
        action_intent.setAction("ACTION_ONE")
        pending_action_intent = PendingIntent.getActivity(
            context, 
            0, 
            action_intent, 
            PendingIntent.FLAG_IMMUTABLE
        )
        
        # Convert text to CharSequence
        action_text = cast('java.lang.CharSequence', String("Action 1"))
        
        # Add action with proper types
        builder.addAction(
            int(context.getApplicationInfo().icon),  # Cast icon to int
            action_text,                             # CharSequence text
            pending_action_intent                    # PendingIntent
        )
        
        
        # Set content intent for notification tap
        builder.setContentIntent(pending_action_intent)
    except Exception as e:
        print('Failed adding Action 1',e)

    
    # Apply styles
    if style == "big_text":
        big_text_style = NotificationCompatBigTextStyle()
        big_text_style.bigText(message)
        builder.setStyle(big_text_style)
        
        
    elif style == "big_picture" and img_path:
        try:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img))
            # bitmap = BitmapFactory.decodeFile(img_path)
            builder.setLargeIcon(bitmap)
            big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
            # big_picture_style.bigPicture(bitmap).bigLargeIcon(None)
            # big_picture_style.bigLargeIcon(bitmap) # This just changes dropdown app icon
            
            builder.setStyle(big_picture_style)
        except Exception as e:
            print('Failed Adding Bitmap...', e)
    elif style == "inbox":
        inbox_style = NotificationCompatInboxStyle()
        for line in message.split("\n"):
            inbox_style.addLine(line)
        builder.setStyle(inbox_style)
    elif style == "large_icon" and img_path:
        try:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img))
            builder.setLargeIcon(bitmap)
        except Exception as e:
            print('Failed Large Icon...', e)
    
    # Show the notification
    notification_manager.notify(random.randint(0, 100), builder.build())
