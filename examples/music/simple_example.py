"""
Standalone example: media notification for music playback
=========================================================

``android_notify.media.music.MediaNotification``:

- Play / pause controls on the notification, lock screen and quick settings are auto bound to SoundLoader.
- The seek bar progress moves while playing and can be dragged to seek, no app-side polling of the notification needed.

Tracks are read from MediaStore with scoped storage (``content://`` URIs), so
the app needs ``READ_MEDIA_AUDIO`` (Android 13+) / ``READ_EXTERNAL_STORAGE``
(Android 12 and below) — no All Files Access. Add the permissions (plus
``POST_NOTIFICATIONS`` for the notification) to buildozer.spec:

    android.permissions = POST_NOTIFICATIONS, (name=android.permission.READ_EXTERNAL_STORAGE;maxSdkVersion=32), READ_MEDIA_AUDIO

Paste this file into your own project (it is self-contained)
"""

import logging

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from android_notify.config import on_android_platform, get_python_activity_context
from android_notify.media.music import MediaNotification
from android_notify.media.music.helper import SoundLoader, MediaPermissionHandler
from android_notify.internal.permissions import is_music_permission_in_manifest
from android_notify import logger

logger.setLevel(logging.DEBUG)

if on_android_platform():
    from jnius import autoclass
else:
    autoclass = None


def scan_audio_files():
    """Return track dicts from MediaStore using scoped storage.

    The ``_data`` (file path) column is intentionally not requested: on
    Android 10+ it needs All Files Access. The ``content://`` URI built from the
    MediaStore ``_id`` is the correct handle under scoped storage.
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


class TestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.sound = None
        self.notification = None
        self.tracks = []
        self.current_index = 0

    def build(self):
        self.sound = None
        self.notification = None

        root = BoxLayout(orientation="vertical", padding=20, spacing=12)

        self.status_label = Label(text="Tap 'Play first track' to begin")
        self.status_label.bind(
            size=lambda *a: setattr(self.status_label, "text_size", self.status_label.size)
        )
        root.add_widget(self.status_label)

        root.add_widget(Button(text="Play first track", on_release=lambda *_: self.start()))

        return root

    def start(self):
        if not is_music_permission_in_manifest():
            self.status_label.text = (
                "Audio permission missing from buildozer.spec\n"
                "(android.permissions = READ_MEDIA_AUDIO)"
            )
            return

        if MediaPermissionHandler.has_permission_to_access_audio_files():
            self._scan_and_play()
            return

        self.status_label.text = "Requesting audio access..."
        MediaPermissionHandler.ask_permission_to_access_audio_files(callback=self._on_permission)

    def _on_permission(self, granted):
        if not granted:
            self.status_label.text = "Audio access denied"
            return
        self._scan_and_play()

    def _scan_and_play(self):
        self.tracks = scan_audio_files()
        if not self.tracks:
            self.status_label.text = "No audio files found"
            return
        self.current_index = 0
        self.load_track()

    def load_track(self):
        track = self.tracks[self.current_index]

        self._release_sound()

        sound = SoundLoader.load(track["uri"])
        if sound is None:
            self.status_label.text = f"Failed to load:\n{track['title']}"
            return
        sound.loop = True
        sound.bind(on_load=self.on_loaded)
        self.sound = sound

        self.notification = MediaNotification(
            sound,
            on_next=self.next_track if self.current_index + 1 < len(self.tracks) else None,
            on_previous=self.previous_track if self.current_index > 0 else None,
        )
        self.notification.setTitle(track["title"])
        self.notification.setArtist(track["artist"] or "Unknown Artist")

        self.status_label.text = f"Loading:\n{track['title']}"

    def on_loaded(self, *_):
        self.sound.play()
        self.status_label.text = f"Playing:\n{self.tracks[self.current_index]['title']}"

    def next_track(self):
        if self.current_index + 1 < len(self.tracks):
            self.current_index += 1
            self.load_track()

    def previous_track(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_track()

    def _release_sound(self):
        if self.sound is not None:
            self.sound.stop()
            self.sound.unload()
            self.sound = None

    def cleanup(self):
        """Full teardown (app shutdown only)."""
        self._release_sound()
        if self.notification is not None:
            self.notification.release()
            self.notification = None

    def on_stop(self):
        self.cleanup()


if __name__ == "__main__":
    TestApp().run()
