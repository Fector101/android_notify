from jnius import autoclass, cast
import random
import os
from enum import Enum
from typing import Optional, List, Union
from dataclasses import dataclass

class NotificationImportance(Enum):
    MIN = 1
    LOW = 2
    DEFAULT = 3
    HIGH = 4

class NotificationPriority(Enum):
    MIN = -2
    LOW = -1
    DEFAULT = 0
    HIGH = 1
    MAX = 2

class NotificationStyle(Enum):
    DEFAULT = "default"
    BIG_TEXT = "big_text"
    BIG_PICTURE = "big_picture"
    INBOX = "inbox"
    MESSAGING = "messaging"

@dataclass
class NotificationAction:
    name: str
    intent: str
    icon: Optional[int] = None

class AndroidNotificationSystem:
    """Singleton class to handle Android-specific initialization and classes"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AndroidNotificationSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_android_classes()
            self._initialized = True

    def _initialize_android_classes(self):
        try:
            # Core Android classes
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.NotificationChannel = autoclass('android.app.NotificationChannel')
            self.String = autoclass('java.lang.String')
            self.Intent = autoclass('android.content.Intent')
            self.PendingIntent = autoclass('android.app.PendingIntent')
            self.Context = self.PythonActivity.mActivity
            self.BitmapFactory = autoclass('android.graphics.BitmapFactory')
            self.BuildVersion = autoclass('android.os.Build$VERSION')
            
            # Notification specific classes
            self.NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
            self.NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
            self.NotificationBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
            self.BigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
            self.BigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
            self.InboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
            self.MessagingStyle = autoclass('androidx.core.app.NotificationCompat$MessagingStyle')
            
            self.is_initialized = True
        except Exception as e:
            raise ImportError(
                "Failed to initialize Android classes. Ensure you have the following in buildozer.spec:\n"
                "android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0\n"
                "android.enable_androidx = True\n"
                "android.permissions = POST_NOTIFICATIONS"
            ) from e

class NotificationChannel:
    def __init__(
        self,
        channel_id: str,
        name: str,
        importance: NotificationImportance = NotificationImportance.DEFAULT,
        description: Optional[str] = None,
        enable_lights: bool = True,
        enable_vibration: bool = True
    ):
        self.android = AndroidNotificationSystem()
        self.channel_id = channel_id
        self.name = name
        
        if self.android.BuildVersion.SDK_INT >= 26:
            channel = self.android.NotificationChannel(
                channel_id,
                name,
                importance.value
            )
            if description:
                channel.setDescription(description)
            channel.enableLights(enable_lights)
            channel.enableVibration(enable_vibration)
            
            self.android.Context.getSystemService(
                self.android.Context.NOTIFICATION_SERVICE
            ).createNotificationChannel(channel)

class EnhancedNotificationManager:
    """Enhanced notification manager with more features and better organization"""
    
    _notification_ids = set()

    def __init__(
        self,
        channel_id: str,
        channel_name: str,
        importance: NotificationImportance = NotificationImportance.HIGH,
        group_key: Optional[str] = None
    ):
        self.android = AndroidNotificationSystem()
        self.channel = NotificationChannel(channel_id, channel_name, importance)
        self.builder = self.android.NotificationBuilder(
            self.android.Context,
            channel_id
        )
        self.notification_id = self._generate_unique_id()
        self.group_key = group_key
        
        if group_key:
            self.builder.setGroup(group_key)

    def _generate_unique_id(self) -> int:
        while (notification_id := random.randint(1, 10000)) in self._notification_ids:
            continue
        self._notification_ids.add(notification_id)
        return notification_id

    def set_content(
        self,
        title: str,
        message: str,
        style: NotificationStyle = NotificationStyle.DEFAULT,
        style_content: Optional[Union[str, str]] = None,
        image_path: Optional[str] = None
    ):
        """Set notification content with enhanced styling options"""
        self.builder.setContentTitle(title)
        self.builder.setContentText(message)
        
        if style == NotificationStyle.BIG_TEXT:
            big_text = style_content or message
            self.builder.setStyle(
                self.android.BigTextStyle().bigText(big_text)
            )
        elif style == NotificationStyle.BIG_PICTURE and image_path:
            bitmap = self._load_image(image_path)
            if bitmap:
                self.builder.setStyle(
                    self.android.BigPictureStyle()
                    .bigPicture(bitmap)
                    .setBigContentTitle(title)
                )
        elif style == NotificationStyle.INBOX and isinstance(style_content, list):
            inbox_style = self.android.InboxStyle()
            for line in style_content:
                inbox_style.addLine(line)
            self.builder.setStyle(inbox_style)
        elif style == NotificationStyle.MESSAGING:
            messaging_style = self.android.MessagingStyle("User")
            if isinstance(style_content, list):
                for msg in style_content:
                    messaging_style.addMessage(msg, 0, "Sender")
            self.builder.setStyle(messaging_style)

    def add_actions(self, actions: List[NotificationAction]):
        """Add multiple actions (buttons) to the notification"""
        for action in actions:
            intent = self.android.Intent(
                self.android.Context,
                self.android.PythonActivity
            )
            intent.setAction(action.intent)
            
            pending_intent = self.android.PendingIntent.getActivity(
                self.android.Context,
                random.randint(0, 10000),  # Unique request code
                intent,
                self.android.PendingIntent.FLAG_IMMUTABLE
            )
            
            icon = action.icon or self.android.Context.getApplicationInfo().icon
            action_text = cast('java.lang.CharSequence',
                             self.android.String(action.name))
            
            self.builder.addAction(icon, action_text, pending_intent)

    def set_icons(
        self,
        small_icon_path: Optional[str] = None,
        large_icon_path: Optional[str] = None
    ):
        """Set both small and large icons"""
        if small_icon_path:
            small_icon = self._load_image(small_icon_path)
            if small_icon:
                self.builder.setSmallIcon(small_icon)
        else:
            self.builder.setSmallIcon(
                self.android.Context.getApplicationInfo().icon
            )
            
        if large_icon_path:
            large_icon = self._load_image(large_icon_path)
            if large_icon:
                self.builder.setLargeIcon(large_icon)

    def _load_image(self, image_path: str):
        """Load image from app storage with error handling"""
        try:
            uri = self.__get_image_uri(image_path)
            return self.android.BitmapFactory.decodeStream(
                self.android.Context.getContentResolver().openInputStream(uri)
            )
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None

    def __get_image_uri(self, relative_path: str):
        """Get URI for image file"""
        from android.storage import app_storage_path # type: ignore
        
        output_path = os.path.join(
            app_storage_path(),
            'app',
            relative_path
        )
        if not os.path.exists(output_path):
            raise FileNotFoundError(
                f"Image not found at path: {output_path}"
            )
        
        Uri = autoclass('android.net.Uri')
        return Uri.parse(f"file://{output_path}")

    def set_priority(self, priority: NotificationPriority):
        """Set notification priority"""
        self.builder.setPriority(priority.value)

    def set_ongoing(self, ongoing: bool = True):
        """Set whether notification is ongoing"""
        self.builder.setOngoing(ongoing)

    def set_auto_cancel(self, auto_cancel: bool = True):
        """Set whether notification is automatically canceled on click"""
        self.builder.setAutoCancel(auto_cancel)

    def send(self) -> int:
        """Send the notification and return its ID"""
        notification_manager = self.android.Context.getSystemService(
            self.android.Context.NOTIFICATION_SERVICE
        )
        notification_manager.notify(
            self.notification_id,
            self.builder.build()
        )
        return self.notification_id

    def update(
        self,
        title: Optional[str] = None,
        message: Optional[str] = None,
        progress: Optional[tuple] = None
    ):
        """Update existing notification"""
        if title:
            self.builder.setContentTitle(title)
        if message:
            self.builder.setContentText(message)
        if progress:
            current, max_value = progress
            self.builder.setProgress(max_value, current, False)
            
        self.send()

    def cancel(self):
        """Cancel this notification"""
        notification_manager = self.android.Context.getSystemService(
            self.android.Context.NOTIFICATION_SERVICE
        )
        notification_manager.cancel(self.notification_id)
        self._notification_ids.remove(self.notification_id)

    @classmethod
    def cancel_all(cls):
        """Cancel all notifications"""
        android = AndroidNotificationSystem()
        notification_manager = android.Context.getSystemService(
            android.Context.NOTIFICATION_SERVICE
        )
        notification_manager.cancelAll()
        cls._notification_ids.clear()

# Example usage:
def example_usage():
    # Create a notification
    notification = EnhancedNotificationManager(
        channel_id="messages",
        channel_name="Messages",
        importance=NotificationImportance.HIGH
    )
    
    # Set basic content
    notification.set_content(
        title="New Message",
        message="Hello World!",
        style=NotificationStyle.BIG_TEXT
    )
    
    # Add actions
    actions = [
        NotificationAction("Reply", "REPLY_ACTION"),
        NotificationAction("Delete", "DELETE_ACTION")
    ]
    notification.add_actions(actions)
    
    # Set icons
    notification.set_icons(
        large_icon_path="assets/imgs/profile.png"
    )
    
    # Configure behavior
    notification.set_priority(NotificationPriority.HIGH)
    notification.set_auto_cancel(True)
    
    # Send the notification
    notification_id = notification.send()
    
    # Later, update the notification
    notification.update(
        message="Updated message!",
        progress=(50, 100)
    )
    
    # Cancel when done
    notification.cancel()