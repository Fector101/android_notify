"""
For autocomplete Storing and Safely Running on PC
Also For Reference of Available Methods
"""

from enum import IntFlag, auto
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




class Intent(IntFlag):
    NONE = 0
    FLAG_ACTIVITY_CLEAR_TOP = auto()
    FLAG_ACTIVITY_NEW_TASK = auto()
    FLAG_ACTIVITY_SINGLE_TOP = auto()
    EXTRA_ALLOW_MULTIPLE = auto()
    ACTION_GET_CONTENT = auto()
    CATEGORY_OPENABLE = auto()
    FLAG_GRANT_READ_URI_PERMISSION = auto()
    ACTION_SEND = auto()
    ACTION_SEND_MULTIPLE = auto()
    EXTRA_STREAM = auto()
    ACTION_MEDIA_BUTTON = auto()
    EXTRA_KEY_EVENT = auto()

    def __init__(self, context='', activity=''):
        self.IS = "FACADE"
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

    def setType(self, char_sequence:String):
        self.obj['char_sequence'] = char_sequence
        logger.debug(f"[MOCK] Intent.setType called with char_sequence={char_sequence}")

    @classmethod
    def createChooser(cls, intent, char_sequence:String):
        logger.debug(f"[MOCK] Intent.createChooser called with intent={intent}, char_sequence={char_sequence}")

    @classmethod
    def setClipData(cls, clip):
        logger.debug(f"[MOCK] Intent.setClipData called with clip={clip}")

    @classmethod
    def putParcelableArrayListExtra(cls, flag, uris:list):
        logger.debug(f"[MOCK] Intent.putParcelableArrayListExtra called with flag={flag} and uris={uris}")

    def setPackage(self, param):
        pass

class PendingIntent:
    FLAG_UPDATE_CURRENT = 0x08000000
    FLAG_IMMUTABLE = 0x04000000

    @classmethod
    def getActivity(cls, context, value, action_intent, pending_intent_type):
        logger.debug(
            f"[MOCK] PendingIntent.getActivity called with context={context}, value={value}, action_intent={action_intent}, type={pending_intent_type}"
        )

    @classmethod
    def getBroadcast(cls, context, value, action_intent, pending_intent_type):
        logger.debug(
            f"[MOCK] PendingIntent.getBroadcast called with context={context}, value={value}, action_intent={action_intent}, type={pending_intent_type}"
        )


class BitmapFactory:
    @classmethod
    def decodeStream(cls, stream):
        logger.debug(f"[MOCK] BitmapFactory.decodeStream called with stream={stream}")

    @classmethod
    def decodeByteArray(cls, art_bytes, art_bytes_start, art_bytes_len):
        logger.debug(f"[MOCK] BitmapFactory.decodeStream called with art_bytes={art_bytes},art_bytes_start={art_bytes_start}, art_bytes_len={art_bytes_len}")



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

    @classmethod
    def parse(cls, uri_string):
        logger.debug(f"[MOCK] Uri.parse called with uri_string={uri_string}")
        return cls

    @classmethod
    def fromFile(cls, java_file):
        logger.debug(f"[MOCK] Uri.fromFile called with file={java_file}")
        return cls

    @classmethod
    def withAppendedPath(cls, base_uri, path_segment:String):
        logger.debug(f"[MOCK] Uri.withAppendedPath called with base_uri={base_uri} and path_segment={path_segment}")
        return cls


class AudioAttributes:
    CONTENT_TYPE_SONIFICATION = 4
    USAGE_NOTIFICATION = 5
    USAGE_ALARM = 4


class AudioAttributesBuilder:
    def __init__(self):
        logger.debug("[MOCK] AudioAttributesBuilder initialized")

    def setContentType(self, content_type):
        logger.debug(f"[MOCK] AudioAttributesBuilder.setContentType called with content_type={content_type}")
        return self

    def setUsage(self, usage):
        logger.debug(f"[MOCK] AudioAttributesBuilder.setUsage called with usage={usage}")
        return self

    def build(self):
        logger.debug("[MOCK] AudioAttributesBuilder.build called")
        return AudioAttributes()


class File:
    def __init__(self, path):
        self.path = path
        logger.debug(f"[MOCK] File initialized with path={path}")

    def getAbsolutePath(self):
        logger.debug(f"[MOCK] File.getAbsolutePath called, returning {self.path}")
        return self.path

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

    def enableVibration(self, state):
        logger.debug(f"[MOCK] NotificationChannel.enableVibration called, state={state}")

    def setVibrationPattern(self, list_of_numbers):
        logger.debug(f"[MOCK] NotificationChannel.setVibrationPattern called, list_of_numbers={list_of_numbers}")


class IconClass:
    @classmethod
    def createWithBitmap(cls, bitmap):
        logger.debug(f"[MOCK] IconClass.createWithBitmap called with bitmap={bitmap}")


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


class AndroidNotification:
    DEFAULT_ALL = 3
    PRIORITY_HIGH = 4
    PRIORITY_DEFAULT = ''
    PRIORITY_LOW = ''
    PRIORITY_MIN = ''


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

    @classmethod
    def setProgress(cls, max_value, current_value, endless):
        logger.debug(f"[MOCK] setProgress called with max={max_value}, current={current_value}, endless={endless}")

    @classmethod
    def setStyle(cls, style):
        logger.debug(f"[MOCK] setStyle called with style={style}")

    @classmethod
    def setContentTitle(cls, title):
        logger.debug(f"[MOCK] setContentTitle called with title={title}")

    @classmethod
    def setContentText(cls, text):
        logger.debug(f"[MOCK] setContentText called with text={text}")

    @classmethod
    def setSmallIcon(cls, icon):
        logger.debug(f"[MOCK] setSmallIcon called with icon={icon}")

    @classmethod
    def setLargeIcon(cls, icon):
        logger.debug(f"[MOCK] setLargeIcon called with icon={icon}")

    @classmethod
    def setAutoCancel(cls, auto_cancel: bool):
        logger.debug(f"[MOCK] setAutoCancel called with auto_cancel={auto_cancel}")

    @classmethod
    def setPriority(cls, priority):
        logger.debug(f"[MOCK] setPriority called with priority={priority}")

    @classmethod
    def setDefaults(cls, defaults):
        logger.debug(f"[MOCK] setDefaults called with defaults={defaults}")

    @classmethod
    def setOngoing(cls, persistent: bool):
        logger.debug(f"[MOCK] setOngoing called with persistent={persistent}")

    @classmethod
    def setOnlyAlertOnce(cls, state):
        logger.debug(f"[MOCK] setOnlyAlertOnce called with state={state}")

    @classmethod
    def build(cls):
        logger.debug("[MOCK] build called")

    @classmethod
    def setContentIntent(cls, pending_action_intent: PendingIntent):
        logger.debug(f"[MOCK] setContentIntent called with {pending_action_intent}")

    @classmethod
    def addAction(cls, *args):
        if len(args) == 1:
            logger.debug(f"[MOCK] addAction called with action={args[0]}")
        else:
            icon_int, action_text, pending_action_intent = args
            logger.debug(
                f"[MOCK] addAction called with icon={icon_int}, text={action_text}, intent={pending_action_intent}"
            )

    @classmethod
    def setShowWhen(cls, state):
        logger.debug(f"[MOCK] setShowWhen called with state={state}")

    @classmethod
    def setWhen(cls, time_ms):
        logger.debug(f"[MOCK] setWhen called with time_ms={time_ms}")

    @classmethod
    def setCustomContentView(cls, layout):
        logger.debug(f"[MOCK] setCustomContentView called with layout={layout}")

    @classmethod
    def setCustomBigContentView(cls, layout):
        logger.debug(f"[MOCK] setCustomBigContentView called with layout={layout}")

    @classmethod
    def setSubText(cls, text):
        logger.debug(f"[MOCK] setSubText called with text={text}")

    @classmethod
    def setColor(cls, color: Color) -> None:
        logger.debug(f"[MOCK] setColor called with color={color}")

    @classmethod
    def setVibrate(cls, state) -> None:
        logger.debug(f"[MOCK] setVibrate called with state={state}")


    @classmethod
    def setVisibility(cls, state) -> None:
        logger.debug(f"[MOCK] setVisibility called with state={state}")


class NotificationCompatBigTextStyle:
    def bigText(cls, body):
        logger.debug(f"[MOCK] NotificationCompatBigTextStyle.bigText called with body={body}")
        return cls

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


class Context:
    NOTIFICATION_SERVICE = "notification"
    VIBRATOR_SERVICE = "vibrator"

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

    @staticmethod
    def getExternalFilesDir(directory_type):
        logger.debug(f"[MOCK] Context.getExternalFilesDir called with type={directory_type}")
        return File("mock_external_files_dir")

    @staticmethod
    def getExternalCacheDir():
        logger.debug("[MOCK] Context.getExternalCacheDir called")
        return File("mock_external_cache_dir")

class MActivity(Context):
    def getSystemService(self):
        logger.debug("[MOCK] mActivity.getSystemService called")
        return self
    def runOnUiThread(self,runnable):
        logger.debug(f"[MOCK] mActivity.runOnUiThread called with runnable={runnable}")
        return self


class PythonActivity:
    def __init__(self):
        logger.debug("[MOCK] PythonActivity initialized")

    @staticmethod
    def mActivity():
        logger.debug("[MOCK] mActivity used")
        return MActivity()

    @staticmethod
    def startForeground(notification_id, builder_build, foreground_type):
        logger.debug(
            f"[MOCK] startForeground called with notification_id={notification_id}, builder.build()={builder_build}, foreground_type={foreground_type}")

    def setAutoRestartService(self):
        logger.debug("[MOCK] setAutoRestartService called")
        return self


class DummyIcon:
    icon = 101

    def __init__(self):
        logger.debug("[MOCK] DummyIcon initialized")



class PackageManager:
    @property
    def PERMISSION_GRANTED(self):
        logger.debug("[MOCK] PackageManager.PERMISSION_GRANTED called")
        return 1


class KeyEvent:
    ACTION_DOWN = 0
    KEYCODE_MEDIA_PLAY = 126
    KEYCODE_MEDIA_PAUSE = 127
    KEYCODE_MEDIA_PREVIOUS = 88
    KEYCODE_MEDIA_NEXT = 87

    def __init__(self, action, code):
        self.action = action
        self.code = code
        logger.debug(f"[MOCK] KeyEvent initialized with action={action}, code={code}")


class R_drawable:
    ic_media_previous = 0
    ic_media_pause = 1
    ic_media_play = 2
    ic_media_next = 3


class ActionBuilder:
    def __init__(self, icon, title, pending_intent):
        logger.debug(
            f"[MOCK] ActionBuilder initialized with icon={icon}, title={title}, intent={pending_intent}"
        )

    def build(self):
        logger.debug("[MOCK] ActionBuilder.build called")
        return self


class MediaSession:
    def __init__(self, context, tag):
        self._token = object()
        logger.debug(f"[MOCK] MediaSession initialized with context={context}, tag={tag}")

    def setFlags(self, flags):
        logger.debug(f"[MOCK] MediaSession.setFlags called with flags={flags}")
        return self

    def setCallback(self, callback):
        logger.debug(f"[MOCK] MediaSession.setCallback called with callback={callback}")
        return self

    def setActive(self, state):
        logger.debug(f"[MOCK] MediaSession.setActive called with state={state}")
        return self

    def setMetadata(self, metadata):
        logger.debug(f"[MOCK] MediaSession.setMetadata called with metadata={metadata}")
        return self

    def setPlaybackState(self, playback_state):
        logger.debug(f"[MOCK] MediaSession.setPlaybackState called with playback_state={playback_state}")
        return self

    def getSessionToken(self):
        logger.debug("[MOCK] MediaSession.getSessionToken called")
        return self._token

    def release(self):
        logger.debug("[MOCK] MediaSession.release called")

    def setCallsetCallbackback(self, callback):
        logger.debug(f"[MOCK] MediaSession.release called with callback={callback}")


class MediaSessionListener:
    def onPlay(self):
        pass
    def onPause(self):
        pass
    def onSeekTo(self):
        pass
    def onSkipToNext(self):
        pass
    def onSkipToPrevious(self):
        pass
class PlaybackState:
    ACTION_PLAY = 1
    ACTION_PAUSE = 2
    ACTION_SEEK_TO = 4
    ACTION_PLAY_PAUSE = 8
    ACTION_SKIP_TO_NEXT = 16
    ACTION_SKIP_TO_PREVIOUS = 32
    ACTION_FAST_FORWARD = 64
    ACTION_REWIND = 128
    STATE_PLAYING = 3
    STATE_PAUSED = 2


class PlaybackStateBuilder:
    def __init__(self):
        logger.debug("[MOCK] PlaybackStateBuilder initialized")

    def setState(self, state, position_ms, playback_speed):
        logger.debug(
            f"[MOCK] PlaybackStateBuilder.setState called with state={state}, position_ms={position_ms}, playback_speed={playback_speed}"
        )
        return self

    def setActions(self, actions):
        logger.debug(f"[MOCK] PlaybackStateBuilder.setActions called with actions={actions}")
        return self

    def build(self):
        logger.debug("[MOCK] PlaybackStateBuilder.build called")
        return self


class MediaMetadata:
    METADATA_KEY_TITLE = 'android.media.metadata.TITLE'
    METADATA_KEY_ARTIST = 'android.media.metadata.ARTIST'
    METADATA_KEY_DURATION = 'android.media.metadata.DURATION'


class MediaMetadataBuilder:
    def __init__(self):
        self._metadata = {}
        logger.debug("[MOCK] MediaMetadataBuilder initialized")

    def putString(self, key, value):
        self._metadata[key] = value
        logger.debug(f"[MOCK] MediaMetadataBuilder.putString called with key={key}, value={value}")
        return self

    def putLong(self, key, value):
        self._metadata[key] = value
        logger.debug(f"[MOCK] MediaMetadataBuilder.putLong called with key={key}, value={value}")
        return self

    def build(self):
        logger.debug(f"[MOCK] MediaMetadataBuilder.build called, returning {self._metadata}")
        return self


class MediaStyle:
    def __init__(self):
        logger.debug("[MOCK] MediaStyle initialized")

    def setMediaSession(self, token):
        logger.debug(f"[MOCK] MediaStyle.setMediaSession called with token={token}")
        return self

    def setShowActionsInCompactView(self, index):
        logger.debug(f"[MOCK] MediaStyle.setShowActionsInCompactView called with index={index}")
        return self


class MediaMetadataRetriever:
    def __init__(self):
        logger.debug("[MOCK] MediaMetadataRetriever initialized")

    def setDataSource(self, path):
        logger.debug(f"[MOCK] MediaMetadataRetriever.setDataSource called with path={path}")

    def getEmbeddedPicture(self):
        logger.debug("[MOCK] MediaMetadataRetriever.getEmbeddedPicture called")
        return None


# Now writing Knowledge from errors
# notify.(int, Builder.build()) # must be int
