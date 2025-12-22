"""For autocomplete Storing Reference to Available Methods"""
from typing import Literal

Importance = Literal['urgent', 'high', 'medium', 'low', 'none']
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
    def putString(self, key, value):
        print(f"[MOCK] Bundle.putString called with key={key}, value={value}")

    def putInt(self, key, value):
        print(f"[MOCK] Bundle.putInt called with key={key}, value={value}")


class String(str):
    def __new__(cls, value):
        print(f"[MOCK] String created with value={value}")
        return str.__new__(cls, value)


class Intent:
    FLAG_ACTIVITY_NEW_TASK = 'FACADE_FLAG_ACTIVITY_NEW_TASK'
    CATEGORY_DEFAULT = 'FACADE_FLAG_CATEGORY_DEFAULT'

    def __init__(self, context='', activity=''):
        self.obj = {}
        print(f"[MOCK] Intent initialized with context={context}, activity={activity}")

    def setAction(self, action):
        print(f"[MOCK] Intent.setAction called with: {action}")
        return self

    def addFlags(self, *flags):
        print(f"[MOCK] Intent.addFlags called with: {flags}")
        return self

    def setData(self, uri):
        print(f"[MOCK] Intent.setData called with: {uri}")
        return self

    def setFlags(self, intent_flag):
        print(f"[MOCK] Intent.setFlags called with: {intent_flag}")
        return self

    def addCategory(self, intent_category):
        print(f"[MOCK] Intent.addCategory called with: {intent_category}")
        return self

    def getAction(self):
        print("[MOCK] Intent.getAction called")
        return self

    def getStringExtra(self, key):
        print(f"[MOCK] Intent.getStringExtra called with key={key}")
        return self

    def putExtra(self, key, value):
        self.obj[key] = value
        print(f"[MOCK] Intent.putExtra called with key={key}, value={value}")

    def putExtras(self, bundle: Bundle):
        self.obj['bundle'] = bundle
        print(f"[MOCK] Intent.putExtras called with bundle={bundle}")


class PendingIntent:
    FLAG_IMMUTABLE = ''
    FLAG_UPDATE_CURRENT = ''

    def getActivity(self, context, value, action_intent, pending_intent_type):
        print(
            f"[MOCK] PendingIntent.getActivity called with context={context}, value={value}, action_intent={action_intent}, type={pending_intent_type}")


class BitmapFactory:
    def decodeStream(self, stream):
        print(f"[MOCK] BitmapFactory.decodeStream called with stream={stream}")


class BuildVersion:
    SDK_INT = 0

class Manifest:
    POST_NOTIFICATIONS = 'FACADE_IMPORT'

class Settings:
    ACTION_APP_NOTIFICATION_SETTINGS = 'FACADE_IMPORT_ACTION_APP_NOTIFICATION_SETTINGS'
    EXTRA_APP_PACKAGE = 'FACADE_IMPORT_EXTRA_APP_PACKAGE'
    ACTION_APPLICATION_DETAILS_SETTINGS = 'FACADE_IMPORT_ACTION_APPLICATION_DETAILS_SETTINGS'

class Uri:
    def __init__(self,package_name):
        print("FACADE_URI")

class NotificationManager:
    pass


class NotificationChannel:
    def __init__(self, channel_id, channel_name, importance):
        self.description = None
        self.channel_id = channel_id
        self.channel = None
        print(
            f"[MOCK] NotificationChannel initialized with id={channel_id}, name={channel_name}, importance={importance}")

    def createNotificationChannel(self, channel):
        self.channel = channel
        print(f"[MOCK] NotificationChannel.createNotificationChannel called with channel={channel}")

    def getNotificationChannel(self, channel_id):
        self.channel_id = channel_id
        print(f"[MOCK] NotificationChannel.getNotificationChannel called with id={channel_id}")

    def setDescription(self, description):
        self.description = description
        print(f"[MOCK] NotificationChannel.setDescription called with description={description}")

    def getId(self):
        print(f"[MOCK] NotificationChannel.getId called, returning {self.channel_id}")
        return self.channel_id


class IconCompat:
    def createWithBitmap(self, bitmap):
        print(f"[MOCK] IconCompat.createWithBitmap called with bitmap={bitmap}")


class Color:
    def __init__(self):
        print("[MOCK] Color initialized")

    def parseColor(self, color: str):
        print(f"[MOCK] Color.parseColor called with color={color}")
        return self


class RemoteViews:
    def __init__(self, package_name, small_layout_id):
        print(f"[MOCK] RemoteViews initialized with package_name={package_name}, layout_id={small_layout_id}")

    def createWithBitmap(self, bitmap):
        print(f"[MOCK] RemoteViews.createWithBitmap called with bitmap={bitmap}")

    def setTextViewText(self, id, text):
        print(f"[MOCK] RemoteViews.setTextViewText called with id={id}, text={text}")

    def setTextColor(self, id, color: Color):
        print(f"[MOCK] RemoteViews.setTextColor called with id={id}, color={color}")


class NotificationManagerCompat:
    IMPORTANCE_HIGH = 4
    IMPORTANCE_DEFAULT = 3
    IMPORTANCE_LOW = ''
    IMPORTANCE_MIN = ''
    IMPORTANCE_NONE = ''


class NotificationCompat:
    DEFAULT_ALL = 3
    PRIORITY_HIGH = 4
    PRIORITY_DEFAULT = ''
    PRIORITY_LOW = ''
    PRIORITY_MIN = ''


class MActions:
    def clear(self):
        """This Removes all buttons"""
        print('[MOCK] MActions.clear called')


class NotificationCompatBuilder:
    def __init__(self, context, channel_id):
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

    def setSmallIcon(self, icon):
        print(f"[MOCK] setSmallIcon called with icon={icon}")

    def setLargeIcon(self, icon):
        print(f"[MOCK] setLargeIcon called with icon={icon}")

    def setAutoCancel(self, auto_cancel: bool):
        print(f"[MOCK] setAutoCancel called with auto_cancel={auto_cancel}")

    def setPriority(self, priority: Importance):
        print(f"[MOCK] setPriority called with priority={priority}")

    def setDefaults(self, defaults):
        print(f"[MOCK] setDefaults called with defaults={defaults}")

    def setOngoing(self, persistent: bool):
        print(f"[MOCK] setOngoing called with persistent={persistent}")

    def setOnlyAlertOnce(self, state):
        print(f"[MOCK] setOnlyAlertOnce called with state={state}")

    def build(self):
        print("[MOCK] build called")

    def setContentIntent(self, pending_action_intent: PendingIntent):
        print(f"[MOCK] setContentIntent called with {pending_action_intent}")

    def addAction(self, icon_int, action_text, pending_action_intent):
        print(f"[MOCK] addAction called with icon={icon_int}, text={action_text}, intent={pending_action_intent}")

    def setShowWhen(self, state):
        print(f"[MOCK] setShowWhen called with state={state}")

    def setWhen(self, time_ms):
        print(f"[MOCK] setWhen called with time_ms={time_ms}")

    def setCustomContentView(self, layout):
        print(f"[MOCK] setCustomContentView called with layout={layout}")

    def setCustomBigContentView(self, layout):
        print(f"[MOCK] setCustomBigContentView called with layout={layout}")

    def setSubText(self, text):
        print(f"[MOCK] setSubText called with text={text}")

    def setColor(self, color: Color) -> None:
        print(f"[MOCK] setColor called with color={color}")


class NotificationCompatBigTextStyle:
    def bigText(self, body):
        print(f"[MOCK] NotificationCompatBigTextStyle.bigText called with body={body}")
        return self


class NotificationCompatBigPictureStyle:
    def bigPicture(self, bitmap):
        print(f"[MOCK] NotificationCompatBigPictureStyle.bigPicture called with bitmap={bitmap}")
        return self


class NotificationCompatInboxStyle:
    def addLine(self, line):
        print(f"[MOCK] NotificationCompatInboxStyle.addLine called with line={line}")
        return self


class NotificationCompatDecoratedCustomViewStyle:
    def __init__(self):
        print("[MOCK] NotificationCompatDecoratedCustomViewStyle initialized")


class Permission:
    POST_NOTIFICATIONS = ''


def check_permission(permission: Permission.POST_NOTIFICATIONS):
    print(f"[MOCK] check_permission called with {permission}")
    print(permission)


def request_permissions(_list: [], _callback):
    print(f"[MOCK] request_permissions called with {_list}")
    _callback()


class AndroidActivity:
    def bind(self, on_new_intent):
        print(f"[MOCK] AndroidActivity.bind called with {on_new_intent}")

    def unbind(self, on_new_intent):
        print(f"[MOCK] AndroidActivity.unbind called with {on_new_intent}")


class PythonActivity:
    def __init__(self):
        print("[MOCK] PythonActivity initialized")


class DummyIcon:
    icon = 101

    def __init__(self):
        print("[MOCK] DummyIcon initialized")


class Context:
    def __init__(self):
        print("[MOCK] Context initialized")
        pass

    @staticmethod
    def getApplicationInfo():
        print("[MOCK] Context.getApplicationInfo called")
        return DummyIcon

    @staticmethod
    def getResources():
        print("[MOCK] Context.getResources called")
        return None

    @staticmethod
    def getPackageName():
        print("[MOCK] Context.getPackageName called")
        return None  # TODO get package name from buildozer.spec file

# Now writing Knowledge from errors
# notify.(int, Builder.build()) # must be int
