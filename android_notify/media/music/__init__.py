# noinspection PyUnusedLocal,DuplicatedCode,PyTypeChecker
import time
import traceback

from android_notify.widgets.images import find_and_set_default_icon, get_img_absolute_path, get_bitmap_from_path
from jnius import autoclass, cast, PythonJavaClass, java_method

from android_notify.internal.android import get_active_notification_ids
from android_notify.internal.java_classes import (  # noqa: re-exported for main.py
    Context, Intent, PendingIntent, NotificationManager, NotificationCompatBuilder,
    NotificationChannel, BuildVersion, String, BitmapFactory
)
from android_notify.config import on_android_platform, get_python_activity_context, get_package_name, \
    get_notification_manager, from_service_file, get_python_activity

from android_notify.internal.channels import create_channel
from android_notify.widgets.texts import set_title, set_message
from android_notify.internal.logger import logger
from android_notify import logger as android_notify_logger
import logging




JAVA_FILE_NAME = "MyMediaCallback" # For Java <-> Python bridge

PythonActivity = autoclass('org.kivy.android.PythonActivity')
KeyEvent = autoclass('android.view.KeyEvent')
#
# MediaSession = autoclass('android.support.v4.media.session.MediaSessionCompat')
# PlaybackState = autoclass('android.support.v4.media.session.PlaybackStateCompat')
# PlaybackStateBuilder = autoclass('android.support.v4.media.session.PlaybackStateCompat$Builder')
# MediaMetadata = autoclass('android.support.v4.media.MediaMetadataCompat')
# MediaMetadataBuilder = autoclass('android.support.v4.media.MediaMetadataCompat$Builder')
# MediaStyle = autoclass('androidx.media.app.NotificationCompat$MediaStyle')
#

MediaSession = autoclass('android.media.session.MediaSession')
PlaybackState = autoclass('android.media.session.PlaybackState')
PlaybackStateBuilder = autoclass('android.media.session.PlaybackState$Builder')
MediaMetadata = autoclass('android.media.MediaMetadata')
MediaMetadataBuilder = autoclass('android.media.MediaMetadata$Builder')
MediaStyle = autoclass('android.app.Notification$MediaStyle')

MyMediaCallback = autoclass(f'{get_package_name()}.{JAVA_FILE_NAME}')

def get_intent_for_launching_app():
    try:
        context = get_python_activity_context()
        package_manager = context.getPackageManager()
        package_name = context.getPackageName()
        return package_manager.getLaunchIntentForPackage(package_name)
    except Exception as error_getting_default_intent_for_launching_app:
        print(error_getting_default_intent_for_launching_app)
        traceback.print_exc()
        return None

def add_intent_to_open_app(builder, action_name, notification_title, notification_id, data_object,_ignore_data=False):
    context = get_python_activity_context()
    PythonActivity = get_python_activity()
    intent = get_intent_for_launching_app() or Intent(context, PythonActivity)
    intent.setFlags(
        Intent.FLAG_ACTIVITY_CLEAR_TOP |  # Makes Sure tapping notification always brings the existing instance of app forward.
        Intent.FLAG_ACTIVITY_SINGLE_TOP |  # If the activity is already at the top, reuse it instead of creating a new instance.
        Intent.FLAG_ACTIVITY_NEW_TASK
        # Required when starting an Activity from a Service; ignored when starting from another Activity.
    )
    if not _ignore_data:
        pass
        # add_data_to_intent(intent, notification_title, notification_id, str(action_name), data_object)
    pending_intent = PendingIntent.getActivity(
        context, notification_id,
        intent, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
    )
    builder.setContentIntent(pending_intent)
    if not _ignore_data:
        logger.debug(
            f'data for opening app-  notification_title: {notification_title}, notification_id: {notification_id}, notification_name: {action_name}')


# ---------------------------------------------------
# AndroidRunnable - run code on Android's main (UI) thread
# ---------------------------------------------------
# Android's MediaSession APIs MUST be created/accessed from the
# main/UI thread. This wraps a Python function in a java.lang.Runnable
# so it can be passed to Activity.runOnUiThread().
class AndroidRunnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __javacontext__ = 'app'

    def __init__(self, callback_func):
        super().__init__()
        self.callback_func = callback_func

    @java_method('()V')
    def run(self):
        try:
            self.callback_func()
        except Exception as error_running_callback:
            print(error_running_callback)
            traceback.print_exc()

class Listener(PythonJavaClass):
    __javainterfaces__ = [
        get_package_name().replace(".","/")+'/MyMediaCallback$Listener'
    ]

    __javacontext__ = 'app'

    def __init__(self, play_music=None, pause_music=None, seek_music=None, next_music=None, prev_music=None):
        super().__init__()
        self.play_music = play_music
        self.pause_music = pause_music
        self.seek_music = seek_music
        self.next_music = next_music
        self.prev_music = prev_music

    @java_method('()V')
    def onPlay(self):
        logger.debug("jListener - PLAY EVENT RECEIVED")
        self.play_music()

    @java_method('()V')
    def onPause(self):
        logger.debug("jListener - PAUSE EVENT RECEIVED")
        self.pause_music()

    @java_method('(J)V')
    def onSeekTo(self, pos):
        logger.debug(f"jListener - SEEK EVENT RECEIVED: {pos}")
        self.seek_music(pos / 1000.0)

    @java_method('()V')
    def onSkipToNext(self):
        logger.debug("jListener -SKIP NEXT EVENT RECEIVED")
        self.next_music()

    @java_method('()V')
    def onSkipToPrevious(self):
        print("jListener -SKIP PREV EVENT RECEIVED")
        self.prev_music()

class MusicNotification:
    listener = Listener # so users can switch listener Class
    def __init__(self,
                 play_music=None,
                 pause_music=None,
                 seek_music=None,
                 next_music=None,
                 prev_music=None
         ):
        self._play_music = play_music
        self._pause_music = pause_music
        self._seek_music = seek_music
        self._next_music = next_music
        self._prev_music = prev_music

        self.channel_id = "music_channel"
        self.channel_name = "Music"
        self.notification_id = self.__get_unique_id()

        self.context = None
        self.callback = None
        self.session = None

        if on_android_platform():
            self.context = get_python_activity_context()
            self.builder = NotificationCompatBuilder(self.context, self.channel_id)
            try:
                # Run init on Android's UI thread (required by MediaSession)
                runnable = AndroidRunnable(self.__init_media_session_on_main)
                self.context.runOnUiThread(runnable)
            except Exception as error_setting_controls:
                print(error_setting_controls)
                traceback.print_exc()

    # noinspection DuplicatedCode
    def __init_media_session_on_main(self):
        logger.debug("Initializing MediaSession explicitly on Native Android UI Thread...")

        # MediaSession: the central hub for media control.
        # Flag 1 = FLAG_HANDLES_TRANSPORT_CONTROLS
        # Flag 2 = FLAG_HANDLES_MEDIA_BUTTONS
        self.session = MediaSession(self.context, get_package_name()+".MusicSession")
        self.session.setFlags(1 | 2)

        # Wire the Java callback (MyMediaCallback) to the Python Listener

        self.listener = self.listener()
        self.listener.play_music = self._play_music
        self.listener.pause_music = self._pause_music
        self.listener.seek_music = self._seek_music
        self.listener.next_music = self._next_music
        self.listener.prev_music = self._prev_music

        self.callback = MyMediaCallback(self.listener)
        self.session.setCallback(self.callback)
        self.session.setActive(True)
        create_channel( name=self.channel_name, id__=self.channel_id, importance="medium")
        logger.debug("MediaSession initialization complete!")

    # noinspection DuplicatedCode
    def build_notification(self, title, artist, is_playing, current_ms, duration_ms):
        """Fully builds and dispatches the media notification.

        This is a "heavy" operation - it rebuilds the entire notification
        including icons and actions. Called only on state changes
        (play/pause/seek/next/prev) to avoid flickering during seekbar drags.
        """
        if self.session is None:
            logger.error("MediaSession not initialized.")
            return

        set_title(builder=self.builder,title=title)
        set_message(builder=self.builder,message=artist)
        find_and_set_default_icon(self.builder)

        self.builder.setOngoing(is_playing)
        self.builder.setVisibility(1)# VISIBILITY_PUBLIC = 1 (show content on lock screen)

        # Tapping the notification opens the app
        add_intent_to_open_app(self.builder,notification_id=self.notification_id,_ignore_data=True,notification_title="",action_name="",data_object=None)
        self.__add_buttons(is_playing=is_playing,builder=self.builder)
        # MediaStyle makes the notification show with a larger media
        # layout and wires it to the MediaSession for lock-screen control
        style = MediaStyle()
        style.setMediaSession(self.session.getSessionToken())
        self.builder.setStyle(style)

        # Attach metadata (title, artist, duration) to the MediaSession
        # so the system UI can display it
        metadata = (
            MediaMetadataBuilder()
            .putString(MediaMetadata.METADATA_KEY_TITLE, String(title))
            .putString(MediaMetadata.METADATA_KEY_ARTIST, String(artist))
            .putLong(MediaMetadata.METADATA_KEY_DURATION, int(duration_ms))
            .build()
        )
        self.session.setMetadata(metadata)
        # Update the playback state (position, playing/paused, available actions)
        self.updateProgressBar(current_ms, is_playing)

        manager = get_notification_manager()
        manager.notify(self.notification_id, self.builder.build())

    # noinspection DuplicatedCode
    def updateProgressBar(self, current_ms, is_playing):
        """Call every ~1 second by Kivy Clock to keep seekbar updated.

        Only calls setPlaybackState() - lightweight, no notification rebuild.
        This avoids interrupting the user if they're dragging the seekbar.


        Updates the MediaSession playback state.

        This is the "lightweight" update - it only calls
        setPlaybackState() without rebuilding the notification.
        Called both by the periodic timer (every 1s) and by
        build_notification() on state changes.
        """
        if self.session is None:
            return

        actions = (
                PlaybackState.ACTION_PLAY
                | PlaybackState.ACTION_PAUSE
                | PlaybackState.ACTION_SEEK_TO
                | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_SKIP_TO_NEXT
                | PlaybackState.ACTION_SKIP_TO_PREVIOUS
                | PlaybackState.ACTION_FAST_FORWARD
                | PlaybackState.ACTION_REWIND
        )
        state_builder = PlaybackStateBuilder()
        state = PlaybackState.STATE_PLAYING if is_playing else PlaybackState.STATE_PAUSED
        state_builder.setState(state, int(current_ms), 1.0)
        state_builder.setActions(actions)
        self.session.setPlaybackState(state_builder.build())

    def release(self):
        """Clean up resources when the app shuts down."""
        if self.session:
            self.session.setActive(False)
            self.session.release()

    # noinspection DuplicatedCode
    def __create_media_button_intent(self, key_code):
        """Creates a PendingIntent for a notification action button.

        Each button (prev, play/pause, next) sends a broadcast with a
        KeyEvent matching the desired action. MediaStyle.setMediaSession()
        routes the tap through MediaSession.Callback instead.
        """
        if not self.context:
            return None
        intent = Intent(Intent.ACTION_MEDIA_BUTTON)
        intent.setPackage(self.context.getPackageName())

        event = KeyEvent(KeyEvent.ACTION_DOWN, key_code)
        parcelable_event = cast('android.os.Parcelable', event)
        intent.putExtra(Intent.EXTRA_KEY_EVENT, parcelable_event)

        flag = PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 23 else 0
        return PendingIntent.getBroadcast(self.context, key_code, intent, flag | PendingIntent.FLAG_UPDATE_CURRENT)

    def __add_buttons(self, is_playing,builder):
        # Add prev, play/pause, and next action buttons using Android
        # built-in media icons from android.R$drawable
        play_pause_text = "Pause" if is_playing else "Play"
        play_pause_code = KeyEvent.KEYCODE_MEDIA_PAUSE if is_playing else KeyEvent.KEYCODE_MEDIA_PLAY
        R_drawable = autoclass('android.R$drawable')

        builder.addAction(
            R_drawable.ic_media_previous, String("Previous"),
            self.__create_media_button_intent(KeyEvent.KEYCODE_MEDIA_PREVIOUS)
        )
        builder.addAction(
            R_drawable.ic_media_pause if is_playing else R_drawable.ic_media_play,
            String(play_pause_text),
            self.__create_media_button_intent(play_pause_code)
        )
        builder.addAction(
            R_drawable.ic_media_next, String("Next"),
            self.__create_media_button_intent(KeyEvent.KEYCODE_MEDIA_NEXT)
        )

    @staticmethod
    def __to_str(string__):
        value = str(string__) # for weird values
        return String(value)

    @staticmethod
    def __get_unique_id():
        if not on_android_platform():
            return 0

        if from_service_file():
            return int(time.time() * 1000) % 2_147_483_647

        notification_id=1
        try:
            ids_in_tray = get_active_notification_ids(notification_manager = get_notification_manager())
            while notification_id in ids_in_tray:
                if notification_id not in ids_in_tray:
                    break
                notification_id = notification_id + 1
        except Exception as error_getting_id_that_is_not_in_tray:
            logger.exception(error_getting_id_that_is_not_in_tray)
            traceback.print_exc()
        return notification_id

    def setLargeIcon(self,music_path=None,img_path=None):
        if img_path:
            image_absolute_path = get_img_absolute_path(img_path)
            bitmap = get_bitmap_from_path(image_absolute_path)
            if bitmap:
                self.builder.setLargeIcon(bitmap)
            else:
                logger.error("Failed getting bitmap from path")
        elif music_path:
            try:
                MediaMetadataRetriever = autoclass('android.media.MediaMetadataRetriever')
                retriever = MediaMetadataRetriever()
                retriever.setDataSource(music_path)
                art_bytes = retriever.getEmbeddedPicture()
                if art_bytes:
                    bitmap = BitmapFactory.decodeByteArray(art_bytes, 0, len(art_bytes))
                    self.builder.setLargeIcon(bitmap)
            except Exception as error_getting_art_bytes:
                logger.exception(error_getting_art_bytes)
                traceback.print_exc()

        manager = get_notification_manager()
        manager.notify(self.notification_id, self.builder.build())

