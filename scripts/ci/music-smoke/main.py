"""Music notification smoke app (Android only).

Checks that the android-notify-music-bridge AAR resolves from Maven into the
fixed package org.android_notify.music, that a media session notification is
built and playing, and that injected KEYCODE_MEDIA_* events reach the Java
MediaSession callback. Emits logcat markers consumed by emulator_music_test.sh:

    MUSIC_BRIDGE_OK           AAR MediaSessionCallback resolved (class + interface)
    MUSIC_NOTIFICATION_BUILT  notification constructed and posted
    MUSIC_PLAYING             audio started
    MUSIC_STATE: <state>      play/pause state changes (KEYCODE_MEDIA_PLAY_PAUSE)
    MUSIC_SKIPPED             KEYCODE_MEDIA_NEXT / PREVIOUS reached the session
"""

import math
import os
import struct
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label

from android_notify.media.music import MediaSessionCallback, MusicNotification
from android_notify.core import asks_permission_if_needed


def _write_tone(path, seconds=30.0, sample_rate=22050, freq=440.0):
    """Tiny mono 16-bit WAV sine tone (stdlib only - no audioop dependency)."""
    n = int(sample_rate * seconds)
    data_size = n * 2
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        for i in range(n):
            v = int(32767 * 0.25 * math.sin(2 * math.pi * freq * i / sample_rate))
            f.write(struct.pack("<h", v))


class SmokeApp(App):
    def build(self):
        return Label(text="android-notify music smoke", color=(0, 0, 0, 1))

    def on_start(self):
        try:
            if MediaSessionCallback is not None:
                print("MUSIC_BRIDGE_OK: org.android_notify.music.MediaSessionCallback loaded", flush=True)
            else:
                print("MUSIC_BRIDGE_MISSING: MediaSessionCallback was not resolved", flush=True)
            self._run_smoke()
        except Exception:
            print("MUSIC_SMOKE_CRASH:", flush=True)
            traceback.print_exc()
            self.stop()

    def _run_smoke(self):
        asks_permission_if_needed()

        from android_notify.config import get_python_activity_context

        context = get_python_activity_context()
        files_dir = context.getFilesDir().getAbsolutePath()
        tone_path = os.path.join(files_dir, "tone.wav")
        _write_tone(tone_path)

        self._built_printed = False
        self._first_play_printed = False

        self.mn = MusicNotification(
            on_next=lambda: print("MUSIC_SKIPPED: next", flush=True),
            on_previous=lambda: print("MUSIC_SKIPPED: prev", flush=True),
        )
        self.mn.setTitle("Smoke Test - android-notify")
        self.mn.setArtist("music notification")

        sound = SoundLoader.load(tone_path)
        self.mn.setSoundLoader(sound)
        self.sound = sound
        sound.bind(state=self._on_state)

        Clock.schedule_once(lambda dt: self._start_playback(), 2)
        Clock.schedule_interval(self._post_build_check, 1)
        Clock.schedule_once(lambda dt: self._smoke_timeout(), 40)

    def _start_playback(self):
        print("MUSIC_STARTING_PLAYBACK", flush=True)
        self.sound.play()

    def _on_state(self, _sound, state):
        print(f"MUSIC_STATE: {state}", flush=True)
        if state == "play" and not self._first_play_printed:
            self._first_play_printed = True
            print("MUSIC_PLAYING", flush=True)

    def _post_build_check(self, dt):
        if self.mn.already_built and not self._built_printed:
            self._built_printed = True
            print("MUSIC_NOTIFICATION_BUILT", flush=True)
            return False
        return True

    def _smoke_timeout(self):
        if not (self._built_printed and self._first_play_printed):
            print("MUSIC_BUILD_TIMEOUT", flush=True)
            self.stop()


if __name__ == "__main__":
    SmokeApp().run()