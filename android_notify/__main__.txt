# from typing import List
# from dataclasses import dataclass
# import random
# from jnius import autoclass, cast, java_method

# # Android classes
# PythonActivity = autoclass('org.kivy.android.PythonActivity')
# Context = autoclass('android.content.Context')
# NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
# NotificationManager = autoclass('android.app.NotificationManager')
# Intent = autoclass('android.content.Intent')
# PendingIntent = autoclass('android.app.PendingIntent')
# String = autoclass('java.lang.String')

# @dataclass
# class NotificationAction:
#     """Class to define notification action buttons"""
#     name: str
#     intent: str
#     icon: int = None  # Android resource ID for the icon
    
# class NotificationBuilder:
#     def __init__(self, context=None):
#         self.context = context or PythonActivity.mActivity
#         self.CHANNEL_ID = "app_channel"
#         self.notification_manager = cast(
#             'android.app.NotificationManager',
#             self.context.getSystemService(Context.NOTIFICATION_SERVICE)
#         )
        
#         # Create the notification builder
#         self.builder = NotificationCompat.Builder(self.context, self.CHANNEL_ID)
#         self.builder.setAutoCancel(True)
#         self.builder.setPriority(NotificationCompat.PRIORITY_DEFAULT)
        
#         # Create notification channel for Android 8.0+
#         self.create_notification_channel()
        
#     def create_notification_channel(self):
#         """Create the notification channel required for Android 8.0+"""
#         NotificationChannel = autoclass('android.app.NotificationChannel')
#         channel = NotificationChannel(
#             self.CHANNEL_ID,
#             "App Channel",
#             NotificationManager.IMPORTANCE_DEFAULT
#         )
#         self.notification_manager.createNotificationChannel(channel)
    
#     def set_content(self, title: str, message: str, icon_id: int = None):
#         """Set the basic content of the notification"""
#         if icon_id is None:
#             icon_id = self.context.getApplicationInfo().icon
            
#         self.builder.setContentTitle(title)
#         self.builder.setContentText(message)
#         self.builder.setSmallIcon(icon_id)
#         return self
        
#     def add_actions(self, actions: List[NotificationAction]):
#         """Add multiple actions (buttons) to the notification"""
#         for action in actions:
#             # Create intent for this action
#             intent = Intent(self.context, PythonActivity.mActivity.getClass())
#             intent.setAction(action.intent)
#             intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
            
#             # Create unique pending intent for this action
#             pending_intent = PendingIntent.getActivity(
#                 self.context,
#                 random.randint(0, 10000),  # Unique request code
#                 intent,
#                 PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
#             )
            
#             # Set icon (use app icon if none provided)
#             icon = action.icon or self.context.getApplicationInfo().icon
            
#             # Convert action name to Java String
#             action_text = cast('java.lang.CharSequence', String(action.intent))
            
#             # Add the action to the notification
#             self.builder.addAction(icon, action_text, pending_intent)
        
#         return self
    
#     def show(self, notification_id: int = None):
#         """Show the notification"""
#         if notification_id is None:
#             notification_id = random.randint(1, 10000)
#         self.notification_manager.notify(notification_id, self.builder.build())
#         return notification_id

# class NotificationHandler:
#     """Class to handle notification responses in your Kivy app"""
    
#     @staticmethod
#     def handle_intent(intent):
#         """Handle the intent when a notification action is clicked"""
#         action = intent.getAction()
#         if action is None:
#             return
            
#         # Handle different actions
#         if action == "PLAY_ACTION":
#             print("Play button clicked")
#             # Add your play handling code here
            
#         elif action == "PAUSE_ACTION":
#             print("Pause button clicked")
#             # Add your pause handling code here
            
#         elif action == "STOP_ACTION":
#             print("Stop button clicked")
#             # Add your stop handling code here

# # Example usage in your Kivy app
# class KivyApp:
#     def create_notification_with_actions(self):
#         # Define actions
#         actions = [
#             NotificationAction(
#                 name="Play",
#                 intent="PLAY_ACTION",
#                 icon=android.R.drawable.ic_media_play
#             ),
#             NotificationAction(
#                 name="Pause",
#                 intent="PAUSE_ACTION",
#                 icon=android.R.drawable.ic_media_pause
#             ),
#             NotificationAction(
#                 name="Stop",
#                 intent="STOP_ACTION",
#                 icon=android.R.drawable.ic_media_stop
#             )
#         ]
        
#         # Create and show notification with actions
#         notification = NotificationBuilder()
#         notification.set_content(
#             title="Media Player",
#             message="Now Playing: Song Name"
#         )
#         notification.add_actions(actions)
#         notification.show()
        
#     def on_new_intent(self, intent):
#         """Handle notification action clicks"""
#         NotificationHandler.handle_intent(intent)