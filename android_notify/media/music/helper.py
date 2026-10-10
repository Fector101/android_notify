"""
    SoundLoader with events
    __events__ = ('on_play', 'on_stop', 'on_pause', 'on_load', 'on_seek', 'on_complete')

"""

import os
from android_notify.internal.logger import logger
from android_notify.config import on_android_platform
from android_notify.internal.permissions import ask_audio_permission, has_permission_to_read_audio

try:
    from kivy.properties import ObjectProperty
    from kivy.event import EventDispatcher
except:
    logger.warning("Kivy not found.")
    EventDispatcher = object
    ObjectProperty = lambda default: None  # Dummy property for non-Kivy environments



if on_android_platform():
    from jnius import autoclass, PythonJavaClass, java_method, jnius

    MediaPlayer = autoclass('android.media.MediaPlayer')
    class PlayerReadyListener(PythonJavaClass):
        __javainterfaces__ = ['android/media/MediaPlayer$OnPreparedListener']
        __javacontext__ = 'app'

        def __init__(self, on_player_ready):
            super().__init__()
            self.on_player_ready = on_player_ready

        # noinspection PyUnusedLocal
        @java_method('(Landroid/media/MediaPlayer;)V')
        def onPrepared(self, mp):
            self.on_player_ready()


    class CompletionListener(PythonJavaClass):
        __javainterfaces__ = ['android/media/MediaPlayer$OnCompletionListener']
        __javacontext__ = 'app'

        def __init__(self, on_player_complete):
            super().__init__()
            self.on_player_complete = on_player_complete

        # noinspection PyUnusedLocal
        @java_method('(Landroid/media/MediaPlayer;)V')
        def onCompletion(self, mp):
            self.on_player_complete()
else:
    class MediaPlayer:
        def setDataSource(self,path=None,context=None,uri=None):
            pass
        def setOnPreparedListener(self,callback):
            pass
        def setOnCompletionListener(self,callback):
            pass
        def prepareAsync(self):
            pass
        def start(self):
            pass
        def pause(self):
            pass
        def stop(self):
            pass
        def seekTo(self,sec):
            pass
        def release(self):
            pass
        @classmethod
        def getCurrentPosition(cls):
            return 0
        @classmethod
        def getDuration(cls):
            return 0

    class PlayerReadyListener:
        pass

    class CompletionListener:
        pass
    PythonJavaClass = object
    java_method = lambda signature: (lambda func: func)  # Dummy decorator for non-Android platforms

class SoundLoader(EventDispatcher):
    _instance = None
    _player = None
    _player_ready = False
    source = ''
    callback = None
    state = ObjectProperty('stop')

    length = property(lambda self: self._get_length(),
                      doc="Get length of the sound (in seconds).")
    loop=False

    __events__ = ('on_play', 'on_stop', 'on_pause', 'on_load', 'on_seek', 'on_complete')

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        # Prevent re-running Kivy's setup logic on subsequent instantiations
        if getattr(self, "_initialized", False):
            return

        super().__init__(**kwargs)  # Crucial for Kivy Property & Event bindings
        self._initialized = True

    @classmethod
    def load(cls, source, use_path=False):
        """Load a source into the shared MediaPlayer.

        source: an absolute file path or a "content://" URI.
        use_path: force the file-path datasource logic even when the source looks
            like a content URI. Defaults to False, in which case content://
            sources are opened through the resolver (scoped storage safe).
        """
        instance=cls()
        instance.source = source

        if str(source).startswith("content://"):
            logger.info(f"audio source: {source}")
        else:
            logger.info(f"audio source: {os.path.abspath(source)}")
        instance._player_ready = False
        instance._player = MediaPlayer()
        try:
            if not use_path and str(source).startswith("content://"):
                from android_notify.config import get_python_activity_context
                from android_notify.internal.java_classes import Uri
                context = get_python_activity_context()
                instance._player.setDataSource(context, Uri.parse(source))
            else:
                instance._player.setDataSource(source)
        except jnius.JavaException as e:
            if "Permission denied" in str(e):
                logger.error("Permission denied while loading sound source.")
            else:
                logger.error(e)
            instance._player.release()
            instance._player = None
            instance._player_ready = False
            return None
        # Keep strong refs to the Pyjnius proxies while MediaPlayer holds them,
        # otherwise garbage collection can drop the callbacks before they fire.
        instance._ready_listener = PlayerReadyListener(instance.on_player_ready)
        instance._completion_listener = CompletionListener(instance.on_player_complete)
        instance._player.setOnPreparedListener(instance._ready_listener)
        instance._player.setOnCompletionListener(instance._completion_listener)
        instance._player.prepareAsync()
        return instance._instance

    def on_player_ready(self):
        """Called by PlayerReadyListener when MediaPlayer is ready."""
        self._player_ready = True
        logger.debug("on_load dispatched")
        self.dispatch("on_load",'')

    def on_player_complete(self):
        """Called by CompletionListener when the track reaches its end."""
        if not self.loop:
            self.state = "stop"
        logger.debug("sound Dispatching: COMPLETE")
        self.dispatch("on_complete", self._player)
        if self.loop:
            self.seek(0)
            self._player.start()

    def get_pos(self):
        """Get current playback position in seconds."""
        if not self._player or not self._player_ready:
            logger.warning("Warning player is not ready... get_pos")
            return 0.0

        raw = self._player.getCurrentPosition() / 1000.0
        pos = raw

        duration = self._player.getDuration() / 1000.0
        if pos < 0:
            pos = 0
        elif 0 < duration < pos:
            pos = duration

        # logger.debug(f"read_pos: raw_pos={raw:.3f} duration={duration:.3f} returning={pos}")
        return pos

    def play(self):
        """Resume playback."""
        if not self._player or not self._player_ready:
            logger.warning("Warning player is not ready... no play")
            return None
        self._player.start()
        self.state = 'play'
        logger.debug("sound dispatching: PLAY")
        self.dispatch("on_play",self._player)
        return None

    def pause(self):
        """Pause playback."""
        if not self._player or not self._player_ready:
            logger.warning("Warning player is not ready... no pause")
            return None
        self._player.pause()
        self.state = 'pause'
        logger.debug("sound dispatching: PAUSE")
        self.dispatch("on_pause",self._player)
        return None

    def stop(self):
        if not self._player:
            return
        self._player.stop()
        self.state = 'stop'

    def _get_length(self):
        if not self._player or not self._player_ready:
            logger.warning("Warning player is not ready... no _get_length")
            return None

        return self._player.getDuration() / 1000.0

    def seek(self, position):
        """Seek to a position (sec = seconds from start)."""
        if not self._player or not self._player_ready:
            logger.warning("Warning player is not ready...no seek")
            return None
        self._player.seekTo(int(position * 1000))
        logger.debug(f"sound dispatching: SEEK {position:.1f}s")
        self.dispatch("on_seek",'')
        return None

    def unload(self):
        """Unload the file from memory."""
        if self._player:
            self._player.release()
        else:
            logger.warning("Warning player not loaded.")

    def on_play(self,player):
        pass

    def on_stop(self,player):
        pass

    def on_pause(self,player):
        pass

    def on_load(self,player):
        pass

    def on_seek(self,player):
        pass

    def on_complete(self, player):
        pass


class MediaPermissionHandler:
    __requesting_permission = False

    @classmethod
    def has_permission_to_access_audio_files(cls):
        """
        Checks if app has permission to read the audio files
        :return: True if it's allowed, False otherwise
        """
        return has_permission_to_read_audio()

    @classmethod
    def ask_permission_to_access_audio_files(cls, callback=None):
        """
        Asks permission to read the audio files
        """

        if cls.__requesting_permission:
            logger.warning("still requesting permission to reading audio files")
            return

        def requesting_state(state):
            cls.__requesting_permission = state

        ask_audio_permission(callback=callback, set_requesting_state=requesting_state)


# RELICS --- I'm keeping these for visible reference, for when I implement other features

# def has_permission_to_access_files():
#     try:
#         return autoclass('android.os.Environment').isExternalStorageManager()
#     except Exception as error_checking_permission_state:
#         logger.error(error_checking_permission_state)
#         return False
#
# def requestAllFilesAccess():
#     """Requests 'All Files Access' permission for Android 11+"""
#     if not on_android_platform():
#         return None
#     from android_notify.config import get_python_activity_context
#     from android_notify.internal.java_classes import Intent
#     Settings = autoclass('android.provider.Settings')
#     Uri = autoclass('android.net.Uri')
#     mActivity = get_python_activity_context()
#     if not has_permission_to_access_files():
#         try:
#             intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
#             print(f"package:{mActivity.getPackageName()}")
#             intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}"))
#             mActivity.startActivity(intent)
#         except Exception as error_opening_permission_screen:
#             print("PermissionHandler.requestAllFilesAccess --> ", error_opening_permission_screen)
#     print("requestAllFilesAccess OK")
#     return None

# Legacy fallback for setups that can't use the Maven bridge artifact:
# copy this file into "./src/MediaSessionCallback.java" and point buildozer at it
# with "android.add_src = ./src". New setups should add
# android-notify-music-bridge to android.gradle_dependencies instead.
#
# The package is fixed to match the pre-compiled Maven bridge, so the same class
# is loadable from either path.

JAVA_CALLBACK_FILE_CONTENT = """
// Place as-is inside: "./src/MediaSessionCallback.java"
// Point to it in buildozer.spec "android.add_src = ./src"
// Prefer the Maven artifact: android.gradle_dependencies = io.github.fector101:android-notify-music-bridge
 // A bridge: It receives MediaSession transport control events (play/pause/seek/next/prev) and forwards them to a Python listener interface.
// Android-Notify implements MediaSessionListener a Callback Listener with python.


package org.android_notify.music;"""+"""
import android.media.session.MediaSession;

public class MediaSessionCallback extends MediaSession.Callback {

    public interface MediaSessionListener {
        void onPlay();
        void onPause();
        void onSeekTo(long pos);
        void onSkipToNext();
        void onSkipToPrevious();
    }

    private MediaSessionListener listener;

    public MediaSessionCallback(MediaSessionListener listener) {
        this.listener = listener;
    }

    @Override
    public void onPlay() {
        if (listener != null) {
            listener.onPlay();
        }
    }

    @Override
    public void onPause() {
        if (listener != null) {
            listener.onPause();
        }
    }

    @Override
    public void onSeekTo(long pos) {
        if (listener != null) {
            listener.onSeekTo(pos);
        }
    }

    @Override
    public void onSkipToNext() {
        if (listener != null) {
            listener.onSkipToNext();
        }
    }

    @Override
    public void onSkipToPrevious() {
        if (listener != null) {
            listener.onSkipToPrevious();
        }
    }
}
"""
