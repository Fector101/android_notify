"""
Plain-controller music player, full-size: scan, list, seek, loop, advance
==========================================================================

Like ``example_2.py`` in scope (track list, draggable seek bar, loop toggle,
auto-advance at track end, notification transport controls), but it drives the
notification through a controller that dispatches **no** events.

The player is Kivy's own ``kivy.core.audio.SoundLoader`` wrapped in a plain
object (``KivySoundController``). Because it has no ``bind`` / ``events``,
``MediaNotification`` cannot subscribe to playback state and must instead be
fed by hand: **every time the app changes playback it calls
``notification.syncPlaybackState()``**. That single call is the manual half of
the feature; the notification's own play / pause / seek buttons still come back
into the controller and are synced for you.

Consequences of using Kivy's ``SoundLoader``:

- It plays *file paths* only, so tracks are resolved from MediaStore ``_data``
  instead of ``content://`` URIs. ``_data`` is filtered on Android 10+ unless
  the app holds All Files Access, so this scan is really aimed at older Android
  or testing - see ``example_2.py`` for the scoped-storage way.
- There is no ``on_complete`` event, so auto-advance is guessed from position
  in the app-side UI ticker (``get_pos()`` at the track length, or a rewind
  while playing). That is app-side refresh only - the notification is never
  polled.

Features:
- Scans MediaStore for audio file paths (``_data``), list view, tap to play.
- Prev / Next / Play / Pause, with notification, lock screen & headset controls.
- Draggable seek bar synced with playback (app seeks call syncPlaybackState).
- Loop toggle that repeats the current track.
- Auto-advance to the next track on completion (ticker-detected).
- In-app level-colored log panel fed by ``install_kivy_log_handler()``.
- Self-contained - paste into your Kivy project.
"""

import os
import threading
import logging

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.slider import Slider
try:
    from kivy.core.audio_output import SoundLoader as KivySoundLoader
except ModuleNotFoundError:
    from kivy.core.audio import SoundLoader as KivySoundLoader

from android_notify.widgets.log_view import LogPanel, install_kivy_log_handler

_LOG_HANDLER = install_kivy_log_handler()

from android_notify import logger as android_notify_logger
from android_notify.config import on_android_platform, get_python_activity_context
from android_notify.media import MediaNotification
from android_notify.media.music.helper import MediaPermissionHandler
from android_notify.internal.permissions import is_music_permission_in_manifest

android_notify_logger.setLevel(logging.DEBUG)
logger = logging.getLogger("PlainControllerExample2")


if on_android_platform():
    from jnius import autoclass
else:
    autoclass = None


def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _basename(path):
    """Best-effort human name for a file path."""
    name = path.rstrip("/")
    return os.path.basename(name) or name


def scan_audio_file_paths():
    """MediaStore -> list of audio file paths (the ``_data`` column).

    Kivy's SoundLoader plays paths, not ``content://`` URIs. ``_data`` is
    filtered on Android 10+ unless the app holds All Files Access, so this is
    primarily for Android 9 and below / testing.
    """
    if not on_android_platform():
        return []

    context = get_python_activity_context()
    if not context:
        logger.error("scan_audio_file_paths: no activity context")
        return []

    resolver = context.getContentResolver()
    uri = autoclass("android.provider.MediaStore$Audio$Media").EXTERNAL_CONTENT_URI
    projection = ["_id", "title", "artist", "duration", "_data"]
    cursor = resolver.query(uri, projection, None, None, None)
    tracks = []

    if cursor:
        title_idx = cursor.getColumnIndex("title")
        artist_idx = cursor.getColumnIndex("artist")
        duration_idx = cursor.getColumnIndex("duration")
        data_idx = cursor.getColumnIndex("_data")
        while cursor.moveToNext():
            path = cursor.getString(data_idx)
            if not path:
                continue
            tracks.append(
                {
                    "path": path,
                    "title": cursor.getString(title_idx) or "(unknown title)",
                    "artist": cursor.getString(artist_idx) or "",
                    "duration": cursor.getLong(duration_idx),
                }
            )
        cursor.close()
    tracks.sort(key=lambda track: track["title"].lower())
    logger.info("Scan complete: %d loadable file path(s)", len(tracks))
    return tracks


class TrackRow(RecycleDataViewBehavior, BoxLayout):
    """One row in the track list. Tapping it sends `on_release` up to the
    RecycleView, which forwards the selected path to the app."""
    index = NumericProperty(0)
    filename = StringProperty("")
    path = StringProperty("")
    is_current = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.filename = data.get("filename", "")
        self.path = data.get("path", "")
        self.is_current = data.get("is_current", False)
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            rv = self.parent
            while rv is not None and not isinstance(rv, RecycleView):
                rv = rv.parent
            if rv is not None:
                rv.select_track(self.path)
            return True
        return super().on_touch_down(touch)


Builder.load_string("""
<TrackRow>:
    size_hint_y: None
    height: dp(48)
    padding: dp(8), 0
    canvas.before:
        Color:
            rgba: (0.20, 0.45, 0.75, 1) if root.is_current else (0.12, 0.12, 0.12, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.filename
        color: (1, 1, 1, 1)
        size_hint_x: 1
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        shorten: True
        shorten_from: 'right'

<TrackList>:
    viewclass: 'TrackRow'
    RecycleBoxLayout:
        default_size: None, dp(48)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(1)
""")


class TrackList(RecycleView):
    def __init__(self, on_track_selected, **kwargs):
        super().__init__(**kwargs)
        self.on_track_selected = on_track_selected

    def select_track(self, path):
        self.on_track_selected(path)

    def set_tracks(self, tracks, current_path=None):
        self.data = [
            {
                "filename": track.get("title") or _basename(track.get("path", "")),
                "path": track["path"],
                "is_current": track["path"] == current_path,
            }
            for track in tracks
        ]

    def mark_current(self, current_path):
        for item in self.data:
            item["is_current"] = (item["path"] == current_path)
        self.refresh_from_data()


class KivySoundController:
    """Minimal ``IMediaController`` adapter around a Kivy ``Sound`` (no events).

    A plain object on purpose: it has no ``bind`` / ``dispatch`` / ``events``,
    so ``MediaNotification`` treats it as a controller that cannot drive the
    notification through events - the app must call ``syncPlaybackState()``.

    One instance is reused for every track via :meth:`load`, so the
    ``MediaNotification`` built around it stays valid across track changes.
    """

    def __init__(self):
        self._sound = None
        self._length = 0.0
        self._pos = 0.0
        self._playing = False
        self._paused = False
        self._loop = False

    def load(self, path):
        """Drop the current sound and load a new one. Returns True on success."""
        self.stop_playback()
        self._sound = KivySoundLoader.load(path)
        self._length = float(self._sound.length or 0) if self._sound else 0.0
        self._pos = 0.0
        if self._sound is not None:
            self._sound.loop = self._loop
        return self._sound is not None

    def stop_playback(self):
        if self._sound is not None:
            try:
                self._sound.stop()
                self._sound.unload()
            except Exception as error:
                logger.warning("sound cleanup error: %s", error)
            self._sound = None
        self._pos = 0.0
        self._playing = False
        self._paused = False

    # --- IMediaController contract -----------------------------------------
    @property
    def source(self):
        return self._sound.source if self._sound else None

    @property
    def length(self):
        return self._length

    @property
    def state(self):
        if self._paused:
            return "pause"
        return "play" if self._playing else "stop"

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = bool(value)
        if self._sound is not None:
            self._sound.loop = self._loop

    def play(self):
        if self._sound is None:
            return
        self._sound.play()
        if self._paused:
            # Kivy's Sound cannot resume in place, so seek back after starting.
            self._sound.seek(self._pos)
        self._paused = False
        self._playing = True

    def pause(self):
        if self._sound is None:
            return
        self._pos = self.get_pos()
        self._sound.stop()  # Kivy Sound has no pause(); stop and remember.
        self._paused = True
        self._playing = False

    def seek(self, seconds):
        if self._sound is None:
            return
        self._pos = float(max(0.0, seconds))
        self._sound.seek(self._pos)

    def get_pos(self):
        if self._sound is None:
            return 0.0
        if self._paused:
            return self._pos
        pos = self._sound.get_pos()
        if pos is not None:
            self._pos = float(pos)
        return self._pos

    def get_length(self):
        """Length may only be known after the sound is loaded (no on_load event)."""
        if self._sound is not None and self._sound.length:
            self._length = float(self._sound.length)
        return self._length


class PlainPlayerRoot(BoxLayout):
    """Full plain-controller player: scan list, tap-to-play, seek, loop,
    auto-advance, all synced to the notification with syncPlaybackState()."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(10), dp(50)], spacing=dp(8), **kwargs)

        self.controller = None
        self.notification = None
        self.tracks = []          # list[dict] from scan_audio_file_paths
        self.current_index = -1
        self.loop_track = False   # repeat current track
        self._tick = None
        self._seeking = False
        self._pending_seek = None
        self._last_pos = 0.0
        self._scan_in_progress = False

        # --- top bar: scan + loop --------------------------------
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.scan_btn = Button(text="Scan device")
        self.scan_btn.bind(on_release=lambda *_: self.scan_device())
        top.add_widget(self.scan_btn)
        self.loop_btn = Button(text="Loop: OFF")
        self.loop_btn.bind(on_release=lambda *_: self.toggle_loop())
        top.add_widget(self.loop_btn)
        self.add_widget(top)

        # --- now playing label -----------------------------------------
        self.now_playing = Label(
            text="Nothing playing",
            size_hint_y=None,
            height=dp(40),
            shorten=True,
            shorten_from="right",
        )
        self.add_widget(self.now_playing)

        # --- track list ------------------------------------------------
        self.track_list = TrackList(on_track_selected=self.play_track_by_path)
        self.add_widget(self.track_list)

        # --- seek bar --------------------------------------------------
        self.seek_bar = Slider(min=0, max=1, value=0, size_hint_y=None, height=dp(44))
        self.seek_bar.bind(
            on_touch_down=self._on_seek_touch_down,
            on_touch_up=self._on_seek_touch_up,
            on_value=lambda *_: self._on_seek_value_changed()
        )
        self.add_widget(self.seek_bar)

        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=dp(24))
        self.add_widget(self.time_label)

        # --- transport controls -----------------------------------------
        controls = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        self.prev_btn = Button(text="Prev")
        self.prev_btn.bind(on_release=lambda *_: self.previous_track())
        controls.add_widget(self.prev_btn)
        self.play_btn = Button(text="Play")
        self.play_btn.bind(on_release=lambda *_: self.toggle_play_pause())
        self.play_btn.disabled = True
        controls.add_widget(self.play_btn)
        self.next_btn = Button(text="Next")
        self.next_btn.bind(on_release=lambda *_: self.next_track())
        controls.add_widget(self.next_btn)
        self.add_widget(controls)

        self.status_label = Label(text="Starting...", size_hint_y=None, height=dp(24))
        self.add_widget(self.status_label)

        # In-app log panel at the bottom (captures android_notify logs too).
        self.log_panel = LogPanel(handler=_LOG_HANDLER, size_hint_y=1)
        self.add_widget(self.log_panel)

        # UI refresh + completion detection. There is no on_complete event, so
        # the ticker watches get_pos(); the notification is never polled - app
        # changes call syncPlaybackState() instead.
        self._tick = Clock.schedule_interval(self._on_tick, 0.25)

        Clock.schedule_once(self._start, 2)

    # ------------------------------------------------------------------ #
    # Startup / permission / scan                                         #
    # ------------------------------------------------------------------ #
    @mainthread
    def _start(self, _dt):
        logger.info("starting: request audio permission")
        self.scan_device()

    def scan_device(self):
        if self._scan_in_progress:
            return
        if not on_android_platform():
            self.status_label.text = "Scanning needs Android (device example)"
            return
        if not is_music_permission_in_manifest():
            self.status_label.text = "Audio permission missing from buildozer.spec (android.permissions = READ_MEDIA_AUDIO, READ_EXTERNAL_STORAGE)"
            return

        if MediaPermissionHandler.has_permission_to_access_audio_files():
            self._scan()
            return

        self.status_label.text = "Requesting audio access..."
        MediaPermissionHandler.ask_permission_to_access_audio_files(callback=self._on_permission)

    @mainthread
    def _on_permission(self, granted):
        if not granted:
            self.status_label.text = "Audio access denied"
            return
        self._scan()

    def _scan(self):
        self._scan_in_progress = True
        self.scan_btn.disabled = True
        self.status_label.text = "Scanning..."

        def worker():
            try:
                tracks = scan_audio_file_paths()
            except Exception as error:
                logger.exception("scan failed: %s", error)
                tracks = []
            Clock.schedule_once(lambda *_: self._on_scan_done(tracks))

        threading.Thread(target=worker, daemon=True).start()

    @mainthread
    def _on_scan_done(self, tracks):
        self._scan_in_progress = False
        self.scan_btn.disabled = False
        self.tracks = tracks
        self.current_index = -1
        self.track_list.set_tracks(tracks)
        if not tracks:
            self.status_label.text = (
                "No loadable file paths - '_data' is hidden on Android 10+ "
                "without All Files Access, or no audio found"
            )
            return
        self.status_label.text = f"Found {len(tracks)} track(s)"

    # ------------------------------------------------------------------ #
    # Loading / playback                                                  #
    # ------------------------------------------------------------------ #
    def play_track_by_path(self, path):
        for index, track in enumerate(self.tracks):
            if track["path"] == path:
                self.current_index = index
                break
        else:
            return
        self.load_current()

    def load_current(self):
        if not (0 <= self.current_index < len(self.tracks)):
            return
        track = self.tracks[self.current_index]
        title = track.get("title") or _basename(track["path"])
        artist = track.get("artist") or "Unknown Artist"

        if self.controller is None:
            self.controller = KivySoundController()
        if not self.controller.load(track["path"]):
            logger.error("Failed to load track: %s", track["path"])
            self.now_playing.text = f"Failed to load: {title}"
            self.status_label.text = "Could not load track (unreadable or permission denied)"
            return
        self.controller.loop = self.loop_track

        # Build the notification once; the controller instance is reused, so the
        # session stays the same across track changes and only titles move.
        if self.notification is None:
            self.notification = MediaNotification(
                mediaController=self.controller,
                on_next=self.next_track,
                on_previous=self.previous_track,
            )
        self.notification.setNowPlaying(title, artist)

        self._pending_seek = None
        self._last_pos = 0.0
        self.seek_bar.max = 1
        self.seek_bar.value = 0
        self.time_label.text = "00:00 / 00:00"
        self.now_playing.text = f"Loading: {title}"
        self.status_label.text = f"Track {self.current_index + 1} / {len(self.tracks)}"
        self.track_list.mark_current(track["path"])

        logger.info("now playing: %s (%s)", title, track["path"])
        self.controller.play()
        self.play_btn.text = "Pause"
        self.play_btn.disabled = False
        # App-driven change -> tell the notification (no events to react to).
        self.notification.syncPlaybackState()

    def toggle_play_pause(self):
        if self.controller is None:
            # Nothing loaded yet - play the first track if we have any.
            if self.tracks and self.current_index < 0:
                self.current_index = 0
                self.load_current()
            return
        if self.controller.source is None:
            return
        if self.controller.state == "play":
            self.controller.pause()
            self.play_btn.text = "Play"
            logger.info("pause")
        else:
            self.controller.play()
            self.play_btn.text = "Pause"
            logger.info("play")
        self._last_pos = self.controller.get_pos()
        self.notification.syncPlaybackState()

    def next_track(self):
        if not self.tracks:
            return
        if self.current_index + 1 < len(self.tracks):
            self.current_index += 1
            self.load_current()
        # else: end of list; loop one repeats the player's track itself.

    def previous_track(self):
        if not self.tracks:
            return
        # If we're >3s into the current track, restart it instead.
        if self.controller is not None and self.controller.get_pos() > 3:
            self._perform_seek(0)
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current()

    def toggle_loop(self):
        self.loop_track = not self.loop_track
        if self.controller is not None:
            self.controller.loop = self.loop_track
        self.loop_btn.text = f"Loop: {'ON' if self.loop_track else 'OFF'}"
        logger.info("loop -> %s", self.loop_track)

    # ------------------------------------------------------------------ #
    # Ticker: UI progress + completion detection (no on_complete event)   #
    # ------------------------------------------------------------------ #
    def _on_tick(self, _dt):
        if self.controller is None:
            return
        length = self.controller.get_length()
        if length > 0:
            self.seek_bar.max = length

        pos = self.controller.get_pos()
        dropped = self._last_pos - pos
        self._last_pos = pos

        if self._pending_seek is not None:
            if abs(pos - self._pending_seek) < 0.75:
                self._pending_seek = None
            else:
                self.time_label.text = f"{_fmt(self._pending_seek)} / {_fmt(length)}"
                return

        if not self._seeking:
            self.seek_bar.value = min(pos, self.seek_bar.max)
        self.time_label.text = f"{_fmt(pos)} / {_fmt(length)}"

        if self.controller.state != "play":
            return
        # Guess completion from position: sitting at the end, or a rewind while
        # playing (an endless loop restarting / backend reset).
        at_end = length > 1 and pos >= length - 0.15
        rewound = dropped > 1.0
        if at_end or rewound:
            self._track_finished()

    def _track_finished(self):
        """Reached track end. Loop repeats; otherwise advance or stop."""
        if self.loop_track:
            # The sound loops itself; snap the UI back and resync.
            self.controller.seek(0)
            self._reset_seek_ui()
            self.notification.syncPlaybackState()
            return
        if self.current_index + 1 < len(self.tracks):
            self.next_track()
            return
        # "Play once": stop at the beginning of the last track.
        self.controller.seek(0)
        self.controller.pause()
        self.play_btn.text = "Play"
        self._reset_seek_ui()
        self.notification.syncPlaybackState()

    def _reset_seek_ui(self):
        self._pending_seek = None
        self._last_pos = 0.0  # don't let the "rewound" check refire after seek(0)
        self.seek_bar.value = 0
        length = self.controller.get_length() if self.controller else 0
        self.time_label.text = f"00:00 / {_fmt(length)}"

    # ------------------------------------------------------------------ #
    # Seek bar                                                            #
    # ------------------------------------------------------------------ #
    def _on_seek_touch_down(self, slider, touch):
        if slider.collide_point(*touch.pos):
            self._seeking = True
        return False

    def _on_seek_touch_up(self, slider, touch):
        if self._seeking:
            self._seeking = False
            self._perform_seek(slider.value)
        return False

    def _on_seek_value_changed(self):
        if self.controller is None or not self._seeking:
            return
        length = self.controller.get_length()
        self.time_label.text = f"{_fmt(self.seek_bar.value)} / {_fmt(length)}"

    def _perform_seek(self, seconds):
        if self.controller is None or self.controller.source is None:
            return
        target = float(max(0.0, seconds))
        self._pending_seek = target
        self._last_pos = target
        self.controller.seek(target)
        logger.info("seek %.1fs", target)
        self.notification.syncPlaybackState()  # app-driven seek

    # ------------------------------------------------------------------ #
    # Lifecycle                                                           #
    # ------------------------------------------------------------------ #
    def cleanup(self):
        if self._tick is not None:
            self._tick.cancel()
            self._tick = None
        if self.controller is not None:
            self.controller.stop_playback()
        if self.notification is not None:
            try:
                self.notification.release()
            except Exception as error:
                logger.exception("error releasing notification: %s", error)
            self.notification = None
        for name in ("", "android_notify"):
            logging.getLogger(name).removeHandler(_LOG_HANDLER)


class PlainPlayerApp(App):
    def build(self):
        self.title = "Plain Controller Example 2"
        self.root = PlainPlayerRoot()
        return self.root

    def on_stop(self):
        if self.root is not None:
            self.root.cleanup()


if __name__ == "__main__":
    PlainPlayerApp().run()