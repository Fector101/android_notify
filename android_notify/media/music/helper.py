import os
from typing import Callable, Optional
from kivy.clock import Clock
from jnius import autoclass, PythonJavaClass, java_method
from android_notify.internal.java_classes import Intent
from android_notify.config import get_python_activity_context, on_android_platform


def requestAllFilesAccess():
    """Requests 'All Files Access' permission for Android 11+"""
    if not on_android_platform():
        return None
    Environment = autoclass('android.os.Environment')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
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

if on_android_platform():

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
else:
    class MediaPlayer:
        def setDataSource(self,path):
            pass
        def setOnPreparedListener(self,callback):
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

class SoundLoader:
    _instance = None
    _player = None
    _player_ready = False
    source = ''
    callback = None
    state = 'stop'
    on_play = None
    on_pause = None
    on_load: Optional[Callable[[], None]] = None
    length = property(lambda self: self._get_length(),
                      doc='Get length of the sound (in seconds).')
    loop=False


    __events__ = ('on_play', 'on_stop', 'on_pause','on_load')

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

    @classmethod
    def load(cls, source, on_load):
        instance=cls()
        instance.on_load = on_load
        instance.source = source

        print("audio source:",os.path.abspath(source))
        instance._player = MediaPlayer()
        instance._player.setDataSource(source)
        instance._player.setOnPreparedListener(PlayerReadyListener(instance.on_player_ready))
        instance._player.prepareAsync()
        return instance._instance

    def on_player_ready(self):
        """Called by PlayerReadyListener when MediaPlayer is ready."""
        self._player_ready = True
        if self.on_load:
            self.on_load()

    def get_pos(self):
        """Get current playback position in seconds."""
        if not self._player or not self._player_ready:
            print("Warning player is not ready...")
            return 0.0

        raw = self._player.getCurrentPosition() / 1000.0
        pos = raw

        duration = self._player.getDuration() / 1000.0
        if pos < 0:
            pos = 0
        elif 0 < duration < pos:
            pos = duration

        if pos == duration and self.loop: # under the assumption get_pos will be call every sec
            self.seek(0)
            pos=0
        print(f"read_pos: raw_pos={raw:.3f} duration={duration:.3f} returning={pos}")
        return pos

    def play(self):
        """Resume playback."""
        if not self._player or not self._player_ready:
            print("Warning player is not ready...")
            return None
        self._player.start()
        self.state = 'play'
        print("EVENT: PLAY")
        self.__dispatch(self.on_play)
        return None

    def pause(self):
        """Pause playback."""
        if not self._player or not self._player_ready:
            print("Warning player is not ready...")
            return None
        self._player.pause()
        self.state = 'pause'
        print("EVENT: PAUSE")
        self.__dispatch(self.on_pause)
        return None

    def stop(self):
        if not self._player:
            return
        self._player.stop()

    def _get_length(self):
        if not self._player or not self._player_ready:
            print("Warning player is not ready...")
            return None

        return self._player.getDuration() / 1000.0

    def seek(self, position):
        """Seek to a position (sec = seconds from start)."""
        if not self._player or not self._player_ready:
            print("Warning player is not ready...")
            return None
        self._player.seekTo(int(position * 1000))
        print(f"EVENT: SEEK {position:.1f}s")
        return None

    def unload(self):
        """Unload the file from memory."""
        if self._player:
            self._player.release()
        else:
            print("Warning player not loaded.")

    @staticmethod
    def __dispatch(__function):
        if __function:
            try:
                __function()
            except Exception as error_dispatching_listener:
                print(f"Error: {error_dispatching_listener}")
      
