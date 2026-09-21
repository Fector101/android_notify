"""
Complete music player app: scan device for audio files, play with notification controls.
=========================================================================================

Features:
- Scans device storage for audio files (.mp3, .m4a, .ogg, .wav, .flac, .aac)
- List view of all found tracks, tap to play
- Prev / Next / Play / Pause with notification, lock screen & bluetooth controls
- Draggable seek bar synced with playback
- Loop / Shuffle toggles
- Auto-advance to next track on completion
- Reads embedded album art for the notification
- Requests All Files Access on Android 11+
- Self-contained — paste into your Kivy project
"""

import os
import random
import threading

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.slider import Slider
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.utils import platform
from kivy.lang import Builder

import logging

from android_notify.media.music import MusicNotification
from android_notify.media.music.helper import SoundLoader, requestAllFilesAccess
from android_notify import logger as android_notify_logger

android_notify_logger.setLevel(logging.INFO)
logger = logging.getLogger("MusicApp")


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
AUDIO_EXTENSIONS = (".mp3", ".m4a", ".ogg", ".wav", ".flac", ".aac",)# ".opus")

# Where to scan. On Android we try the most common public music dirs first,
# then fall back to a broader scan. Add or remove roots to fit your needs.
ANDROID_SCAN_ROOTS = [
    "/storage/emulated/0/Music",
    "/storage/emulated/0/Download",
    "/storage/emulated/0/Downloads",
    "/storage/emulated/0/Android/media",
    "/sdcard/Music",
    "/sdcard/Download",
]

# If nothing is found in the roots above, do a full scan of this root.
# Set to None to disable the fallback (faster, but may miss files).
ANDROID_FALLBACK_ROOT = "/storage/emulated/0"


def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def scan_audio_files():
    """Return a list of absolute paths to audio files found on the device.

    Scans a set of well-known folders first; if nothing is found and a
    fallback root is configured, does a broader walk. Silently skips
    directories it can't read.
    """
    found = []
    seen = set()

    def add(path):
        if path in seen:
            return
        seen.add(path)
        found.append(path)

    def walk(root):
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
            # Skip common non-music directories to speed things up.
            dirnames[:] = [
                d for d in dirnames
                if d not in (".thumbnails", "cache", "Cache", "Android/data", "obb")
            ]
            for name in filenames:
                if name.lower().endswith(AUDIO_EXTENSIONS):
                    add(os.path.join(dirpath, name))

    roots = ANDROID_SCAN_ROOTS if platform == "android" else [
        os.path.expanduser("~/Music"),
        os.path.expanduser("~/Downloads"),
    ]

    for root in roots:
        if os.path.isdir(root):
            walk(root)

    if not found and ANDROID_FALLBACK_ROOT and os.path.isdir(ANDROID_FALLBACK_ROOT):
        logger.info("No audio in common folders, scanning %s ...", ANDROID_FALLBACK_ROOT)
        walk(ANDROID_FALLBACK_ROOT)

    found.sort(key=lambda p: os.path.basename(p).lower())
    logger.info("Scan complete: %d tracks", len(found))
    return found


# --------------------------------------------------------------------------- #
# RecycleView row for a single track
# --------------------------------------------------------------------------- #
class TrackRow(RecycleDataViewBehavior, BoxLayout):
    """One row in the track list. Tapping it sends `on_release` up to the
    RecycleView, which forwards `selected_path` to the app."""
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
    height: dp(56)
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
        default_size: None, dp(56)
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

    def set_tracks(self, paths, current_path=None):
        self.data = [
            {
                "filename": os.path.basename(p),
                "path": p,
                "is_current": p == current_path,
            }
            for p in paths
        ]

    def mark_current(self, current_path):
        for item in self.data:
            item["is_current"] = (item["path"] == current_path)
        self.refresh_from_data()


# --------------------------------------------------------------------------- #
# Root UI
# --------------------------------------------------------------------------- #
class MusicPlayerRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)

        # --- state ---------------------------------------------------------
        self.tracks = []             # list[str] absolute paths
        self.current_index = -1      # index into self.tracks
        self.sound = None
        self.notification = None
        self._tick = None
        self._seeking = False
        self._pending_seek = None
        self.loop_track = False      # repeat one
        self.shuffle = False
        self._scan_in_progress = False

        # --- top bar: scan + shuffle + loop --------------------------------
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        self.scan_btn = Button(text="Scan device")
        self.scan_btn.bind(on_release=lambda *_: self.scan_device())
        top.add_widget(self.scan_btn)

        self.shuffle_btn = Button(text="Shuffle: OFF")
        self.shuffle_btn.bind(on_release=lambda *_: self.toggle_shuffle())
        top.add_widget(self.shuffle_btn)

        self.loop_btn = Button(text="Loop: OFF")
        self.loop_btn.bind(on_release=lambda *_: self.toggle_loop())
        top.add_widget(self.loop_btn)

        self.add_widget(top)

        # --- now playing label ---------------------------------------------
        self.now_playing = Label(
            text="Nothing playing",
            size_hint_y=None,
            height=dp(40),
            shorten=True,
            shorten_from="right",
        )
        self.add_widget(self.now_playing)

        # --- track list ----------------------------------------------------
        self.track_list = TrackList(on_track_selected=self.play_track_by_path)
        self.add_widget(self.track_list)

        # --- seek bar ------------------------------------------------------
        self.seek_bar = Slider(min=0, max=1, value=0)
        self.seek_bar.bind(on_touch_down=self._on_seek_touch_down)
        self.seek_bar.bind(on_touch_up=self._on_seek_touch_up)
        self.seek_bar.bind(on_value=lambda *_: self._on_seek_value_changed())
        self.add_widget(self.seek_bar)

        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=dp(28))
        self.add_widget(self.time_label)

        # --- transport controls --------------------------------------------
        controls = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6))

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

        self.status_label = Label(text="Tap 'Scan device' to find music", size_hint_y=None, height=dp(24))
        self.add_widget(self.status_label)

    # ------------------------------------------------------------------ #
    # Scanning                                                             #
    # ------------------------------------------------------------------ #
    def scan_device(self):
        if self._scan_in_progress:
            return
        self._scan_in_progress = True
        self.scan_btn.disabled = True
        self.status_label.text = "Scanning..."

        def worker():
            try:
                tracks = scan_audio_files()
            except Exception:
                logger.exception("scan failed")
                tracks = []
            self._on_scan_done(tracks)

        threading.Thread(target=worker, daemon=True).start()

    @mainthread
    def _on_scan_done(self, tracks):
        self._scan_in_progress = False
        self.scan_btn.disabled = False
        self.tracks = tracks
        self.track_list.set_tracks(tracks)
        if tracks:
            self.status_label.text = f"Found {len(tracks)} track(s)"
        else:
            self.status_label.text = "No audio files found - check storage permission"

    # ------------------------------------------------------------------ #
    # Playback control                                                     #
    # ------------------------------------------------------------------ #
    def play_track_by_path(self, path):
        try:
            self.current_index = self.tracks.index(path)
        except ValueError:
            # File not in our list (shouldn't happen), just load it directly.
            self.tracks.append(path)
            self.current_index = len(self.tracks) - 1
        self.load_current()

    def load_current(self):
        if not (0 <= self.current_index < len(self.tracks)):
            return
        path = self.tracks[self.current_index]

        # Release previous player/notification first (SoundLoader is a singleton).
        self._release_player()

        requestAllFilesAccess()

        notification = MusicNotification(
            on_next=self.next_track,
            on_previous=self.previous_track,
        )
        notification.setTitle(os.path.splitext(os.path.basename(path))[0])
        notification.setArtist("Unknown Artist")

        sound = SoundLoader.load(path)
        sound.loop = self.loop_track
        sound.bind(on_load=self._on_loaded)
        sound.bind(on_complete=self._on_track_finished)
        sound.bind(state=self._on_state_changed)
        self.sound = sound

        notification.setSoundLoader(sound)
        notification.set_skip_available(self._has_next(), self._has_prev())
        self.notification = notification

        # Reset seek bar
        self.seek_bar.max = 1
        self.seek_bar.value = 0
        self._pending_seek = None
        self._seeking = False
        self.time_label.text = "00:00 / 00:00"

        self.now_playing.text = f"Loading: {os.path.basename(path)}"
        self.status_label.text = f"Track {self.current_index + 1} / {len(self.tracks)}"
        self.track_list.mark_current(path)

    def _release_player(self):
        self._stop_ticker()
        if self.sound is not None:
            try:
                self.sound.stop()
                self.sound.unload()
            except Exception:
                logger.exception("error releasing sound")
            self.sound = None
        if self.notification is not None:
            try:
                self.notification.release()
            except Exception:
                logger.exception("error releasing notification")
            self.notification = None

    @mainthread
    def _on_loaded(self, *_):
        duration = self.sound.length or 0
        self.seek_bar.max = max(duration, 1)
        self.seek_bar.value = 0
        self._pending_seek = None

        self.sound.play()

        # Use embedded title/artist if available so notification is nicer.
        self._apply_metadata_from_file()

        self.now_playing.text = os.path.basename(self.sound.source)

    def _apply_metadata_from_file(self):
        """Read ID3 tags for title/artist if the tags library is available."""
        try:
            from mutagen import File as MutagenFile  # optional dependency
        except Exception:
            return
        try:
            tags = MutagenFile(self.sound.source, easy=True)
            if not tags:
                return
            title = (tags.get("title") or [None])[0]
            artist = (tags.get("artist") or [None])[0]
            if title:
                self.notification.setTitle(title)
            if artist:
                self.notification.setArtist(artist)
        except Exception:
            logger.exception("failed reading tags")

    def toggle_play_pause(self):
        if self.sound is None:
            # Nothing loaded yet - play the first track if we have any.
            if self.tracks and self.current_index < 0:
                self.current_index = 0
                self.load_current()
            return
        if self.sound.state == "play":
            self.sound.pause()
        else:
            self.sound.play()

    @mainthread
    def _on_state_changed(self, instance, state):
        is_playing = state == "play"
        self.play_btn.text = "Pause" if is_playing else "Play"
        self.play_btn.disabled = self.sound is None
        if is_playing:
            self._start_ticker()
        else:
            self._stop_ticker()
        self._update_time()

    def _start_ticker(self):
        if self._tick is None:
            self._tick = Clock.schedule_interval(lambda dt: self._update_time(), 0.25)

    def _stop_ticker(self):
        if self._tick is not None:
            self._tick.cancel()
            self._tick = None

    def _update_time(self):
        if self.sound is None:
            return
        pos = self.sound.get_pos()
        length = self.sound.length or 0

        if self._pending_seek is not None:
            if abs(pos - self._pending_seek) < 0.75:
                self._pending_seek = None
            else:
                self.seek_bar.value = self._pending_seek
                self.time_label.text = f"{_fmt(self._pending_seek)} / {_fmt(length)}"
                return

        if not self._seeking:
            self.seek_bar.value = min(pos, self.seek_bar.max)
        self.time_label.text = f"{_fmt(pos)} / {_fmt(length)}"

    # ------------------------------------------------------------------ #
    # Seek bar                                                             #
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
        if self.sound is None:
            return
        if self._seeking:
            length = self.sound.length or 0
            self.time_label.text = f"{_fmt(self.seek_bar.value)} / {_fmt(length)}"

    def _perform_seek(self, position_seconds):
        if self.sound is None:
            return
        target = float(max(0.0, position_seconds))
        self._pending_seek = target
        self.seek_bar.value = target
        length = self.sound.length or 0
        self.time_label.text = f"{_fmt(target)} / {_fmt(length)}"
        try:
            self.sound.seek(target)   # SoundLoader.seek takes seconds
        except Exception:
            logger.exception("seek failed")
            self._pending_seek = None

    # ------------------------------------------------------------------ #
    # Track changes                                                        #
    # ------------------------------------------------------------------ #
    def _has_next(self):
        if self.shuffle:
            return len(self.tracks) > 1
        return self.current_index + 1 < len(self.tracks) or self.loop_track

    def _has_prev(self):
        if self.shuffle:
            return len(self.tracks) > 1
        return self.current_index > 0

    def next_track(self):
        if not self.tracks:
            return
        if self.shuffle and len(self.tracks) > 1:
            choices = [i for i in range(len(self.tracks)) if i != self.current_index]
            self.current_index = random.choice(choices)
        else:
            if self.current_index + 1 < len(self.tracks):
                self.current_index += 1
            elif self.loop_track:
                # loop one is handled by the player, but keep index consistent
                pass
            else:
                # End of list - stop at the last track
                return
        self.load_current()

    def previous_track(self):
        if not self.tracks:
            return
        # If we're >3s into the current track, restart it instead.
        if self.sound is not None and self.sound.get_pos() > 3:
            self._perform_seek(0)
            return
        if self.shuffle and len(self.tracks) > 1:
            choices = [i for i in range(len(self.tracks)) if i != self.current_index]
            self.current_index = random.choice(choices)
        elif self.current_index > 0:
            self.current_index -= 1
        else:
            return
        self.load_current()

    def _on_track_finished(self, *_):
        """Called by SoundLoader on track completion.

        SoundLoader auto-restarts when loop=True; otherwise we advance.
        """
        if self.loop_track:
            # SoundLoader handles the restart; reset UI.
            self._reset_seek_ui()
            return
        # Auto-advance
        if self.shuffle and len(self.tracks) > 1:
            self.next_track()
        elif self.current_index + 1 < len(self.tracks):
            self.next_track()
        else:
            # Last track, stop
            if self.sound is not None:
                self.sound.seek(0)
                self.sound.state = "pause"
            self._reset_seek_ui()

    def _reset_seek_ui(self):
        self._pending_seek = None
        self.seek_bar.value = 0
        length = (self.sound.length if self.sound else 0) or 0
        self.time_label.text = f"00:00 / {_fmt(length)}"

    # ------------------------------------------------------------------ #
    # Toggles                                                              #
    # ------------------------------------------------------------------ #
    def toggle_loop(self):
        self.loop_track = not self.loop_track
        if self.sound is not None:
            self.sound.loop = self.loop_track
        self.loop_btn.text = f"Loop: {'ON' if self.loop_track else 'OFF'}"
        if self.notification is not None:
            self.notification.set_skip_available(self._has_next(), self._has_prev())

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.shuffle_btn.text = f"Shuffle: {'ON' if self.shuffle else 'OFF'}"
        if self.notification is not None:
            self.notification.set_skip_available(self._has_next(), self._has_prev())

    # ------------------------------------------------------------------ #
    # Lifecycle                                                            #
    # ------------------------------------------------------------------ #
    def cleanup(self):
        self._release_player()


class MusicPlayerApp(App):
    def build(self):
        self.title = "Music Player"
        return MusicPlayerRoot()

    def on_stop(self):
        if self.root is not None:
            self.root.cleanup()


if __name__ == "__main__":
    MusicPlayerApp().run()
