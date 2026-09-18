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

import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import logging
from android_notify.media.music import MusicNotification
from android_notify.media.music.helper import SoundLoader, requestAllFilesAccess
from android_notify import logger as android_notify_logger
android_notify_logger.setLevel(logging.DEBUG)
DEFAULT_TRACK_PATH = "/storage/emulated/0/Music/test.mp3"


def _fmt(seconds):
    """Seconds -> "mm:ss"."""
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class MusicPlayerRoot(BoxLayout):
    """The whole example UI: path input, Load, Play/Pause, Repeat toggle and
    a small time/status readout.

    All the notification logic lives in this class so it can be dropped into
    any screen you already have.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=12, **kwargs)

        self.sound = None
        self.notification = None
        self._tick = None

        # --- example state -------------------------------------------------
        # A real queue would compute these from (current_index, len(tracks)).
        self.loop_enabled = True
        self.has_next = False   # set True if a next track exists
        self.has_prev = False   # set True if a previous track exists

        self.path_input = TextInput(
            text=DEFAULT_TRACK_PATH,
            multiline=False,
            size_hint_y=None,
            height=48,
        )
        self.add_widget(self.path_input)

        self.load_btn = self._btn("Load", self.load_track)
        self.add_widget(self.load_btn)

        self.play_btn = self._btn("Play", self.toggle_play_pause)
        self.play_btn.disabled = True
        self.add_widget(self.play_btn)

        self.repeat_btn = self._btn("Repeat: ON", self.toggle_loop)
        self.add_widget(self.repeat_btn)

        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=48)
        self.add_widget(self.time_label)

        self.status_label = Label(text="Load a track to begin", size_hint_y=None)
        self.add_widget(self.status_label)

    def _btn(self, text, callback):
        button = Button(text=text)
        button.bind(on_release=lambda *_: callback())
        return button

    # ------------------------------------------------------------------ #
    # Loading and the two objects that matter                              #
    # ------------------------------------------------------------------ #
    def load_track(self):
        """Create the SoundLoader + MusicNotification and wire them together."""
        path = (self.path_input.text or DEFAULT_TRACK_PATH).strip()

        # Release the previous track/notification first: SoundLoader is a
        # singleton, so a new load would otherwise leak the old MediaPlayer,
        # and the previous notification's callbacks/session would stay active.
        self.cleanup()

        # 1) Ask for All Files Access (needed to read /storage/emulated/0).
        requestAllFilesAccess()
        notification = MusicNotification(
                  on_next=self.next_track,
                  on_previous=self.previous_track,
        )
        notification.setTitle(os.path.splitext(os.path.basename(path))[0] or "Unknown")
        notification.setArtist("Example Artist")

        # 2) The player. SoundLoader is a singleton; `load` prepares the
        #    Android MediaPlayer asynchronously and fires on_load when ready.
        sound = SoundLoader.load(path)
        sound.loop = self.loop_enabled
        sound.bind(on_load=self.on_loaded)
        sound.bind(on_complete=self.on_track_finished)  # our end-of-track hook
        sound.bind(state=self.on_state_changed)         # play/pause from anywhere
        self.sound = sound

        # 3) The notification. It registers a MediaSession owned by the app
        #    and builds an Android media notification around it. All play /
        #    pause / seek commands from the notification come back into
        #    `sound`, so you only have to react to state changes.

        notification.setSoundLoader(sound)              # wires state/on_load/on_seek
        notification.set_skip_available(self.has_next, self.has_prev)
        self.notification = notification

        self.status_label.text = f"Loading {path}"

    def on_loaded(self, *_):
        """MediaPlayer is ready -> start playing (fires on_load)."""
        self.sound.play()
        self.status_label.text = f"Playing {self.sound.source}"

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
        if self.has_next:
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

    # -------------------------------
    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        if self.sound is not None:
            self.sound.loop = self.loop_enabled
        self.repeat_btn.text = "Repeat: ON" if self.loop_enabled else "Repeat: OFF"

    def next_track(self):
        """Replace with your queue logic, then call load_track() again."""
        print("next_track: point this at your next file")

    def previous_track(self):
        """Replace with your queue logic, then call load_track() again."""
        print("previous_track: point this at your previous file")


class MusicExampleApp(App):

    def build(self):
        return MusicPlayerRoot()

    def on_stop(self):
        if self.root is not None:
            self.root.cleanup()


if __name__ == "__main__":
    MusicExampleApp().run()
