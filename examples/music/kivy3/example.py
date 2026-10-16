"""
Plain-controller music notification: Kivy SoundLoader without events
====================================================================

This example shows how to drive a media notification with a controller that
does **not** dispatch ``state`` / ``on_seek`` events.

Kivy's own ``kivy.core.audio.SoundLoader`` is a good stand-in: its ``Sound``
exposes ``source`` / ``play`` / ``seek`` / ``get_pos`` / ``length`` / ``state``
but has no ``on_seek`` event and no ``pause()``. We wrap it in a tiny adapter
that:

- adds a ``pause()`` (Kivy's ``Sound`` has none) by stopping and remembering the
  position, then seeking back on resume;
- tracks the playback state itself (Kivy's Android backend does not update
  ``state`` when the sound is stopped).

Because the adapter is a plain object (not a Kivy ``EventDispatcher``),
``MediaNotification`` skips event binding. The notification's own play/pause and
seek buttons still work - but whenever *your app* changes playback you must call
``notification.syncPlaybackState()`` so the notification follows. That single
call is the whole manual half of the feature.

For a full-featured player built on the event-driven ``SoundLoader`` (loop,
auto-advance, content:// MediaStore URIs) see ``example_2.py``.

Caveats of Kivy's SoundLoader:
- it plays *file paths* only; ``content://`` URIs are not supported;
- there is no ``on_complete`` event, so this minimal demo does not auto-advance.
"""

# An audio file path on the device. Reading it needs the audio permission, which
# is requested after the UI is up (see _start_after_ui). Swap for any file path.
TRACK = "/storage/emulated/0/Ringtones/test.mp3"

import logging

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
try:
    from kivy.core.audio_output import SoundLoader as KivySoundLoader
except ModuleNotFoundError:
    from kivy.core.audio import SoundLoader as KivySoundLoader


from android_notify.widgets.log_view import LogPanel, install_kivy_log_handler

_LOG_HANDLER = install_kivy_log_handler()

from android_notify.media import MediaNotification
from android_notify.media.music.helper import MediaPermissionHandler


logger = logging.getLogger("PlainControllerExample")


def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class KivySoundController:
    """Minimal ``IMediaController`` adapter around a Kivy ``Sound`` (no events).

    A plain object on purpose: it has no ``bind`` / ``dispatch`` / ``events``,
    so ``MediaNotification`` treats it as a controller that cannot drive the
    notification through events.
    """

    def __init__(self, source):
        self._sound = KivySoundLoader.load(source)
        self._length = float(self._sound.length or 0) if self._sound else 0.0
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
        return self._sound.get_pos()

class PlainControllerApp(App):
    def build(self):
        self.title = "Plain Controller Example"

        # Playback objects are created only after the UI exists and the audio
        # permission is granted (see _start_after_ui).
        self.controller = None
        self.notification = None

        root = BoxLayout(orientation="vertical", padding=[dp(10),dp(50)], spacing=dp(12))

        self.status = Label(text="Starting...", size_hint_y=None, height=dp(40))
        root.add_widget(self.status)

        self.toggle_btn = Button(text="Play", size_hint_y=None, height=dp(48))
        self.toggle_btn.disabled = True  # enabled once a track is loaded
        self.toggle_btn.bind(on_release=lambda *_: self.toggle_play_pause())
        root.add_widget(self.toggle_btn)

        self.seek = Slider(min=0, max=1, value=0, size_hint_y=None, height=100)
        self.seek.bind(on_touch_up=self._on_seek)
        root.add_widget(self.seek)

        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=dp(28),y=100)
        root.add_widget(self.time_label)

        # --- on-screen log panel (always visible) --------------------------
        self.log_panel = LogPanel(handler=_LOG_HANDLER, size_hint_y=1)
        root.add_widget(self.log_panel)
        logger.info("UI created, track=%s", TRACK)

        # Start sound loading, the notification and the permission request only
        # after the UI is up (a short delay lets the activity resume so the
        # permission dialog can be shown).
        Clock.schedule_once(self._start_after_ui, 2)

        # App-side UI refresh only - the system seek bar is anchored by
        # syncPlaybackState() and interpolated by Android, so this is not a poll.
        Clock.schedule_interval(self._refresh, 0.25)
        return root

    @mainthread
    def _start_after_ui(self, _dt):
        self.status.text = "Requesting audio permission..."
        logger.info("requesting audio permission")
        # Loading the track needs read access to the audio file, so request it
        # first and only start playback from the grant callback.
        MediaPermissionHandler.ask_permission_to_access_audio_files(
            callback=self._on_audio_permission
        )

    @mainthread
    def _on_audio_permission(self, granted):
        logger.info("audio permission granted=%s", granted)
        if not granted:
            self.status.text = "Audio permission denied - cannot load track"
            self.toggle_btn.disabled = True
            return
        self._start_playback()

    def _start_playback(self):
        # 1. load the sound
        self.controller = KivySoundController(TRACK)
        self.seek.max = max(self.controller.length, 1)

        # 2. build the notification and let it anchor the system seek bar.
        self.notification = MediaNotification(
            mediaController=self.controller,
            on_next=None,
            on_previous=None,
        )
        self.notification.setTitle("Plain controller")
        self.notification.setArtist("Kivy SoundLoader adapter")

        if self.controller.source is None:
            self.status.text = f"Could not load: {TRACK}"
            self.toggle_btn.disabled = True
        else:
            self.status.text = "Ready"
            self.toggle_btn.disabled = False
            # No on_load event will ever fire, so build the notification here.
            self.notification.syncPlaybackState()

    def toggle_play_pause(self):
        if self.controller is None:
            return
        if self.controller.state == "play":
            self.controller.pause()
            logger.info("pause")
        else:
            self.controller.play()
            logger.info("play")
        # App-driven change -> tell the notification (it has no events to react
        # to). The notification's own play/pause button does this for you.
        self.notification.syncPlaybackState()
        self._refresh(0)

    def _on_seek(self, slider, touch):
        if self.controller is None:
            return
        if slider.collide_point(*touch.pos):
            self.controller.seek(slider.value)
            logger.info("seek %.1fs", slider.value)
            self.notification.syncPlaybackState()  # app-driven seek

    def _refresh(self, _dt):
        if self.controller is None:
            return
        pos = self.controller.get_pos()
        length = self.controller.length or 0
        self.seek.max = max(length, 1)
        self.seek.value = min(pos, self.seek.max)
        self.time_label.text = f"{_fmt(pos)} / {_fmt(length)}"
        self.toggle_btn.text = "Pause" if self.controller.state == "play" else "Play"

    def on_stop(self):
        if self.controller is not None and self.controller.state == "play":
            self.controller.pause()
        if self.notification is not None:
            self.notification.release()
        for logger_name in ("", "android_notify"):
            logging.getLogger(logger_name).removeHandler(_LOG_HANDLER)


if __name__ == "__main__":
    PlainControllerApp().run()
