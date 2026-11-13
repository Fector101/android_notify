# Media Notifications

Android Notify ships a full media notification for audio and video playback in Kivy apps:

- `MediaNotification` - a media-style notification with a system `MediaSession`. Play / pause / next / previous controls are shown on the notification, the lock screen and Quick Settings, and the seek bar moves (and seeks) on its own.
- `SoundLoader` - an Android `MediaPlayer` wrapper with Kivy events (`on_load`, `on_play`, `on_pause`, `on_seek`, `on_complete`).
- `MediaPermissionHandler` - helpers to check and request `READ_MEDIA_AUDIO` (Android 13+) / `READ_EXTERNAL_STORAGE` (Android 12 and below).

The whole point: button presses and seek commands typed from the notification are routed **back into your media controller automatically**. You only react to its state events; you never re-post or poll the notification yourself.

The notification does not depend on `SoundLoader` directly. It works against any object that satisfies the small `IMediaController` contract:

- `source` (property) - current media path or `content://` URI.
- `play()` / `pause()` / `seek(seconds)`.
- `get_pos()` - current position in seconds.
- `length` (property) - duration in seconds.
- `state` (property) - `"play"` or anything else (treated as paused).

`SoundLoader` already implements this, so most apps can use it as-is. Pass a Kivy `Sound` (or any wrapper) to use a different player - just keep the contract above.

If your controller is **not** a Kivy `EventDispatcher` (or does not expose `state` and `on_seek` events), the notification skips event binding and falls back to the manual sync described in [Controllers that don't dispatch events](#controllers-that-dont-dispatch-events).

```{note}
The media notification module is Android + Kivy only (it builds on `pyjnius`
and Kivy's `EventDispatcher`). It does not run on desktop. The bundled
`SoundLoader` is an audio player; the notification itself works with any media
controller that follows the contract above.
```

## Setup

The media buttons are wired through a small **pre-compiled Java bridge**
[`io.github.fector101:android-notify-music-bridge`](https://github.com/Fector101/android_notify/blob/main/bridges/android/CHANGELOG.md),
published on Maven Central. You do not write or copy any Java - just add one line
to your `buildozer.spec`:

```ini
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.2
```

`mavenCentral()` is already included in the Gradle project buildozer generates,
so no extra repository line is needed.

```{note}
The AAR manifest registers the explicit, non-exported receiver used by the
notification's play/pause/next/previous buttons. Android 12 builds should use
bridge version 1.0.2 or later; older bridge versions do not include this
receiver.
```

## Reading audio files

`SoundLoader.load()` accepts either an absolute file path or a `content://` URI.

Playing audio **requires the audio read permission**: `READ_MEDIA_AUDIO` on
Android 13+, `READ_EXTERNAL_STORAGE` on Android 12 and below. This applies to
external-storage files too - including `Ringtones`, `Notifications` and `Alarms`
under `/storage/emulated/0/...`. Without it, `SoundLoader.load()` fails with
`Couldn't open asset`:

```python
sound = SoundLoader.load("/storage/emulated/0/Ringtones/my_ringtone.ogg")
```

```{note}
`SoundLoader.load()` routes sources that start with `content://` through the
resolver and everything else (like the path above) straight to the file. Pass
`use_path=True` only if a real file path happens to start with `content://`.
```

Declare both permissions - plus `POST_NOTIFICATIONS` for the notification itself
- in `buildozer.spec`:

```ini
android.permissions = POST_NOTIFICATIONS, (name=android.permission.READ_EXTERNAL_STORAGE;maxSdkVersion=32), READ_MEDIA_AUDIO
```

Then check/request the audio permission at runtime:

```python
from android_notify.media.music import MediaPermissionHandler

if not MediaPermissionHandler.has_permission_to_access_audio_files():
    MediaPermissionHandler.ask_permission_to_access_audio_files(callback=on_granted)
    return
```

Then query `MediaStore` for each track's `_id` and turn it into a `content://`
URI. The `_id` is per-device, so it can only be discovered by querying - never
hardcode it:

```python
from jnius import autoclass

from android_notify.config import get_python_activity_context

def scan_audio_files():
    resolver = get_python_activity_context().getContentResolver()
    collection = autoclass("android.provider.MediaStore$Audio$Media").EXTERNAL_CONTENT_URI
    cursor = resolver.query(collection, ["_id", "title", "artist", "duration"], None, None, None)
    tracks = []
    if cursor:
        id_idx = cursor.getColumnIndex("_id")
        title_idx = cursor.getColumnIndex("title")
        artist_idx = cursor.getColumnIndex("artist")
        duration_idx = cursor.getColumnIndex("duration")
        while cursor.moveToNext():
            media_id = cursor.getLong(id_idx)
            tracks.append({
                "uri": f"content://media/external/audio/media/{media_id}",
                "title": cursor.getString(title_idx) or "(unknown title)",
                "artist": cursor.getString(artist_idx) or "",
                "duration": cursor.getLong(duration_idx),
            })
        cursor.close()
    return tracks

tracks = scan_audio_files()
if tracks:
    sound = SoundLoader.load(tracks[0]["uri"])
else:
    sound = None  # no audio found - show an empty state instead
```

```{note}
The scan is fast because `MediaStore` is an index maintained by Android - you
never walk the filesystem yourself. On a real device the query above returned
**270 tracks across different folders in about 2 seconds**, including tracks in
`Music`, `Download`, `Ringtones` and app-specific folders.
```

```{caution}
Don't request the `_data` (file path) column: it is restricted on Android 10+,
so read tracks through the `content://` URI built from `_id` instead. Also avoid
`MANAGE_EXTERNAL_STORAGE` ("All files access") - it is a restricted permission
under Google Play policy. Absolute paths work too, but they still require the
audio permission and are less portable across devices than the `content://`
route built from `_id`.
```

## Minimal example

```{note}
The notification is built when the media controller finishes loading (its
`on_load` event) and is dispatched automatically. `setMediaController` handles
both call orders: wire it before the load completes (it waits for `on_load`), or
after the controller is already loaded (it builds the notification immediately).
```

```python
import os

from kivy.app import App
from kivy.uix.button import Button

from android_notify.media import MediaNotification
from android_notify.media.music import SoundLoader

# An external-storage ringtone. Reading it needs the audio permission (see
# "Reading audio files"); otherwise the load fails with "Couldn't open asset".
TRACK = "/storage/emulated/0/Ringtones/my_ringtone.ogg"


class MyApp(App):
    def build(self):
        # 1) The player: prepares the MediaPlayer asynchronously,
        #    fires on_load when ready.
        self.sound = SoundLoader.load(TRACK)
        self.sound.loop = True
        self.sound.bind(on_load=self.on_loaded)
        self.sound.bind(on_complete=self.on_track_finished)
        self.sound.bind(state=self.on_state_changed)

        # 2) The notification: builds a media notification and wires it to the
        #    same player. Pass the skip callbacks up front (or later with
        #    setNext()/setPrev()).
        self.notification = MediaNotification(
            self.sound,
            on_next=self.next_track,
            on_previous=self.previous_track,
        )
        title=os.path.splitext(os.path.basename(TRACK))[0]
        artist="Example Artist"
        self.notification.setNowPlaying(title, artist)

        return Button(text="Playing...")

    def on_loaded(self, *_):
        self.sound.play()

    def on_state_changed(self, instance, state):
        # Called whenever playback starts/stops, including from the
        # notification or lock screen.
        self.root.text = "Paused" if state != "play" else "Playing..."

    def on_track_finished(self, *_):
        # loop=True auto-restarts the track; no-op needed here.
        pass

    def next_track(self):
        print("point this at the next file in your queue")

    def previous_track(self):
        print("point this at the previous file in your queue")

    def on_stop(self):
        self.sound.stop()
        self.sound.unload()
        self.notification.release()


if __name__ == "__main__":
    MyApp().run()
```

Ready-to-run variants live in the repository under `examples/music/`:

- `examples/music/kivy2_android_only/simple_example.py` - standalone player: MediaStore scan, load and play, with the notification bound to `SoundLoader`.
- `examples/music/kivy2_android_only/example_1.py` - compact player: transport controls, Repeat toggle, auto-advance and an in-app log panel.
- `examples/music/kivy2_android_only/full_app_example.py` - full app: track list, draggable seek bar, loop/shuffle, auto-advance and album art.
- `examples/music/kivy3/example.py` - plain controller (Kivy `SoundLoader` with no events) driven through `syncPlaybackState()`.
- `examples/music/kivy3/full_app_example.py` - full-size plain-controller player: track list, seek bar, loop and auto-advance.

## Controllers that don't dispatch events

`SoundLoader` is a Kivy `EventDispatcher`, so it emits `state`, `on_load` and
`on_seek` and the notification updates itself automatically. A plain object that
only fulfills the `IMediaController` contract, however, has no events to bind to.
In that case the notification:

- still routes its own play / pause / seek / next / previous buttons into your
  controller, and refreshes itself after a transport button press;
- will **not** notice playback changes your own code makes (e.g. a play button in
  your UI) unless you tell it.

Track changes don't need `syncPlaybackState()`: `setTitle()` / `setArtist()` /
`setNowPlaying()` update the live notification directly (on a dispatching
controller too, they simply cover the window before the next rebuild).

Call `syncPlaybackState()` whenever your code changes playback on a
non-dispatching controller. Call it once after the player becomes ready too, so
the notification gets built:

```python
from android_notify.media import MediaNotification

class MyPlayer:
    def __init__(self):
        self.source = "/storage/emulated/0/Ringtones/my_ringtone.ogg"
        self.state = "stop"
        self.length = 0.0
        self._pos = 0.0
        # ... start your own audio backend here ...

    def play(self):
        self.state = "play"
        # ... start the backend, then tell the notification:
        self.notification.syncPlaybackState()

    def pause(self):
        self.state = "pause"
        self.notification.syncPlaybackState()

    def seek(self, seconds):
        self._pos = seconds
        self.notification.syncPlaybackState()

    def get_pos(self):
        return self._pos


player = MyPlayer()
player.notification = MediaNotification(player)
# once your backend is ready:
player.notification.syncPlaybackState()
```

```{note}
`syncMediaSession()` is the lower-level call that only updates the seek bar and
playback state; `syncPlaybackState()` additionally flips the play/pause icon and
builds the notification if it hasn't been built yet. Prefer `syncPlaybackState()`
for plain controllers.
```

### Kivy `SoundLoader` as a plain controller

The `kivy3` examples and the tested Melo app wrap Kivy's own
`kivy.core.audio.SoundLoader` in a plain controller. On Android, ask Kivy for
the framework `android` audio provider explicitly. With the SDL3 bootstrap,
Kivy's default choice suspends its audio device when the activity pauses, so
playback stops when the app is backgrounded or the screen turns off. The
`android` provider keeps playing.

```python
from android_notify.config import on_android_platform

try:
    from kivy.core.audio_output import SoundLoader as KivySoundLoader
except ModuleNotFoundError:
    from kivy.core.audio import SoundLoader as KivySoundLoader


def load_kivy_sound(path):
    if on_android_platform():
        return KivySoundLoader.load(path, audio_output_provider="android")
    return KivySoundLoader.load(path)
```

Kivy's own `SoundLoader` plays file paths only; it does not support `content://`
URIs and has no `on_complete` event. It also has no `pause()`, so the Melo
controller stops the sound, remembers the position and seeks back on resume.

## Reference

`MediaNotification(mediaController, on_next=None, on_previous=None)` creates the notification and binds a controller.

- `setNowPlaying(title, artist)` - set both fields and refresh once. Preferred on a track change.
- `setTitle(text)` / `setArtist(text)` - update one field; the live notification follows if it has been built.
- `setLargeIcon(music_path=None, img_path=None)` - use embedded art or an explicit image. Artless tracks fall back to the default app icon.
- `setMediaController(controller)` - bind or replace the player. Re-binding the same instance is a no-op.
- `setNext(callback)` / `setPrev(callback)` - set or clear (with `None`) the skip actions and their `MediaSession` actions.
- `syncPlaybackState()` - flip the play/pause icon, sync the seek bar and build the notification if needed. Use after app-driven changes on plain controllers.
- `syncMediaSession()` - lower-level seek-bar and playback-state sync (called automatically).
- `refresh()` - re-post the notification, re-applying now-playing metadata and artwork first.
- `release()` - final `MediaSession` teardown. Call once in `App.on_stop()`, not between tracks.

`SoundLoader.load(source)` returns the singleton player. It exposes `state`, `loop`, `length`, `play()`, `pause()`, `stop()`, `seek(seconds)`, `get_pos()`, `unload()` and the events `on_load`, `on_play`, `on_pause`, `on_stop`, `on_seek` and `on_complete`.
