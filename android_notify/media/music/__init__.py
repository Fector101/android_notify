import jnius.jnius
import time
import traceback


from android_notify.widgets.images import find_and_set_default_icon, get_img_absolute_path, get_bitmap_from_path

from jnius import autoclass, cast, PythonJavaClass, java_method

from android_notify.internal.android import get_active_notification_ids
from android_notify.internal.java_classes import Intent, PendingIntent, BuildVersion, String, BitmapFactory

NotificationCompatBuilder = autoclass('android.app.Notification$Builder')

from android_notify.config import on_android_platform, get_python_activity_context, get_package_name, \
    get_notification_manager, from_service_file, get_python_activity

from android_notify.internal.channels import create_channel
from android_notify.widgets.texts import set_title, set_message
from android_notify.internal.logger import logger


JAVA_FILE_NAME = "MyMediaCallback" # For Java <-> Python bridge

PythonActivity = autoclass('org.kivy.android.PythonActivity')
KeyEvent = autoclass('android.view.KeyEvent')

MediaSession = autoclass('android.media.session.MediaSession')
PlaybackState = autoclass('android.media.session.PlaybackState')
PlaybackStateBuilder = autoclass('android.media.session.PlaybackState$Builder')
MediaMetadata = autoclass('android.media.MediaMetadata')
MediaMetadataBuilder = autoclass('android.media.MediaMetadata$Builder')
MediaStyle = autoclass('android.app.Notification$MediaStyle')

#
# MediaSession = autoclass('android.support.v4.media.session.MediaSessionCompat')
# PlaybackState = autoclass('android.support.v4.media.session.PlaybackStateCompat')
# PlaybackStateBuilder = autoclass('android.support.v4.media.session.PlaybackStateCompat$Builder')
# MediaMetadata = autoclass('android.support.v4.media.MediaMetadataCompat')
# MediaMetadataBuilder = autoclass('android.support.v4.media.MediaMetadataCompat$Builder')
# MediaStyle = autoclass('androidx.media.app.NotificationCompat$MediaStyle')
#

java_bridge_class = f'{get_package_name()}.{JAVA_FILE_NAME}'
try:
    MyMediaCallback = autoclass(java_bridge_class)
    logger.info(f"Successfully loaded MyMediaCallback: {java_bridge_class}")
except jnius.jnius.JavaException as e:
    MyMediaCallback = None
    if e.classname == 'java.lang.ClassNotFoundException':
        logger.error(f"Didn't find: {java_bridge_class}, visit: docs-on-how-to-add.html")
    else:
        print(e)
        traceback.print_exc()

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
# TODO remove on kivy new version release it exists in kivy/mobile/_platform/android.py and is used in kivy/core/clipboard/clipboard_android.py
# test if this pattern also works for Flet if so then do not delete it
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
        logger.debug("nEventListener - PLAY EVENT RECEIVED")
        if _active_music_notification is not None:
            # _active_music_notification.showPauseIcon() # comment out because bound soundLoader play event to notification, leaving this comment for future reference when implement on Flet Apps
            _active_music_notification.soundLoader.play()
        if self.play_music:
            self.play_music()
        else:
            logger.debug("No play music callback was found")

    @java_method('()V')
    def onPause(self):
        logger.debug("nEventListener - PAUSE EVENT RECEIVED")
        if _active_music_notification is not None:
            # _active_music_notification.showPlayIcon() # comment out because bound soundLoader pause event to notification, leaving this comment for future reference when implement on Flet Apps
            _active_music_notification.soundLoader.pause()

        if self.pause_music:
            self.pause_music()
        else:
            logger.debug("No pause music callback was found")

    @java_method('(J)V')
    def onSeekTo(self, pos):
        logger.debug(f"nEventListener - SEEK EVENT RECEIVED: {pos}")
        if _active_music_notification is not None:
            # _active_music_notification.showPlayIcon() # comment out because bound soundLoader pause event to notification, leaving this comment for future reference when implement on Flet Apps
            _active_music_notification.soundLoader.seek(pos / 1000.0)
            # Sync MediaSession immediately after seek to update system position anchor
            _active_music_notification.updateProgressBar()
        if self.seek_music:
            self.seek_music(pos / 1000.0)
        else:
            logger.debug("No seek music callback was found")

    @java_method('()V')
    def onSkipToNext(self):
        logger.debug("nEventListener -SKIP NEXT EVENT RECEIVED")
        if _active_music_notification is not None and not _active_music_notification._has_next:
            return
        if self.next_music:
            self.next_music()
        else:
            logger.warning("No next music callback was found")

    @java_method('()V')
    def onSkipToPrevious(self):
        print("nEventListener -SKIP PREV EVENT RECEIVED")
        if _active_music_notification is not None and not _active_music_notification._has_prev:
            return
        if self.prev_music:
            self.prev_music()
        else:
            logger.warning("No prev music callback was found")

_active_music_notification = None


class MusicNotification:
    listener = Listener # so users can switch listener Class
    soundLoader = None
    notification_id = None
    builder = None

    def __init__(self, on_next=None, on_previous = None):
        self.already_built = None
        global _active_music_notification
        _active_music_notification = self

        self._update_interval = None
        self._artist = None
        self._title = None
        self._play_music = None
        self._pause_music = None
        self._seek_music = None
        self._next_music = on_next
        self._prev_music = on_previous
        self._has_next = True
        self._has_prev = True
        self._play_pause_index = 1

        self.on_next = on_next
        self.on_previous = on_previous

        self.channel_id = "music_channel"
        self.channel_name = "Music"
        self.notification_id = self.__get_unique_id()

        self.context = None
        self.callback = None
        self.session = None

        print("init ran")
        if on_android_platform():
            self.context = get_python_activity_context()
            self.builder = NotificationCompatBuilder(self.context, self.channel_id)
            try:
                # Run init on Android's UI thread (required by MediaSession)
                runnable = AndroidRunnable(self.__setup_media_session)
                self.context.runOnUiThread(runnable)
            except Exception as error_setting_controls:
                print(error_setting_controls)
                traceback.print_exc()

    # noinspection DuplicatedCode
    def __setup_media_session(self):
        """
        Initialized Media Session and Sets it's callbacks
        :return:
        """
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
        logger.debug("MediaSession initialization and callback setup complete!")

    # noinspection DuplicatedCode
    def build_notification(self, is_playing):
    # def build_notification(self, title, artist, is_playing, current_ms, duration_ms):
        """Fully builds and dispatches the media notification.

        This is a "heavy" operation - it rebuilds the entire notification
        including icons and actions. Called only on state changes
        (play/pause/seek/next/prev) to avoid flickering during seekbar drags.
        """
        if self.session is None:
            logger.error("MediaSession not initialized.")
            return
        print("running build....")
        length_of_song = self.soundLoader.length
        song_position = self.soundLoader.get_pos()
        logger.debug(f"Title: {self._title}, Artist: {self._artist}, Duration: {length_of_song}, song_position: {song_position}")

        set_title(builder=self.builder,title=self._title)
        set_message(builder=self.builder,message=self._artist)
        self.setLargeIcon(music_path=self.soundLoader.source)
        find_and_set_default_icon(self.builder)
        self.builder.setOngoing(is_playing)
        self.builder.setVisibility(1)# NotificationCompat.VISIBILITY_PUBLIC = 1 (show content on lock screen)
        add_intent_to_open_app(self.builder,notification_id=self.notification_id,_ignore_data=True,notification_title="",action_name="",data_object=None)
        self._add_buttons(is_playing=is_playing)
        # MediaStyle makes the notification show with a larger media layout and wires it to the MediaSession for lock-screen control
        style = MediaStyle()
        style.setMediaSession(self.session.getSessionToken())
        style.setShowActionsInCompactView(self._play_pause_index)
        self.builder.setStyle(style)

        # Attach metadata (title, artist, duration) to the MediaSession
        # so the system UI can display it
        metadata = (
            MediaMetadataBuilder()
            .putString(MediaMetadata.METADATA_KEY_TITLE, String(self._title))
            .putString(MediaMetadata.METADATA_KEY_ARTIST, String(self._artist))
            .putLong(MediaMetadata.METADATA_KEY_DURATION, int(length_of_song * 1000))
            .build()
        )
        self.session.setMetadata(metadata)
        # Update the playback state (position, playing/paused, available actions)
        self.updateProgressBar()

        manager = get_notification_manager()
        manager.notify(self.notification_id, self.builder.build())
        self.already_built=1
        #No manual updates, MediaSession playback state handles it in updateProgressBar
        # if is_playing:
        #     self._update_interval = Clock.schedule_interval(self.updateProgressBar, 1)
        # elif self._update_interval:
        #     self._update_interval.cancel()

    def updateProgressBar(self, _=None):
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

        if not self.soundLoader:
            return None
        current_ms = int(self.soundLoader.get_pos() * 1000)
        is_playing=self.soundLoader.state == "play"
        logger.debug(f"updating progress bar...{current_ms}")

        # NOTE: MediaSession playback state, updates progress bar without clock schedules
        actions = (
                PlaybackState.ACTION_PLAY
                | PlaybackState.ACTION_PAUSE
                | PlaybackState.ACTION_SEEK_TO
                | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_FAST_FORWARD
                | PlaybackState.ACTION_REWIND
        )
        if self._has_next:
            actions |= PlaybackState.ACTION_SKIP_TO_NEXT
        if self._has_prev:
            actions |= PlaybackState.ACTION_SKIP_TO_PREVIOUS
        state_builder = PlaybackStateBuilder()
        state = PlaybackState.STATE_PLAYING if is_playing else PlaybackState.STATE_PAUSED
        state_builder.setState(state, current_ms, 1.0)
        state_builder.setActions(actions)
        self.session.setPlaybackState(state_builder.build())
        return None

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
    def refresh(self):
        """Refresh the notification."""
        get_notification_manager().notify(self.notification_id,self.builder.build())

    def _add_buttons(self, is_playing):
        # Add prev, play/pause, and next action buttons using Android
        # built-in media icons from android.R$drawable.
        # Prev/next are only added when a track exists in that direction.
        play_or_pause_text = "Pause" if is_playing else "Play"
        play_pause_code = KeyEvent.KEYCODE_MEDIA_PAUSE if is_playing else KeyEvent.KEYCODE_MEDIA_PLAY
        R_drawable = autoclass('android.R$drawable')
        ActionBuilder = autoclass('android.app.Notification$Action$Builder')

        action_intents = []
        if self._has_prev:
            action_intents.append(
                (R_drawable.ic_media_previous, String("Previous"), KeyEvent.KEYCODE_MEDIA_PREVIOUS)
            )
        self._play_pause_index = len(action_intents)
        action_intents.append(
            (R_drawable.ic_media_pause if is_playing else R_drawable.ic_media_play,
             String(play_or_pause_text), play_pause_code)
        )
        if self._has_next:
            action_intents.append(
                (R_drawable.ic_media_next, String("Next"), KeyEvent.KEYCODE_MEDIA_NEXT)
            )

        actions = [
            ActionBuilder(icon, title, self.__create_media_button_intent(key_code)).build()
            for icon, title, key_code in action_intents
        ]

        # android.app.Notification$Builder appends to mActions on every setActions() / addAction()
        # Clear the internal ArrayList to avoid action duplication
        self.builder.mActions.clear()

        # Re-add the updated actions
        for action in actions:
            self.builder.addAction(action)

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


    def setSoundLoader(self, sound_load_instance):
        self.soundLoader = sound_load_instance
        self.soundLoader.bind(
            state=self._parse_state,
            on_load=lambda instance,v: self.build_notification(is_playing=1 if self.soundLoader.state=="play" else 0),
            on_seek=lambda _,pos:self.updateProgressBar()
        )

        # TODO Receive on seek

    def set_skip_available(self, has_next, has_prev):
        """Tell the notification whether prev/next tracks exist around the current one."""
        self._has_next = bool(has_next)
        self._has_prev = bool(has_prev)
        if not self.already_built or not self.soundLoader:
            return
        is_playing = self.soundLoader.state == "play"
        self._add_buttons(is_playing)
        self.updateProgressBar()
        self.refresh()

    def _parse_state(self, loader_instance,state):
        print(f'sound load state changed: {state}')
        if self.already_built:
            if state == 'play':
                # updateProgressBar - media session auto handles update
                # if self._update_interval is None:
                #     self._update_interval = Clock.schedule_interval(self.updateProgressBar, 1)
                self.showPauseIcon()
            elif state == 'pause':
                # updateProgressBar - media session auto handles update
                # if self._update_interval:
                #     self._update_interval.cancel()
                #     self._update_interval = None
                self.showPlayIcon()
        else:
            logger.error("Not built but trying play or pause")

    def showPauseIcon(self):
        logger.debug("showing pause icon")
        self._add_buttons(True)
        # On Android 13+, MediaSession playback state needs sync to display buttons properly
        self.updateProgressBar()
        self.refresh()

    def showPlayIcon(self):
        logger.debug("showing play icon")
        self._add_buttons(False)
        # On Android 13+, MediaSession playback state needs sync to display buttons properly
        self.updateProgressBar()
        self.refresh()

    def setTitle(self,title:str):
        self._title = title
        pass

    def setArtist(self,artist:str):
        self._artist = artist
        pass

