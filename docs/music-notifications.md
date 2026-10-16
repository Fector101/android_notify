# Music Notifications

Android Notify ships a full media notification for music playback in Kivy apps:

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
The music module is Android + Kivy only (it builds on `pyjnius` and Kivy's `EventDispatcher`). It does not run on desktop.
```

## Setup

The media buttons are wired through a small **pre-compiled Java bridge**
[`io.github.fector101:android-notify-music-bridge`](https://github.com/Fector101/android_notify/blob/main/bridges/android/CHANGELOG.md),
published on Maven Central. You do not write or copy any Java - just add one line
to your `buildozer.spec`:

```ini
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.1
```

`mavenCentral()` is already included in the Gradle project buildozer generates,
so no extra repository line is needed.

```{note}
If the bridge dependency can't be resolved the notification still builds, but
the media buttons do nothing.
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
from android_notify.media.music.helper import MediaPermissionHandler
from android_notify.internal.permissions import is_music_permission_in_manifest

# 1) Make sure the permission is declared in buildozer.spec.
if not is_music_permission_in_manifest():
    raise RuntimeError(
        "add READ_MEDIA_AUDIO (Android 13+) / READ_EXTERNAL_STORAGE "
        "(Android 12 and below) to android.permissions"
    )

# 2) Check / request runtime access.
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

from android_notify.media.music import MediaNotification
from android_notify.media.music.helper import SoundLoader

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

- `examples/music/simple_example.py` - load + play only.
- `examples/music/example_1.py` - full player UI with loop toggle, end-of-track handling and next/previous wiring.
- `examples/music/example_2.py` - MediaStore-based player with scoped-storage scan, permission handling and a track list.
- `examples/music/plain_controller_example.py` - a Kivy `SoundLoader` wrapped in a plain controller that does not dispatch events, demonstrating `syncPlaybackState()`.

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
from android_notify.media.music import MediaNotification

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

## `SoundLoader` reference

`SoundLoader.load(source)` returns the **singleton** instance, so calling it again reuses the same player (call `unload()` first to release the old track).

- `sound.state` - `'stop'`, `'play'` or `'pause'` (a Kivy `ObjectProperty`, so `sound.bind(state=...)` works).
- `sound.loop` - when `True`, the track restarts from 0 after finishing.
- `sound.length` - duration in seconds (once loaded).
- `sound.play()` / `sound.pause()` / `sound.stop()` - control playback.
- `sound.seek(seconds)` - seek to a position.
- `sound.get_pos()` - current position in seconds.
- `sound.unload()` - release the MediaPlayer.
- Events: `on_load`, `on_play`, `on_pause`, `on_stop`, `on_seek`, `on_complete`.

After a track ends, `get_pos()` and `length` report the finished duration without
querying the underlying `MediaPlayer` (which is leaving the playback state and
would raise `IllegalStateException`). React to `on_complete` to advance instead
of polling position on the `stop` transition.

## `MediaNotification` reference

`MediaNotification` is a singleton too: constructing it again for a new track
refreshes the bound controller and skip callbacks and rebuilds the notification.

- `MediaNotification(mediaController, on_next=None, on_previous=None)` - create the notification and bind a media controller (e.g. a `SoundLoader`); pass callbacks for the skip buttons.
- `setNowPlaying(title, artist)` - set the track metadata and immediately update the live notification (title, artist, artwork and lock-screen metadata) in one step. Preferred on a track change.
- `setTitle(text)` / `setArtist(text)` - track metadata (also shown on the lock screen). Each one updates the live notification if it has already been built, so an existing notification never shows a stale track.
- `setMediaController(media_controller)` - bind or replace the media controller; wires state/load/seek updates to the notification automatically when the controller dispatches them. Builds on `on_load`, or immediately if the controller is already loaded. Re-binding the same controller instance is a no-op (no duplicate handlers). For a plain controller without those events, see [Controllers that don't dispatch events](#controllers-that-dont-dispatch-events).
- `setNext(callback)` / `setPrev(callback)` - set the next/previous track callbacks; an explicit `None` clears the matching action. Buttons and the `MediaSession` actions follow the registered callbacks.
- `syncMediaSession()` - sync the seek bar and playback state (called automatically).
- `syncPlaybackState()` - flip the play/pause icon, sync the seek bar and build the notification if needed. Call it after your own code changes playback on a controller that does not dispatch `state`/`on_seek` events.
- `refresh()` - re-post the built notification, re-applying the current title/artist/artwork and `MediaSession` metadata first.
- `release()` - final teardown of the shared `MediaSession` (call it once in `App.on_stop()`). `MediaNotification` is a singleton that reuses one `MediaSession` for the whole app, so don't release between tracks - only the `SoundLoader` is swapped per track.
