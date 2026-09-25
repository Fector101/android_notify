import traceback
from typing import Optional


from android_notify.internal.logger import logger
from android_notify.config import on_android_platform, get_python_activity_context, get_package_name, \
    get_notification_manager, on_flet_app
from android_notify.internal.java_classes import autoclass, cast,Intent, PendingIntent, BuildVersion, String, BitmapFactory
from android_notify.internal.android import get_unique_id
from android_notify.internal.intents import add_intent_to_open_app
from android_notify.internal.channels import create_channel
from android_notify.media.music.helper import JAVA_CALLBACK_FILE_CONTENT
from android_notify.widgets.images import find_and_set_default_icon, get_img_absolute_path, get_bitmap_from_path
from android_notify.widgets.texts import set_title, set_message


JAVA_FILE_NAME = "MediaSessionCallback"
# The bridge ships pre-compiled in a fixed package (io.github.fector101:android-notify-music-bridge)
# so users never have to copy or edit Java. `bridge_interface_class` matches the
# nested interface embedded in that Java class.
MUSIC_BRIDGE_PACKAGE = "org.android_notify.music"
bridge_interface_class = f'{MUSIC_BRIDGE_PACKAGE.replace(".", "/")}/{JAVA_FILE_NAME}$MediaSessionListener'

if on_android_platform():
    import jnius.jnius
    from jnius import PythonJavaClass, java_method
    NotificationCompatBuilder = autoclass('android.app.Notification$Builder')
    R_drawable = autoclass('android.R$drawable')
    ActionBuilder = autoclass('android.app.Notification$Action$Builder')
    KeyEvent = autoclass('android.view.KeyEvent')
    MediaSession = autoclass('android.media.session.MediaSession')
    PlaybackState = autoclass('android.media.session.PlaybackState')
    PlaybackStateBuilder = autoclass('android.media.session.PlaybackState$Builder')
    MediaMetadata = autoclass('android.media.MediaMetadata')
    MediaMetadataBuilder = autoclass('android.media.MediaMetadata$Builder')
    MediaStyle = autoclass('android.app.Notification$MediaStyle')
    MediaMetadataRetriever = autoclass('android.media.MediaMetadataRetriever')

    # MediaSession = autoclass('android.support.v4.media.session.MediaSessionCompat')
    # PlaybackState = autoclass('android.support.v4.media.session.PlaybackStateCompat')
    # PlaybackStateBuilder = autoclass('android.support.v4.media.session.PlaybackStateCompat$Builder')
    # MediaMetadata = autoclass('android.support.v4.media.MediaMetadataCompat')
    # MediaMetadataBuilder = autoclass('android.support.v4.media.MediaMetadataCompat$Builder')
    # MediaStyle = autoclass('androidx.media.app.NotificationCompat$MediaStyle')

    java_bridge_class = f'{MUSIC_BRIDGE_PACKAGE}.{JAVA_FILE_NAME}'
    try:
        MediaSessionCallback = autoclass(java_bridge_class)
        logger.info(f"Successfully loaded MediaSessionCallback: {java_bridge_class}")
    except jnius.jnius.JavaException as e:
        MediaSessionCallback = None
        if e.classname == 'java.lang.ClassNotFoundException':
            # Fall back to the legacy android.add_src layout {app_package}.MediaSessionCallback
            # (copy-pasted Java file). New setups should use the Maven artifact instead.
            legacy_bridge_class = f'{get_package_name()}.{JAVA_FILE_NAME}'
            if legacy_bridge_class != java_bridge_class:
                try:
                    MediaSessionCallback = autoclass(legacy_bridge_class)
                    bridge_interface_class = f'{get_package_name().replace(".", "/")}/{JAVA_FILE_NAME}$MediaSessionListener'
                    logger.warning(f"Bridge not found at '{java_bridge_class}', fell back to legacy: {legacy_bridge_class}")
                except jnius.jnius.JavaException:
                    logger.error("Couldn't find the media bridge anywhere. Add android-notify-music-bridge to "
                                 "android.gradle_dependencies (see docs/music-notifications.html), or add the "
                                 "legacy src/MediaSessionCallback.java via android.add_src.")
                    logger.info(JAVA_CALLBACK_FILE_CONTENT)
            else:
                logger.error("Media bridge missing: add android-notify-music-bridge to android.gradle_dependencies "
                             "(see docs/music-notifications.html), or add the legacy src/MediaSessionCallback.java "
                             "via android.add_src.")
                logger.info(JAVA_CALLBACK_FILE_CONTENT)
        else:
            logger.error(e)
            traceback.print_exc()

else:
    from android_notify.internal.facade import (
        NotificationCompatBuilder, R_drawable,
        ActionBuilder, KeyEvent, MediaSessionCallback,
        MediaSession,
        PlaybackState,
        PlaybackStateBuilder,
        MediaMetadata,
        MediaMetadataBuilder,
        MediaStyle,
        MediaMetadataRetriever,
    )
    PythonJavaClass = object
    java_method = lambda signature: (lambda func: func)  # Dummy decorator for non-Android platforms
    


# AndroidRunnable - run code on Android's main (UI) thread Android's MediaSession APIs MUST be created/accessed from
# the main/UI thread. This wraps a Python function in a java.lang.Runnable so it can be passed to Activity.runOnUiThread().
# TODO remove on Kivy new version release it exists in kivy/mobile/_platform/android.py and
#  is used in kivy/core/clipboard/clipboard_android.py
#  Test if this pattern also works for Flet if so then do not delete it
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
            logger.error(error_running_callback)
            traceback.print_exc()


_active_music_notification: Optional["MusicNotification"] = None
class MediaSessionListener(PythonJavaClass):
    __javainterfaces__ = [
        bridge_interface_class
        # org/android_notify/music/MediaSessionCallback$MediaSessionListener
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
        # _active_music_notification.showPauseIcon() # comment out because bound mediaController play event to notification, leaving this comment for future reference when implement on Flet Apps
        if self.play_music:
            self.play_music()
        else:
            logger.error("No play music callback was found")

    @java_method('()V')
    def onPause(self):
        logger.debug("nEventListener - PAUSE EVENT RECEIVED")
        # _active_music_notification.showPlayIcon() # comment out because bound mediaController pause event to notification, leaving this comment for future reference when implement on Flet Apps
        if self.pause_music:
            self.pause_music()
        else:
            logger.error("No pause music callback was found")

    @java_method('(J)V')
    def onSeekTo(self, pos):
        logger.debug(f"nEventListener - SEEK EVENT RECEIVED: {pos}")
        if self.seek_music:
            self.seek_music(pos / 1000.0)
            if _active_music_notification is not None:
                # Sync MediaSession immediately after seek to update system position anchor
                _active_music_notification.syncMediaSession()
        else:
            logger.error("No seek music callback was found")

    @java_method('()V')
    def onSkipToNext(self):
        logger.debug("nEventListener -SKIP NEXT EVENT RECEIVED")
        if self.next_music:
            self.next_music()
        else:
            logger.warning("No next music callback was found")

    @java_method('()V')
    def onSkipToPrevious(self):
        logger.debug("nEventListener -SKIP PREV EVENT RECEIVED")
        if self.prev_music:
            self.prev_music()
        else:
            logger.warning("No prev music callback was found")


# Users mediaController need to fulfill
class IMediaController:
    def __init__(self,media_controller):
        self.media_controller = media_controller

    def play(self):
        """
        To play audio/video.
        """
        self.media_controller.play()

    def pause(self):
        """
        To pause audio/video.
        """
        self.media_controller.pause()

    def seek(self, pos:float):
        """
        pos: is the milliseconds to change current playing position of media
        """
        self.media_controller.seek(pos)

    def get_pos(self) -> float:
        """
        This returns the current media position in seconds
        """
        return self.media_controller.get_pos()

    @property
    def length(self) -> float:
        """
        This returns the current media length in seconds
        """
        return self.media_controller.length

    def isMediaPlaying(self):
        """
        Checks if media state is equivalent to "play"
        """
        return self.media_controller.state == "play"


class MusicNotification:
    listener = MediaSessionListener # so users can switch listener Class if needed
    mediaController = None

    def __init__(self, on_next=None, on_previous = None):
        self.media_controller = None # In kivy mediaController can be SoundLoader
        self.mediaController = None
        self.already_built = False
        self._build_pending = False
        global _active_music_notification
        _active_music_notification = self

        # self._update_interval = None
        self._artist = None
        self._title = None
        self._media_style = None

        self.on_next = on_next
        self.on_previous = on_previous

        self.channel_id = "music_channel"
        self.channel_name = "Music"
        self.notification_id = get_unique_id()

        self.context = None
        self.callback = None
        self.session = None # for auto seek updates, lock-screen control and speakers

        if on_android_platform():
            self.context = get_python_activity_context()
            self.builder = NotificationCompatBuilder(self.context, self.channel_id)
            try:
                if self.context is not None: # lint
                    # Run init on Android's UI thread (required by MediaSession)
                    runnable = AndroidRunnable(self.__setup_media_session)
                    self.context.runOnUiThread(runnable)
            except Exception as error_setting_controls:
                logger.error(error_setting_controls)
                traceback.print_exc()

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
        self.session.setActive(True)

        # Wire the Java callback (MediaSessionCallback) to the Python MediaSessionListener
        if MediaSessionCallback:
            self.listener = self.listener()
            self.listener.play_music = self.media_controller.play
            self.listener.pause_music = self.media_controller.pause
            self.listener.seek_music = self.media_controller.seek

            self.listener.next_music = self.on_next
            self.listener.prev_music = self.on_previous

            self.callback = MediaSessionCallback(self.listener)
            self.session.setCallback(self.callback)
            logger.debug("MediaSession initialization and callback setup complete!")
        else: # Pyroid3 and Flet
            logger.error("Media bridge is unavailable, media buttons will be inert. Add android-notify-music-bridge to "
                         "android.gradle_dependencies (see docs/music-notifications.html).")
        create_channel( name=self.channel_name, id__=self.channel_id, importance="medium")

        # If a build was deferred while the MediaSession was being created,
        # finish it now that the session exists.
        if self._build_pending and self.mediaController is not None:
            self._build_or_defer(is_playing=self.media_controller.isMediaPlaying())

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

    def _format_buttons(self):
        # Add prev, play/pause, and next action buttons using Android
        # built-in media icons from android.
        # Prev/next are only added when a self.on_next and/or self.on_previous exists.
        is_playing = self.media_controller.isMediaPlaying()
        play_or_pause_text = "Pause" if is_playing else "Play"
        play_pause_code = KeyEvent.KEYCODE_MEDIA_PAUSE if is_playing else KeyEvent.KEYCODE_MEDIA_PLAY


        action_intents = []
        if self.on_previous:
            action_intents.append(
                (R_drawable.ic_media_previous, String("Previous"), KeyEvent.KEYCODE_MEDIA_PREVIOUS)
            )
        action_intents.append(
            (R_drawable.ic_media_pause if is_playing else R_drawable.ic_media_play,
             String(play_or_pause_text), play_pause_code)
        )
        if self.on_next:
            action_intents.append(
                (R_drawable.ic_media_next, String("Next"), KeyEvent.KEYCODE_MEDIA_NEXT)
            )

        actions = [
            ActionBuilder(icon, title, self.__create_media_button_intent(key_code)).build()
            for icon, title, key_code in action_intents
        ]

        self.builder.mActions.clear()

        for action in actions:
            self.builder.addAction(action)

    def _parse_state(self, _,state): #_ is loader_instance
        logger.debug(f'sound load state changed: {state}')
        if not self.already_built:
            return None
        else:
            logger.error("Not built but trying play or pause")

        if state == 'play':
            self.showPauseIcon()
        elif state in ('pause', 'stop'):
            self.showPlayIcon()
        return None

    @staticmethod
    def _sound_is_loaded(sound):
        """True if the sound's on_load has already fired (player is ready)."""
        if getattr(sound, "_player_ready", False):
            return True
        try:
            # Plain Kivy Sound: length is only available once loaded.
            return bool(getattr(sound, "length", 0))
        except Exception as error_getting_length_value:
            logger.error(error_getting_length_value)
            traceback.print_exc()
            return False

    def _build_or_defer(self, is_playing):
        """Build the notification now, or defer once the MediaSession exists.

        build_notification bails out when the MediaSession isn't created yet;
        queue the build so __setup_media_session retries it as soon as the
        session is ready.
        """
        if self.session is not None:
            self.build_notification(is_playing=is_playing)
        else:
            self._build_pending = True

    def setMediaController(self, sound_load_instance: object) -> None:
        self.media_controller = IMediaController(sound_load_instance)
        try:
            if not on_flet_app():
                self.mediaController.bind(
                    state=self._parse_state,
                    on_load=lambda instance,v: self._build_or_defer(is_playing=self.media_controller.isMediaPlaying()),
                    on_seek=lambda _,pos: self.syncMediaSession()
                )
        except Exception as failed_to_bind_to_value:
            logger.error(failed_to_bind_to_value)
            traceback.print_exc()
        # If the sound was already loaded when we bound to it, it's on_load
        # has already fired and will never fire again - build now instead.
        if not self.already_built and self._sound_is_loaded(sound_load_instance):
            self._build_or_defer(is_playing=1 if self.media_controller.isMediaPlaying() else 0)

    def build_notification(self, is_playing):
        """Fully builds and dispatches the media notification.

        This is a "heavy" operation - it rebuilds the entire notification
        including icons and actions. Called only on state changes
        (play/pause/seek/next/prev) to avoid flickering during seekbar drags.
        """
        logger.debug("running build....")

        if self.session is None:
            logger.error("MediaSession not initialized.")
            return

        length_of_song = self.media_controller.length
        song_position = self.media_controller.get_pos()

        logger.debug(f"Title: {self._title}, Artist: {self._artist}, Duration: {length_of_song}, song_position: {song_position}")

        set_title(builder=self.builder,title=self._title)
        set_message(builder=self.builder,message=self._artist)
        self.setLargeIcon(music_path=self.mediaController.source)
        find_and_set_default_icon(self.builder)
        self.builder.setOngoing(is_playing)
        self.builder.setVisibility(1)# NotificationCompat.VISIBILITY_PUBLIC = 1 (show content on lock screen)
        add_intent_to_open_app(self.builder,notification_id=self.notification_id,_ignore_data=True,notification_title="",action_name="",data_object=None)
        self._format_buttons()

        # MediaStyle makes the notification show with a larger media layout and wires it to the MediaSession for lock-screen control and speakers
        style = MediaStyle()
        style.setMediaSession(self.session.getSessionToken())
        style.setShowActionsInCompactView(1 if self.on_previous else 0)
        self._media_style = style
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
        self.syncMediaSession()

        manager = get_notification_manager()
        manager.notify(self.notification_id, self.builder.build())
        self.already_built=1
        # A build happened: consume any queued build request (see setSoundLoader).
        self._build_pending = False

    def set_Next_and_Prev(self, new_next=None, new_prev=None):
        """Tell the notification whether prev/next tracks exist around the current one."""
        if new_next:
            self.on_next = new_next
        if new_prev:
            self.on_previous = new_prev

        if not self.already_built or not self.mediaController:
            return

        self._format_buttons()
        self.syncMediaSession()
        if self._media_style is not None:
            self._media_style.setShowActionsInCompactView(1 if self.on_previous else 0)
            self.builder.setStyle(self._media_style)
        self.refresh()

    def showPauseIcon(self):
        logger.debug("showing pause icon")
        self._format_buttons()
        # On Android 13+, MediaSession playback state needs sync to display buttons properly
        self.syncMediaSession()
        self.refresh()

    def showPlayIcon(self):
        logger.debug("showing play icon")
        self._format_buttons()
        # On Android 13+, MediaSession playback state needs sync to display buttons properly
        self.syncMediaSession()
        self.refresh()

    def setTitle(self,title:str):
        self._title = title

    def setArtist(self,artist:str):
        self._artist = artist

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
                retriever = MediaMetadataRetriever()
                retriever.setDataSource(music_path)
                art_bytes = retriever.getEmbeddedPicture()
                if art_bytes:
                    bitmap = BitmapFactory.decodeByteArray(art_bytes, 0, len(art_bytes))
                    self.builder.setLargeIcon(bitmap)
            except Exception as error_getting_art_bytes:
                logger.exception(error_getting_art_bytes)
                traceback.print_exc()

    def syncMediaSession(self):
        """
        This syncs notification Slider position and buttons with current Media state
        This method doesn't require polling, that's auto handled by Android
        Only call once when Media position or state changes by user action.
        """
        # This method is only achieved by updating the MediaSession playback state.
        # NOTE: MediaSession playback state updates progress bar without clock schedules
        if self.session is None:
            return None

        if not self.mediaController:
            return None

        is_playing = self.media_controller.isMediaPlaying()
        current_ms = int(self.media_controller.get_pos() * 1000)
        logger.debug(f"updating progress bar to milliseconds:{current_ms}")

        actions = (
                PlaybackState.ACTION_PLAY
                | PlaybackState.ACTION_PAUSE
                | PlaybackState.ACTION_SEEK_TO
                | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_FAST_FORWARD
                | PlaybackState.ACTION_REWIND
        )
        if self.on_next:
            actions |= PlaybackState.ACTION_SKIP_TO_NEXT
        if self.on_previous:
            actions |= PlaybackState.ACTION_SKIP_TO_PREVIOUS
        state_builder = PlaybackStateBuilder()
        state = PlaybackState.STATE_PLAYING if is_playing else PlaybackState.STATE_PAUSED
        state_builder.setState(state, current_ms, 1.0)
        state_builder.setActions(actions)
        self.session.setPlaybackState(state_builder.build())
        return None

    def refresh(self):
        """Refresh the notification."""
        if self.already_built:
            get_notification_manager().notify(self.notification_id,self.builder.build())
        else:
            logger.warning("Can't refresh notification because it doesn't have Base parameters created in MusicNotification.build_notification")

    def release(self):
        """Clean up resources when the app shuts down."""
        if self.session:
            self.session.setActive(False)
            self.session.release()
