"""For autocomplete Storing Reference to Available Methods"""
from typing import Literal
Importance = Literal['urgent','high','medium','low','none']
"""
    :argument urgent - Makes a sound and appears as a heads-up notification.
    
    :argument high - Makes a sound.
    
    :argument urgent - Makes no sound.
    
    :argument urgent - Makes no sound and doesn't appear in the status bar.
    
    :argument urgent - Makes no sound and doesn't in the status bar or shade.
"""

# Idea for typing autocompletion and reference
# class Bundle:
#     pass
# class PythonActivity:
#     mActivity=''# Get the app's context
#     pass
# class String(str):
#     pass
# class Intent:
#     def __init__(self,context,activity):
#         pass
# class PendingIntent:
#     FLAG_IMMUTABLE=''
#     FLAG_UPDATE_CURRENT=''
#     def getActivity(self,context,value,action_intent,pending_intent_type):
#         pass
# class BitmapFactory:
#     def decodeStream(self,stream):
#         pass
# class BuildVersion:
#     SDK_INT=0
# class NotificationManager:
#     pass
# class NotificationChannel:
#     def __init__(self,channel_id,channel_name,importance):
#         pass
#     def createNotificationChannel(self, channel):
#         pass
#
#     def getNotificationChannel(self, channel_id):
#         pass
# class IconCompat:
#     def createWithBitmap(self,bitmap):
#         pass
#
# class NotificationManagerCompat:
#     IMPORTANCE_DEFAULT=3
#     IMPORTANCE_HIGH=4
#
#
# class NotificationCompat:
#     DEFAULT_ALL=3
#     PRIORITY_HIGH=4
#
#     def __init__(self,context):
#         pass
#     def Builder(self,context,channel_id):
#         pass
# class NotificationCompatBuilder:
#     def __init__(self,context,channel_id):
#         pass
#     def setContentTitle(self,title):
#         pass
#     def setContentText(self,text):
#         pass
#     def setSmallIcon(self,icon):
#         pass
#     def setLargeIcon(self,icon):
#         pass
#     def setAutoCancel(self,auto_cancel):
#         pass
#     def setPriority(self,priority):
#         pass
#     def setDefaults(self,defaults):
#         pass
#     def build(self):
#         pass
# class NotificationCompatBigTextStyle:
#     pass
# class NotificationCompatBigPictureStyle:
#     pass
# class NotificationCompatInboxStyle:
#     pass

#Now writing Knowledge from errors
# notify.(int, Builder.build()) # must be int
