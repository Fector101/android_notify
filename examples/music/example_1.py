"""
Standalone example: media notification for music playback
=========================================================

``android_notify.media.music.MediaNotification``:

- Play / pause controls on the notification, lock screen and quick settings are auto bound to SoundLoader.
- The seek bar progress moves while playing and can be dragged to seek, no app-side polling of the notification needed.
- Prev / next buttons that appear only when a neighbouring track exists
  (``setNext`` / ``setPrev``).

Tracks are read from MediaStore with scoped storage (``content://`` URIs), so
the app needs ``READ_MEDIA_AUDIO`` (Android 13+) / ``READ_EXTERNAL_STORAGE``
(Android 12 and below) — no All Files Access. Add the permissions (plus
``POST_NOTIFICATIONS`` for the notification) to buildozer.spec:

    android.permissions = POST_NOTIFICATIONS, (name=android.permission.READ_EXTERNAL_STORAGE;maxSdkVersion=32), READ_MEDIA_AUDIO

Paste this file into your own project (it is self-contained)
"""

import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import logging

from android_notify.media.music import MediaNotification
from android_notify.media.music.helper import SoundLoader, MediaPermissionHandler
from android_notify.internal.permissions import is_music_permission_in_manifest
from android_notify.config import on_android_platform, get_python_activity_context
from android_notify import logger as android_notify_logger

android_notify_logger.setLevel(logging.DEBUG)

if on_android_platform():
    from jnius import autoclass
else:
    autoclass = None


def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def scan_audio_files():
    """Return track dicts from MediaStore using scoped storage."""
    if not on_android_platform():
        return []

    context = get_python_activity_context()
    if not context:
        android_notify_logger.error("scan_audio_files: no activity context")
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
            tracks.append(
                {
                    "uri": f"content://media/external/audio/media/{media_id}",
                    "title": cursor.getString(title_idx) or "(unknown title)",
                    "artist": cursor.getString(artist_idx) or "",
                    "duration": cursor.getLong(duration_idx),
                }
            )
        cursor.close()
    tracks.sort(key=lambda track: track["title"].lower())
    return tracks


class MusicPlayerRoot(BoxLayout):
    """The whole example UI: scan, Play/Pause, Prev/Next, Repeat toggle and
    a small time/status readout.

    All the notification logic lives in this class so it can be dropped into
    any screen you already have.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=12, **kwargs)

        self.sound = None
        self.notification = None
        self.tracks = []
        self.current_index = -1
        self._tick = None
        self.loop_enabled = True

        self.scan_btn = self._btn("Scan device", self.scan_device)
        self.add_widget(self.scan_btn)

        nav = BoxLayout(size_hint_y=None, height=48, spacing=6)
        self.prev_btn = self._btn("Prev", self.previous_track)
        nav.add_widget(self.prev_btn)
        self.play_btn = self._btn("Play", self.toggle_play_pause)
        self.play_btn.disabled = True
        nav.add_widget(self.play_btn)
        self.next_btn = self._btn("Next", self.next_track)
        nav.add_widget(self.next_btn)
        self.add_widget(nav)

        self.repeat_btn = self._btn("Repeat: ON", self.toggle_loop)
        self.add_widget(self.repeat_btn)

        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=48)
        self.add_widget(self.time_label)

        self.status_label = Label(text="Scan for music to begin", size_hint_y=None)
        self.add_widget(self.status_label)

    def _btn(self, text, callback):
        button = Button(text=text)
        button.bind(on_release=lambda *_: callback())
        return button

    # ------------------------------------------------------------------ #
    # Scanning                                                            #
    # ------------------------------------------------------------------ #
    def scan_device(self):
        if not is_music_permission_in_manifest():
            self.status_label.text = (
                "Audio permission missing from buildozer.spec "
                "(android.permissions = READ_MEDIA_AUDIO)"
            )
            return

        if MediaPermissionHandler.has_permission_to_access_audio_files():
            self._scan()
            return

        self.status_label.text = "Requesting audio access..."
        MediaPermissionHandler.ask_permission_to_access_audio_files(callback=self._on_permission)

    def _on_permission(self, granted):
        if not granted:
            self.status_label.text = "Audio access denied"
            return
        self._scan()

    def _scan(self):
        self.status_label.text = "Scanning..."

        def worker():
            tracks = scan_audio_files()
            Clock.schedule_once(lambda *_: self._on_scan_done(tracks))

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_done(self, tracks):
        self.tracks = tracks
        if not tracks:
            self.status_label.text = "No audio files found"
            return
        self.status_label.text = f"Found {len(tracks)} track(s)"
        self.current_index = 0
        self.load_current()

    # ------------------------------------------------------------------ #
    # Loading and the two objects that matter                             #
    # ------------------------------------------------------------------ #
    def load_current(self):
        if not (0 <= self.current_index < len(self.tracks)):
            return
        track = self.tracks[self.current_index]

        # Release the previous track/notification first: SoundLoader is a
        # singleton, so a new load would otherwise leak the old MediaPlayer,
        # and the previous notification's callbacks/session would stay active.
        self.cleanup()

        sound = SoundLoader.load(track["uri"])
        if sound is None:
            self.status_label.text = f"Failed to load:\n{track['title']}"
            return
        sound.loop = self.loop_enabled
        sound.bind(on_load=self.on_loaded)
        sound.bind(on_complete=self.on_track_finished)
        sound.bind(state=self.on_state_changed)
        self.sound = sound

        # The notification registers a MediaSession owned by the app and builds
        # an Android media notification around it. Play / pause / seek commands
        # from the notification come back into `sound`, so we only react to
        # state changes.
        notification = MediaNotification(
            sound,
            on_next=self.next_track if self.current_index + 1 < len(self.tracks) else None,
            on_previous=self.previous_track if self.current_index > 0 else None,
        )
        notification.setTitle(track["title"])
        notification.setArtist(track["artist"] or "Unknown Artist")
        self.notification = notification

        self.status_label.text = f"Loading:\n{track['title']}"

    def on_loaded(self, *_):
        """MediaPlayer is ready -> start playing (fires on_load)."""
        self.sound.play()
        self.status_label.text = f"Playing:\n{self.tracks[self.current_index]['title']}"

    def cleanup(self):
        """Release everything (call it from App.on_stop)."""
        self.stop_ticker()
        if self.sound is not None:
            try:
                self.sound.stop()
                self.sound.unload()
            except Exception as error:
                print("cleanup error:", error)
            self.sound = None
        if self.notification is not None:
            self.notification.release()
            self.notification = None

    # ------------------------------------------------------------------ #
    # Play / pause / state                                                #
    # ------------------------------------------------------------------ #
    def toggle_play_pause(self):
        if self.sound is None:
            return
        if self.sound.state == "play":
            self.sound.pause()
        else:
            self.sound.play()

    def on_state_changed(self, instance, state):
        """Called whenever playback starts or stops — including from the
        notification / lock screen, not just from the app's own button."""
        is_playing = state == "play"
        self.play_btn.text = "Pause" if is_playing else "Play"
        self.play_btn.disabled = self.sound is None
        self.prev_btn.disabled = self.current_index <= 0
        self.next_btn.disabled = self.current_index + 1 >= len(self.tracks)
        if is_playing:
            self.start_ticker()
        else:
            self.stop_ticker()
        self.update_time()

    def start_ticker(self):
        if self._tick is None:
            self._tick = Clock.schedule_interval(lambda dt: self.update_time(), 1)

    def stop_ticker(self):
        if self._tick is not None:
            self._tick.cancel()
            self._tick = None

    def update_time(self):
        if self.sound is None:
            return
        self.time_label.text = f"{_fmt(self.sound.get_pos())} / {_fmt(self.sound.length or 0)}"

    # ------------------------------------------------------------------ #
    # End of track: loop vs play-once                                     #
    # ------------------------------------------------------------------ #
    def on_track_finished(self, *_):
        """Fired once per track-end by SoundLoader's completion listener.

        SoundLoader automatically restarts the track (seek 0 + play) when
        ``loop`` is True, so we only have to decide what happens in each mode.
        """
        if self.current_index + 1 < len(self.tracks):
            self.next_track()
        elif self.loop_enabled:
            # Restart is already handled -> snap the UI back to 00:00.
            self.snap_to_zero()
        else:
            # "Play once": stop at the beginning of the track.
            self.sound.seek(0)
            self.sound.state = "pause"   # syncs the play button + notification
            self.snap_to_zero()

    def snap_to_zero(self):
        if self.sound is None:
            return
        self.time_label.text = f"00:00 / {_fmt(self.sound.length or 0)}"

    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        if self.sound is not None:
            self.sound.loop = self.loop_enabled
        self.repeat_btn.text = "Repeat: ON" if self.loop_enabled else "Repeat: OFF"

    def next_track(self):
        if self.current_index + 1 < len(self.tracks):
            self.current_index += 1
            self.load_current()

    def previous_track(self):
        if self.sound is not None and self.sound.get_pos() > 3:
            # Restart the current track before stepping back.
            self.sound.seek(0)
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current()


class MusicExampleApp(App):

    def build(self):
        return MusicPlayerRoot()

    def on_stop(self):
        if self.root is not None:
            self.root.cleanup()


if __name__ == "__main__":
    MusicExampleApp().run()
