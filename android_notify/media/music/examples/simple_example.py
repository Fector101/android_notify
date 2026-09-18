"""
Standalone example: media notification for music playback
=========================================================

``android_notify.media.music.MusicNotification``:

- Play / pause controls on the notification, lock screen and quick settings are auto bound to SoundLoader.
- The seek bar progress moves while playing and can be dragged to seek, no app-side polling of the notification needed.

- Prev / next buttons that are removed from the notification when there is
  no track in that direction (``set_skip_available``).

Paste this file into your own project (it is self-contained)

"""

import os, logging

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from android_notify.media.music import MusicNotification
from android_notify.media.music.helper import SoundLoader, requestAllFilesAccess
from android_notify import logger

logger.setLevel(logging.DEBUG)

#  CONSTANT PATH - change this to your audio file
AUDIO_ABSOLUTE_PATH = "/storage/emulated/0/Music/test.mp3"


class TestApp(App):
    def build(self):
        self.sound = None
        self.notification = None

        root = BoxLayout(orientation="vertical", padding=20, spacing=12)

        # Status
        self.status_label = Label(
            text=f"Path:\n{AUDIO_ABSOLUTE_PATH}",
            halign="center", valign="middle",
        )
        self.status_label.bind(
            size=lambda *a: setattr(self.status_label, "text_size", self.status_label.size)
        )
        root.add_widget(self.status_label)

        # Load button
        load_btn = Button(text="Load", on_release=lambda *_: self.load_track())
        root.add_widget(load_btn)

        return root

    def load_track(self):
        if not os.path.exists(AUDIO_ABSOLUTE_PATH):
            self.status_label.text = f"File not found:\n{AUDIO_ABSOLUTE_PATH}"
            return

        # Ask for All Files Access (MANAGE_EXTERNAL_STORAGE) to read the
        # hard-coded absolute path on Android 11+. This is a special-access
        # permission that Google Play policy restricts for music apps: prefer
        # READ_MEDIA_AUDIO and the Storage Access Framework
        # (ACTION_OPEN_DOCUMENT) for Play-published apps.
        requestAllFilesAccess()

        # Create notification Instance
        self.notification = MusicNotification()
        # No queue in this example: don't advertise prev/next skip controls.
        self.notification.set_skip_available(False, False)
        self.notification.setTitle(os.path.splitext(os.path.basename(AUDIO_ABSOLUTE_PATH))[0] or "Unknown")
        self.notification.setArtist("Example Artist")

        # Load the sound
        self.sound = SoundLoader.load(AUDIO_ABSOLUTE_PATH)
        self.sound.loop = True
        self.sound.bind(on_load=self.on_loaded)

        # Wire the notification to the sound
        self.notification.setSoundLoader(self.sound)

        self.status_label.text = f"Loaded:\n{AUDIO_ABSOLUTE_PATH}"

    def on_loaded(self, *_):
        self.sound.play()
        self.status_label.text = f"Playing:\n{os.path.basename(AUDIO_ABSOLUTE_PATH)}"

    def cleanup(self):
        if self.sound is not None:
            self.sound.stop()
            self.sound.unload()
            self.sound = None
        if self.notification is not None:
            self.notification.release()
            self.notification = None

    def on_stop(self):
        self.cleanup()


if __name__ == "__main__":
    TestApp().run()