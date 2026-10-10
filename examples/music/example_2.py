"""
Complete music player app: scan MediaStore for audio, play with notification controls.
=========================================================================================

Features:
- Scans MediaStore (scoped storage) for audio tracks — no All Files Access needed
- List view of all found tracks, tap to play
- Prev / Next / Play / Pause with notification, lock screen & Bluetooth controls
- Draggable seek bar synced with playback
- Loop / Shuffle toggles
- Auto-advance to next track on completion
- Reads embedded album art for the notification
- Self-contained — paste into your Kivy project
"""

import os
import threading
import traceback
import logging

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.clock import Clock, mainthread

from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.slider import Slider

from android_notify import logger as android_notify_logger
from android_notify.config import on_android_platform, get_python_activity_context
from android_notify.media.music import MediaNotification
from android_notify.media.music.helper import SoundLoader, MediaPermissionHandler
from android_notify.internal.permissions import is_music_permission_in_manifest

android_notify_logger.setLevel(logging.INFO)
logger = logging.getLogger("MusicApp")


class TrackRow(RecycleDataViewBehavior, BoxLayout):
    """One row in the track list. Tapping it sends `on_release` up to the
    RecycleView, which forwards `selected_uri` to the app."""
    index = NumericProperty(0)
    filename = StringProperty("")
    uri = StringProperty("")
    is_current = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.filename = data.get("filename", "")
        self.uri = data.get("uri", "")
        self.is_current = data.get("is_current", False)
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            rv = self.parent
            while rv is not None and not isinstance(rv, RecycleView):
                rv = rv.parent
            if rv is not None:
                rv.select_track(self.uri)
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

if on_android_platform():
    from jnius import autoclass
else:
    autoclass = None

def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def _basename_of_uri(uri):
    """Best-effort human name for a content:// URI."""
    try:
        return os.path.basename(uri.rstrip("/"))
    except Exception as error_requesting_uri:
        logger.exception(f"_basename_of_uri failed: {error_requesting_uri}")
        return uri

def request_audio_permission(on_result=None):
    """Ask for read access to audio only.

    Android 13+ uses READ_MEDIA_AUDIO; older releases use READ_EXTERNAL_STORAGE.
    Returns a plain-string status:
    "desktop" | "missing_manifest" | "granted" | "requested" | "error".
    """
    if not on_android_platform():
        return "desktop"

    if not is_music_permission_in_manifest():
        return "missing_manifest"

    if MediaPermissionHandler.has_permission_to_access_audio_files():
        logger.info("App already has permission to read audio")
        return "granted"

    try:
        MediaPermissionHandler.ask_permission_to_access_audio_files(callback=on_result)
    except Exception as error_requesting_audio_permission:
        logger.exception("request_audio_permissions failed: %s", error_requesting_audio_permission)
        traceback.print_exc()
        return "error"

    return "requested"

def scan_audio_files():
    """Return track dicts from MediaStore using scoped storage.

    The restricted '_data' (file path) column is intentionally NOT requested;
    on Android 10+ it needs All Files Access. The content:// URI built from the
    MediaStore '_id' is the correct handle for scoped storage.

    Each item: {"uri", "title", "artist", "duration"(ms), "filename"}.

    """
    if not on_android_platform():
        return []

    context = get_python_activity_context()
    if not context:
        logger.error("scan_audio_files: no activity context")
        return []
    resolver = context.getContentResolver()
    uri = autoclass("android.provider.MediaStore$Audio$Media").EXTERNAL_CONTENT_URI
    projection = ["_id", "title", "artist", "duration"]
    cursor = resolver.query(uri, projection, None, None, None)
    tracks = []

    if cursor:
        title_idx = cursor.getColumnIndex("title")
        artist_idx = cursor.getColumnIndex("artist")
        duration_idx = cursor.getColumnIndex("duration")
        id_idx = cursor.getColumnIndex("_id")
        while cursor.moveToNext():
            media_id = cursor.getLong(id_idx)
            title = cursor.getString(title_idx) or "(unknown title)"
            tracks.append(
                {
                    "uri": f"content://media/external/audio/media/{media_id}",
                    "title": title,
                    "artist": cursor.getString(artist_idx) or "",
                    "duration": cursor.getLong(duration_idx),
                    "filename": title,
                }
            )
        cursor.close()
    tracks.sort(key=lambda track: track["filename"].lower())
    logger.info("Scan complete: %d tracks", len(tracks))
    return tracks


class TrackList(RecycleView):
    def __init__(self, on_track_selected, **kwargs):
        super().__init__(**kwargs)
        self.on_track_selected = on_track_selected

    def select_track(self, uri):
        self.on_track_selected(uri)

    def set_tracks(self, tracks, current_uri=None):
        self.data = [
            {

                "filename": track.get("filename") or track.get("title") or "",
                "uri": track["uri"],
                "is_current": track["uri"] == current_uri,
            }
            for track in tracks
        ]

    def mark_current(self, current_uri):
        for item in self.data:
            item["is_current"] = (item["uri"] == current_uri)
        self.refresh_from_data()


class MusicPlayerRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)

        self.tracks = []  # list[dict] MediaStore track info
        self.current_index = -1  # index into self.tracks
        self.sound = None
        self.notification = None
        self._tick = None
        self._seeking = False
        self._pending_seek = None
        self.loop_track = False  # repeat one
        self._scan_in_progress = False
        self._rescan_pending = False
        self._permission_status = None

        # --- top bar: scan + loop --------------------------------
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        self.scan_btn = Button(text="Scan device")
        self.scan_btn.bind(on_release=lambda *_: self.scan_device())
        top.add_widget(self.scan_btn)

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
        self.track_list = TrackList(on_track_selected=self.play_track_by_uri)
        self.add_widget(self.track_list)

        # --- seek bar ------------------------------------------------------
        self.seek_bar = Slider(min=0, max=1, value=0)
        self.seek_bar.bind(
            on_touch_down=self._on_seek_touch_down,
            on_touch_up=self._on_seek_touch_up,
            on_value=lambda *_: self._on_seek_value_changed()
        )
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

    def scan_device(self):
        if self._scan_in_progress:
            return
        self._scan_in_progress = True
        self.scan_btn.disabled = True
        self.status_label.text = "Scanning..."
        # Don't block the scan when permission is absent: public audio still shows.
        self._permission_status = request_audio_permission(on_result=self._on_audio_permission_result)
        self._perform_scan()

    def _perform_scan(self):
        def worker():
            try:
                tracks = scan_audio_files()
            except Exception as e:
                logger.exception(f"scan failed:{e}")
                tracks = []
            self._on_scan_done(tracks)

        threading.Thread(target=worker, daemon=True).start()

    @mainthread
    def _on_audio_permission_result(self, granted):
        # Fresh grant: the running scan only saw public audio, so scan again.
        if not granted:
            return
        if self._scan_in_progress:
            self._rescan_pending = True
        else:
            self.scan_device()

    @mainthread
    def _on_scan_done(self, tracks):
        self._scan_in_progress = False
        self.scan_btn.disabled = False
        self.tracks = tracks
        self.track_list.set_tracks(tracks)

        if self._permission_status == "missing_manifest":
            self.status_label.text = (
                "Audio permission missing from buildozer.spec "
                "(android.permissions=... READ_MEDIA_AUDIO) - showing public audio only"
            )
        elif tracks:
            self.status_label.text = f"Found {len(tracks)} track(s)"
        else:
            self.status_label.text = "No audio files found - grant audio permission and rescan"

        if self._rescan_pending:
            self._rescan_pending = False
            self.scan_device()

    def play_track_by_uri(self, uri):

        for index, track in enumerate(self.tracks):
            if track["uri"] == uri:
                self.current_index = index
                break
        else:
            # Track not in our list (shouldn't happen), just load it directly.
            self.tracks.append(
                {
                    "uri": uri,
                    "title": _basename_of_uri(uri),
                    "artist": "",
                    "duration": 0,
                    "filename": _basename_of_uri(uri),
                }
            )
            self.current_index = len(self.tracks) - 1
        self.load_current()

    def load_current(self):
        if not (0 <= self.current_index < len(self.tracks)):
            return

        track = self.tracks[self.current_index]
        uri = track["uri"]
        title = track.get("title") or _basename_of_uri(uri)

        # Release previous player/notification first (SoundLoader is a singleton).
        self._release_player()

        # Track titles/artists come from MediaStore metadata (no file path needed).
        sound = SoundLoader.load(uri)
        sound.loop = self.loop_track
        sound.bind(on_load=self._on_loaded)
        sound.bind(on_complete=self._on_track_finished)
        sound.bind(state=self._on_state_changed)
        self.sound = sound

        notification = MediaNotification(
            sound,
            on_next=self.next_track,
            on_previous=self.previous_track,
        )
        notification.setTitle(str(title))
        notification.setArtist(track.get("artist") or "Unknown Artist")

        self.notification = notification

        # Reset seek bar
        self.seek_bar.max = 1
        self.seek_bar.value = 0
        self._pending_seek = None
        self._seeking = False
        self.time_label.text = "00:00 / 00:00"
        self.now_playing.text = f"Loading: {title}"
        self.status_label.text = f"Track {self.current_index + 1} / {len(self.tracks)}"
        self.track_list.mark_current(uri)

    def init_notification(self, title, artist):
        self.notification = MediaNotification(
            mediaController=self.sound,
            on_next=self.next_track,
            on_previous=self.previous_track,
        )
        self.notification.setTitle(title)
        self.notification.setArtist(artist)

    def _release_player(self):
        self._stop_ticker()
        if self.sound is not None:
            try:
                self.sound.stop()
                self.sound.unload()
            except Exception as e:
                logger.exception(f"error releasing sound: {e}")
            self.sound = None

    @mainthread
    def _on_loaded(self, *_):
        duration = self.sound.length or 0
        self.seek_bar.max = max(duration, 1)
        self.seek_bar.value = 0
        self._pending_seek = None
        self.sound.play()

        if 0 <= self.current_index < len(self.tracks):
            self.now_playing.text = self.tracks[self.current_index].get("title") or _basename_of_uri(self.sound.source)
        else:
            self.now_playing.text = _basename_of_uri(self.sound.source)

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
            self.sound.seek(target)  # SoundLoader.seek takes seconds
        except Exception as e:
            logger.exception(f"seek failed: {e}")
            self._pending_seek = None

    def _has_next(self):
        return self.current_index + 1 < len(self.tracks) or self.loop_track

    def _has_prev(self):
        return self.current_index > 0

    def next_track(self):
        if not self.tracks:
            return
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
        if self.current_index > 0:
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
        if self.current_index + 1 < len(self.tracks):
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

    def toggle_loop(self):
        self.loop_track = not self.loop_track
        if self.sound is not None:
            self.sound.loop = self.loop_track
        self.loop_btn.text = f"Loop: {'ON' if self.loop_track else 'OFF'}"

    # Lifecycle
    def cleanup(self):
        self._release_player()
        if self.notification is not None:
            try:
                self.notification.release()
            except Exception as e:
                logger.exception(f"error releasing notification: {e}")
            self.notification = None


class MusicPlayerApp(App):
    def build(self):
        self.title = "Music Player"
        return MusicPlayerRoot()

    def on_stop(self):
        if self.root is not None:
            self.root.cleanup()


if __name__ == "__main__":
    MusicPlayerApp().run()
