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


# For Dev
# Idea for typing autocompletion and reference
class Bundle:
    def putString(self,key,value):
        print(self,key,value)

    def putInt(self,key,value):
        print(self, key, value)

class String(str):
    pass


class Intent:
    def __init__(self,context,activity):
        self.obj={}
        pass

    def setAction(self,action):
        print(action)
        return self

    def setFlags(self,intent_flag):
        print(intent_flag)
        return self

    def getAction(self):
        return self

    def getStringExtra(self,key):
        return self

    def putExtra(self,key,value):
        self.obj[key] = value

    def putExtras(self,bundle:Bundle):
        self.obj['bundle'] = bundle

class PendingIntent:
    FLAG_IMMUTABLE=''
    FLAG_UPDATE_CURRENT=''

    def getActivity(self,context,value,action_intent,pending_intent_type):
        pass

class BitmapFactory:
    def decodeStream(self,stream):
        pass

class BuildVersion:
    SDK_INT=0

class NotificationManager:
    pass

class NotificationChannel:
    def __init__(self,channel_id,channel_name,importance):
        self.description = None
        self.channel_id = None
        self.channel = None
    def createNotificationChannel(self, channel):
        self.channel=channel

    def getNotificationChannel(self, channel_id):
        self.channel_id=channel_id
        pass

    def setDescription(self, description):
        self.description=description

    def getId(self):
        return  self.channel_id

class IconCompat:
    def createWithBitmap(self,bitmap):
        pass

class Color:
    def __init__(self):
        pass
    def parseColor(self,color:str):
        return self

class RemoteViews:
    def __init__(self, package_name, small_layout_id):
        pass
    def createWithBitmap(self,bitmap):
        pass
    def setTextViewText(self,id, text):
        pass
    def setTextColor(self,id, color:Color):
        pass

class NotificationManagerCompat:
    IMPORTANCE_HIGH=4
    IMPORTANCE_DEFAULT=3
    IMPORTANCE_LOW=''
    IMPORTANCE_MIN=''
    IMPORTANCE_NONE=''

class NotificationCompat:
    DEFAULT_ALL=3
    PRIORITY_HIGH=4
    PRIORITY_DEFAULT = ''
    PRIORITY_LOW=''
    PRIORITY_MIN=''

class MActions:
    def clear(self):
        """This Removes all buttons"""
        print('dummy clear')

class NotificationCompatBuilder:
    def __init__(self,context,channel_id):
        self.mActions = MActions()
        pass
    def setProgress(self,max_value,current_value,endless):
        pass
    def setStyle(self,style):
        pass
    def setContentTitle(self,title):
        pass
    def setContentText(self,text):
        pass
    def setSmallIcon(self,icon):
        pass
    def setLargeIcon(self,icon):
        pass
    def setAutoCancel(self,auto_cancel:bool):
        pass
    def setPriority(self,priority:Importance):
        pass
    def setDefaults(self,defaults:NotificationCompat.DEFAULT_ALL):
        pass
    def setOngoing(self,persistent:bool):
        pass
    def setOnlyAlertOnce(self,state):
        pass
    def build(self):
        pass
    def setContentIntent(self,pending_action_intent:PendingIntent):
        pass
    def addAction(self,icon_int,action_text,pending_action_intent):
        pass
    def setShowWhen(self,state):
        pass
    def setWhen(self,time_ms):
        pass
    def setCustomContentView(self,layout):
        pass
    def setCustomBigContentView(self,layout):
        pass
    def setSubText(self,text):
        pass
    def setColor(self, color:Color) -> None:
        pass
class NotificationCompatBigTextStyle:
    def bigText(self,body):
        return self

class NotificationCompatBigPictureStyle:
    def bigPicture(self,bitmap):
        return self

class NotificationCompatInboxStyle:
    def addLine(self,line):
        return self

class NotificationCompatDecoratedCustomViewStyle:
    pass

class Permission:
    POST_NOTIFICATIONS=''

def check_permission(permission:Permission.POST_NOTIFICATIONS):
    print(permission)

def request_permissions(_list: [], _callback):
    _callback()

class AndroidActivity:
    def bind(self,on_new_intent):
        pass
    def unbind(self,on_new_intent):
        pass

class PythonActivity:
    pass

class DummyIcon:
    icon = 101
    pass
class Context:
    def __init__(self):
        pass

    @staticmethod
    def getApplicationInfo():
        return DummyIcon

    @staticmethod
    def getResources():
        return None

    @staticmethod
    def getPackageName():
        return None # TODO get package name from buildozer.spec file

#Now writing Knowledge from errors
# notify.(int, Builder.build()) # must be int
