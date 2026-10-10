"""
    SoundLoader with events
    __events__ = ('on_play', 'on_stop', 'on_pause', 'on_load', 'on_seek', 'on_complete')

This module exposes a ``SoundLoader`` that is backed by Kivy's own
``kivy.core.audio.SoundLoader`` (so users get normal Kivy behavior: volume,
pitch, loop, per-provider playback), while the returned sound object carries
the extra events above that the music notification binds to
(``on_load``/``on_seek``/``state``) and that apps use for end-of-track /
pause / seek handling (``on_complete``/``on_pause``).

The extra layer is built lazily as a subclass of whatever provider Kivy
selects for the file type (``SoundAndroidPlayer`` on Android,
``SoundSDL2`` on desktop, ...), so no raw ``MediaPlayer`` plumbing lives here.
"""

import os
from android_notify.internal.logger import logger
from android_notify.config import on_android_platform
from android_notify.internal.permissions import ask_audio_permission, has_permission_to_read_audio

try:
    from kivy.clock import Clock
    from kivy.properties import OptionProperty
    from kivy.core.audio import SoundLoader as _KivySoundLoader
    from kivy.resources import resource_find as _resource_find
except Exception as error_importing_kivy:
    logger.warning(f"Kivy not found: {error_importing_kivy}")
    Clock = None
    OptionProperty = None
    _KivySoundLoader = None
    _resource_find = None

def requestAllFilesAccess():
    """Requests 'All Files Access' permission for Android 11+"""
    if not on_android_platform():
        return None
    from kivy.clock import Clock
    from android_notify.config import get_python_activity_context
    from android_notify.internal.java_classes import Intent, Uri, Settings, autoclass
    Environment = autoclass('android.os.Environment')
    mActivity = get_python_activity_context()
    if not Environment.isExternalStorageManager():
        try:
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            print(f"package:{mActivity.getPackageName()}")
            intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}"))
            Clock.schedule_once(lambda dt: mActivity.startActivity(intent), 2)
        except Exception as error_opening_permission_screen:
            print('PermissionHandler.requestAllFilesAccess --> ', error_opening_permission_screen)
    print("requestAllFilesAccess OK")
    return None

# The full event surface exposed by every sound this module loads. Keep in
# sync with MusicNotification.setSoundLoader() (binds state/on_load/on_seek)
# and with the events an app binds for end-of-track / pause / seek handling.
EVENTS = ('on_play', 'on_stop', 'on_pause', 'on_load', 'on_seek', 'on_complete')

# base provider class -> EnhancedSound subclass
_enhanced_cache = {}


def _build_enhanced(base):
    """Create a subclass of a Kivy Sound provider that adds pause + events.

    The provider class (``base``) is whatever ``kivy.core.audio.SoundLoader``
    would have selected for the file type, so we keep all of Kivy's property
    plumbing (volume, pitch, loop, source...) while layering the notification
    events on top.
    """

    class EnhancedSound(base):
        __events__ = EVENTS

        # Kivy's stock state only allows 'stop'/'play'. The notification and
        # music screens sync to a paused state too, so widen the options.
        state = OptionProperty('stop', options=('stop', 'play', 'pause'))

        def load(self):
            super().load()
            # Kivy providers load synchronously (e.g. prepare() on Android).
            # Defer on_load to the next frame so callers that bind handlers
            # right after SoundLoader.load() still receive it, matching the
            # old async prepare behaviour. Only fire it when a sound actually
            # made it into the provider (length known), so a failed decode or
            # a missing file reports "not loaded" instead of a silent no-op.
            Clock.schedule_once(lambda dt: self._dispatch_load_when_ready(), 0)

        def _dispatch_load_when_ready(self):
            try:
                if getattr(self, "_player_ready", False) or bool(getattr(self, "length", 0)):
                    self.dispatch("on_load", "")
            except Exception as error:
                logger.warning(f"on_load check failed: {error}")


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

        def pause(self):
            """Pause playback (Kivy's Sound API has no pause()).

            On Android the MediaPlayer is paused directly and play() resumes
            at the current position. On providers without low-level pause
            (desktop SDL2) we fall back to a position-preserving stop.
            """
            player = getattr(self, '_mediaplayer', None)
            if player is not None:
                player.pause()
            else:
                self._pause_position = self.get_pos()
                self.stop()
            self.state = 'pause'
            self.dispatch('on_pause')

        def play(self):
            # Resume from the position recorded by the fallback pause().
            if self.state == 'pause' and getattr(self, '_pause_position', None) is not None:
                self.seek(self._pause_position)
                self._pause_position = None
            super().play()

        def seek(self, position, *args):
            super().seek(position, *args)
            self.dispatch('on_seek', position)

        def on_loop(self, instance, value):
            # Loop is handled manually in _completion_callback so the
            # MediaPlayer never uses setLooping() (which would swallow the
            # completion callback and break on_complete + UI sync).
            pass

        def _completion_callback(self):
            if getattr(self, 'loop', False):
                self.seek(0)
                player = getattr(self, '_mediaplayer', None)
                if player is not None:
                    player.start()
            else:
                self.state = 'stop'
                player = getattr(self, '_mediaplayer', None)
                if player is not None:
                    player.seekTo(0)
            self.dispatch('on_complete', self)

        def on_pause(self, *args):
            pass

        def on_load(self, *args):
            pass

        def on_seek(self, *args):
            pass

        def on_complete(self, *args):
            pass

    EnhancedSound.__name__ = f"Enhanced{base.__name__}"
    return EnhancedSound


def _get_enhanced_class(base):
    """Return (and cache) the enhanced subclass for a Kivy provider class."""
    enhanced = _enhanced_cache.get(base)
    if enhanced is None:
        enhanced = _build_enhanced(base)
        _enhanced_cache[base] = enhanced
    return enhanced


class SoundLoader:
    """Kivy SoundLoader with the extended event surface.

    Loads through ``kivy.core.audio.SoundLoader``'s own provider selection
    (same extension matching, no double-loading) and returns an enhanced
    subclass carrying ``__events__ = EVENTS``.
    """

    _last = None  # One-at-a-time contract, mirroring the old singleton player.

    @staticmethod
    def load(source):
        if _KivySoundLoader is None:
            raise RuntimeError("Kivy is not available; SoundLoader requires Kivy to be installed.")

        found = _resource_find(source) if _resource_find is not None else None
        filename = found if found is not None else source
        ext = filename.split('.')[-1].lower()
        if '?' in ext:
            ext = ext.split('?')[0]

        base = None
        for classobj in _KivySoundLoader._classes:
            if ext in classobj.extensions():
                base = classobj
                break
        if base is None:
            raise ValueError(f"Unable to find a Kivy audio loader for <{source}>")

        logger.info(f"audio source: {os.path.abspath(filename)}")
        sound = _get_enhanced_class(base)(source=filename)
        previous = SoundLoader._last
        if previous is not None and previous is not sound:
            previous.unload()
        SoundLoader._last = sound
        return sound


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
