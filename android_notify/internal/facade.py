"""
For autocomplete Storing and Safely Running on PC
Also For Reference of Available Methods
"""

from android_notify.internal.logger import logger

class Bundle:
    def putString(self, key, value):
        logger.debug(f"[MOCK] Bundle.putString called with key={key}, value={value}")

    def putInt(self, key, value):
        logger.debug(f"[MOCK] Bundle.putInt called with key={key}, value={value}")


class String(str):
    def __new__(cls, value):
        logger.debug(f"[MOCK] String created with value={value}")
        return str.__new__(cls, value)


class Intent:
    FLAG_ACTIVITY_NEW_TASK = 'FACADE_FLAG_ACTIVITY_NEW_TASK'
    CATEGORY_DEFAULT = 'FACADE_FLAG_CATEGORY_DEFAULT'

    def __init__(self, context='', activity=''):
        self.obj = {}
        logger.debug(f"[MOCK] Intent initialized with context={context}, activity={activity}")

    def setAction(self, action):
        logger.debug(f"[MOCK] Intent.setAction called with: {action}")
        return self

    def addFlags(self, *flags):
        logger.debug(f"[MOCK] Intent.addFlags called with: {flags}")
        return self

    def setData(self, uri):
        logger.debug(f"[MOCK] Intent.setData called with: {uri}")
        return self

    def setFlags(self, intent_flag):
        logger.debug(f"[MOCK] Intent.setFlags called with: {intent_flag}")
        return self

    def addCategory(self, intent_category):
        logger.debug(f"[MOCK] Intent.addCategory called with: {intent_category}")
        return self

    def getAction(self):
        logger.debug("[MOCK] Intent.getAction called")
        return self

    def getStringExtra(self, key):
        logger.debug(f"[MOCK] Intent.getStringExtra called with key={key}")
        return self

    def putExtra(self, key, value):
        self.obj[key] = value
        logger.debug(f"[MOCK] Intent.putExtra called with key={key}, value={value}")

    def putExtras(self, bundle: Bundle):
        self.obj['bundle'] = bundle
        logger.debug(f"[MOCK] Intent.putExtras called with bundle={bundle}")


class PendingIntent:
    FLAG_IMMUTABLE = ''
    FLAG_UPDATE_CURRENT = ''

    @classmethod
    def getActivity(cls, context, value, action_intent, pending_intent_type):
        logger.debug(
            f"[MOCK] PendingIntent.getActivity called with context={context}, value={value}, action_intent={action_intent}, type={pending_intent_type}"
        )


class BitmapFactory:
    @classmethod
    def decodeStream(cls, stream):
        logger.debug(f"[MOCK] BitmapFactory.decodeStream called with stream={stream}")


class BuildVersion:
    SDK_INT = 0


class Manifest:
    POST_NOTIFICATIONS = 'FACADE_IMPORT'


class Settings:
    ACTION_APP_NOTIFICATION_SETTINGS = 'FACADE_IMPORT_ACTION_APP_NOTIFICATION_SETTINGS'
    EXTRA_APP_PACKAGE = 'FACADE_IMPORT_EXTRA_APP_PACKAGE'
    ACTION_APPLICATION_DETAILS_SETTINGS = 'FACADE_IMPORT_ACTION_APPLICATION_DETAILS_SETTINGS'


class Uri:
    def __init__(self, package_name):
        logger.debug("FACADE_URI")


class NotificationManager:
    pass


class NotificationChannel:
    def __init__(self, channel_id, channel_name, importance):
        self.description = None
        self.channel_id = channel_id
        self.channel = None
        logger.debug(
            f"[MOCK] NotificationChannel initialized with id={channel_id}, name={channel_name}, importance={importance}"
        )

    def createNotificationChannel(self, channel):
        self.channel = channel
        logger.debug(f"[MOCK] NotificationChannel.createNotificationChannel called with channel={channel}")

    def getNotificationChannel(self, channel_id):
        self.channel_id = channel_id
        logger.debug(f"[MOCK] NotificationChannel.getNotificationChannel called with id={channel_id}")

    def setDescription(self, description):
        self.description = description
        logger.debug(f"[MOCK] NotificationChannel.setDescription called with description={description}")

    def getId(self):
        logger.debug(f"[MOCK] NotificationChannel.getId called, returning {self.channel_id}")
        return self.channel_id

    def setSound(self, sound_uri, _):
        logger.debug(f"[MOCK] NotificationChannel.setSound called, sound_uri={sound_uri}")

    def enableVibration(self,state):
        logger.debug(f"[MOCK] NotificationChannel.enableVibration called, state={state}")

    def setVibrationPattern(self,list_of_numbers):
        logger.debug(f"[MOCK] NotificationChannel.setVibrationPattern called, list_of_numbers={list_of_numbers}")

class IconCompat:
    @classmethod
    def createWithBitmap(cls, bitmap):
        logger.debug(f"[MOCK] IconCompat.createWithBitmap called with bitmap={bitmap}")


class Color:
    def __init__(self):
        logger.debug("[MOCK] Color initialized")

    @classmethod
    def parseColor(cls, color: str):
        logger.debug(f"[MOCK] Color.parseColor called with color={color}")
        return cls


class RemoteViews:
    def __init__(self, package_name, small_layout_id):
        logger.debug(f"[MOCK] RemoteViews initialized with package_name={package_name}, layout_id={small_layout_id}")

    def createWithBitmap(self, bitmap):
        logger.debug(f"[MOCK] RemoteViews.createWithBitmap called with bitmap={bitmap}")

    def setTextViewText(self, id, text):
        logger.debug(f"[MOCK] RemoteViews.setTextViewText called with id={id}, text={text}")

    def setTextColor(self, id, color: Color):
        logger.debug(f"[MOCK] RemoteViews.setTextColor called with id={id}, color={color}")


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
        logger.debug('[MOCK] MActions.clear called')


class NotificationCompatBuilder:
    def __init__(self, context, channel_id):
        self.mActions = MActions()
        logger.debug(f"[MOCK] NotificationCompatBuilder initialized with context={context}, channel_id={channel_id}")

    def setProgress(self, max_value, current_value, endless):
        logger.debug(f"[MOCK] setProgress called with max={max_value}, current={current_value}, endless={endless}")

    def setStyle(self, style):
        logger.debug(f"[MOCK] setStyle called with style={style}")

    def setContentTitle(self, title):
        logger.debug(f"[MOCK] setContentTitle called with title={title}")

    def setContentText(self, text):
        logger.debug(f"[MOCK] setContentText called with text={text}")

    def setSmallIcon(self, icon):
        logger.debug(f"[MOCK] setSmallIcon called with icon={icon}")

    def setLargeIcon(self, icon):
        logger.debug(f"[MOCK] setLargeIcon called with icon={icon}")

    def setAutoCancel(self, auto_cancel: bool):
        logger.debug(f"[MOCK] setAutoCancel called with auto_cancel={auto_cancel}")

    def setPriority(self, priority):
        logger.debug(f"[MOCK] setPriority called with priority={priority}")

    def setDefaults(self, defaults):
        logger.debug(f"[MOCK] setDefaults called with defaults={defaults}")

    def setOngoing(self, persistent: bool):
        logger.debug(f"[MOCK] setOngoing called with persistent={persistent}")

    def setOnlyAlertOnce(self, state):
        logger.debug(f"[MOCK] setOnlyAlertOnce called with state={state}")

    def build(self):
        logger.debug("[MOCK] build called")

    def setContentIntent(self, pending_action_intent: PendingIntent):
        logger.debug(f"[MOCK] setContentIntent called with {pending_action_intent}")

    def addAction(self, icon_int, action_text, pending_action_intent):
        logger.debug(
            f"[MOCK] addAction called with icon={icon_int}, text={action_text}, intent={pending_action_intent}"
        )

    def setShowWhen(self, state):
        logger.debug(f"[MOCK] setShowWhen called with state={state}")

    def setWhen(self, time_ms):
        logger.debug(f"[MOCK] setWhen called with time_ms={time_ms}")

    def setCustomContentView(self, layout):
        logger.debug(f"[MOCK] setCustomContentView called with layout={layout}")

    def setCustomBigContentView(self, layout):
        logger.debug(f"[MOCK] setCustomBigContentView called with layout={layout}")

    def setSubText(self, text):
        logger.debug(f"[MOCK] setSubText called with text={text}")

    def setColor(self, color: Color) -> None:
        logger.debug(f"[MOCK] setColor called with color={color}")

    def setVibrate(self, state) -> None:
        logger.debug(f"[MOCK] setVibrate called with state={state}")


class NotificationCompatBigTextStyle:
    def bigText(self, body):
        logger.debug(f"[MOCK] NotificationCompatBigTextStyle.bigText called with body={body}")
        return self

    def setBigContentTitle(self, title):
        logger.debug(f"[MOCK] NotificationCompatBigTextStyle.setBigContentTitle called with title={title}")
        return self

    def setSummaryText(self, summary):
        logger.debug(f"[MOCK] NotificationCompatBigTextStyle.setSummaryText called with summary={summary}")


class NotificationCompatBigPictureStyle:
    def bigPicture(self, bitmap):
        logger.debug(f"[MOCK] NotificationCompatBigPictureStyle.bigPicture called with bitmap={bitmap}")
        return self


class NotificationCompatInboxStyle:
    def addLine(self, line):
        logger.debug(f"[MOCK] NotificationCompatInboxStyle.addLine called with line={line}")
        return self


class NotificationCompatDecoratedCustomViewStyle:
    def __init__(self):
        logger.debug("[MOCK] NotificationCompatDecoratedCustomViewStyle initialized")


class Permission:
    POST_NOTIFICATIONS = ''


def check_permission(permission):
    logger.debug(f"[MOCK] check_permission called with {permission}")
    logger.debug(permission)


def request_permissions(_list, _callback):
    logger.debug(f"[MOCK] request_permissions called with {_list}")
    _callback()


class AndroidActivity:
    def bind(self, on_new_intent):
        logger.debug(f"[MOCK] AndroidActivity.bind called with {on_new_intent}")

    def unbind(self, on_new_intent):
        logger.debug(f"[MOCK] AndroidActivity.unbind called with {on_new_intent}")


class MActivity:
    def getSystemService(self):
        logger.debug("[MOCK] mActivity.getSystemService called")
        return self


class PythonActivity:
    def __init__(self):
        logger.debug("[MOCK] PythonActivity initialized")

    @staticmethod
    def mActivity():
        logger.debug("[MOCK] mActivity used")
        return MActivity()


class DummyIcon:
    icon = 101

    def __init__(self):
        logger.debug("[MOCK] DummyIcon initialized")


class Context:
    def __init__(self):
        logger.debug("[MOCK] Context initialized")
        pass

    @staticmethod
    def getApplicationInfo():
        logger.debug("[MOCK] Context.getApplicationInfo called")
        return DummyIcon

    @staticmethod
    def getResources():
        logger.debug("[MOCK] Context.getResources called")
        return None

    @staticmethod
    def getPackageName():
        logger.debug("[MOCK] Context.getPackageName called")
        return None  # TODO get package name from buildozer.spec file


class PackageManager:
    @property
    def PERMISSION_GRANTED(self):
        logger.debug("[MOCK] PackageManager.PERMISSION_GRANTED called")
        return 1

# Now writing Knowledge from errors
# notify.(int, Builder.build()) # must be int
