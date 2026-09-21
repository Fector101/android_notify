# Music Notifications

Android Notify ships a full media notification for music playback in Kivy apps:

- `MusicNotification` - a media-style notification with a system `MediaSession`. Play / pause / next / previous controls are shown on the notification, the lock screen and Quick Settings, and the seek bar moves (and seeks) on its own.
- `SoundLoader` - an Android `MediaPlayer` wrapper with Kivy events (`on_load`, `on_play`, `on_pause`, `on_seek`, `on_complete`).
- `requestAllFilesAccess()` - a helper that opens the "All files access" permission screen on Android 11+.

The whole point: button presses and seek commands typed from the notification are routed **back into your `SoundLoader` automatically**. You only react to its state events; you never re-post or poll the notification yourself.

```{note}
The music module is Android + Kivy only (it builds on `pyjnius` and Kivy's `EventDispatcher`). It does not run on desktop.
```

## Setup

Add `android-notify` to your `buildozer.spec` requirements (see [Installation](installation.md)):

```ini
requirements = python3, kivy, pyjnius, android-notify
```

The media buttons are wired through a small **pre-compiled Java bridge**
[`io.github.fector101:android-notify-music-bridge`](../bridges/android/CHANGELOG.md),
published on Maven Central. You do not write or copy any Java - just add one line
to your `buildozer.spec`:

```ini
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.0
```

`mavenCentral()` is already included in the Gradle project buildozer generates,
so no extra repository line is needed.

```{note}
If the bridge dependency can't be resolved the notification still builds, but
the media buttons do nothing.
```

### Legacy: `android.add_src` fallback

Toolchains that can't pull a Gradle dependency (older p4a setups, forks) can ship
the bridge as a Java source file instead. The file is **fixed** - you never edit
a package line because the bridge always lives in `org.android_notify.music`.

1. Create a `src` folder next to your `buildozer.spec` and add `src/MediaSessionCallback.java` to it.
2. Paste the contents below into that file.
3. Point buildozer at the folder in `buildozer.spec`:

```ini
android.add_src = ./src
```

`src/MediaSessionCallback.java`:

```java
// Android-Notify media bridge: receives MediaSession transport control events
// (play/pause/seek/next/prev) and forwards them to a Python listener interface.
// Keep the package line exactly as-is - it must match the pre-compiled bridge.

package org.android_notify.music;

import android.media.session.MediaSession;

public class MediaSessionCallback extends MediaSession.Callback {

    public interface MediaSessionListener {
        void onPlay();
        void onPause();
        void onSeekTo(long pos);
        void onSkipToNext();
        void onSkipToPrevious();
    }

    private MediaSessionListener listener;

    public MediaSessionCallback(MediaSessionListener listener) {
        this.listener = listener;
    }

    @Override
    public void onPlay() {
        if (listener != null) {
            listener.onPlay();
        }
    }

    @Override
    public void onPause() {
        if (listener != null) {
            listener.onPause();
        }
    }

    @Override
    public void onSeekTo(long pos) {
        if (listener != null) {
            listener.onSeekTo(pos);
        }
    }

    @Override
    public void onSkipToNext() {
        if (listener != null) {
            listener.onSkipToNext();
        }
    }

    @Override
    public void onSkipToPrevious() {
        if (listener != null) {
            listener.onSkipToPrevious();
        }
    }
}
```

```{note}
If the Java file is missing the notification still builds, but the media buttons do nothing. The exact same file content is also shown in your logs when the bridge can't be found (`android_notify.media.music.helper.JAVA_CALLBACK_FILE_CONTENT`).
```

## Reading audio files

To load a track by absolute path (e.g. `/storage/emulated/0/Music/song.mp3`) you need to ask for **All files access** on Android 11+:

```python
from android_notify.media.music.helper import requestAllFilesAccess

requestAllFilesAccess()
```

```{caution}
`MANAGE_EXTERNAL_STORAGE` ("All files access") is a restricted permission under Google Play policy. For Play-published apps, prefer `READ_MEDIA_AUDIO` (Android 13+) / `READ_EXTERNAL_STORAGE` (Android 12 and below) with the Storage Access Framework (`ACTION_OPEN_DOCUMENT`) instead.
```

## Minimal example

```{note}
The notification is built when the sound finishes loading (its `on_load`
event) and is dispatched automatically. `setSoundLoader` handles both call
orders: wire it before the load completes (it waits for `on_load`), or after
the sound is already loaded (it builds the notification immediately).
```

```python
import os

from kivy.app import App
from kivy.uix.button import Button

from android_notify.media.music import MusicNotification
from android_notify.media.music.helper import SoundLoader, requestAllFilesAccess

TRACK = "/storage/emulated/0/Music/test.mp3"


class MyApp(App):
    def build(self):
        requestAllFilesAccess()

        # 1) The notification: builds a media notification and wires it to
        #    the same player.
        self.notification = MusicNotification(
            on_next=self.next_track,
            on_previous=self.previous_track,
        )
        self.notification.setTitle(os.path.splitext(os.path.basename(TRACK))[0])
        self.notification.setArtist("Example Artist")

        # 2) The player: prepares the MediaPlayer asynchronously,
        #    fires on_load when ready.
        self.sound = SoundLoader.load(TRACK)
        self.sound.loop = True
        self.sound.bind(on_load=self.on_loaded)
        self.sound.bind(on_complete=self.on_track_finished)
        self.sound.bind(state=self.on_state_changed)

        self.notification.setSoundLoader(self.sound)
        self.notification.set_skip_available(has_next=False, has_prev=False)

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

Two ready-to-run variants live in the repository under `examples/music/`:

- `examples/music/simple_example.py` - load + play only.
- `examples/music/example_1.py` - full player UI with loop toggle, end-of-track handling and next/previous wiring.

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

## `MusicNotification` reference

- `MusicNotification(on_next=None, on_previous=None)` - create the notification; pass callbacks for the skip buttons.
- `setTitle(text)` / `setArtist(text)` - track metadata (also shown on the lock screen).
- `setSoundLoader(sound)` - bind a `SoundLoader`; wires state/load/seek updates to the notification automatically. Builds on `on_load`, or immediately if the sound is already loaded.
- `set_skip_available(has_next, has_prev)` - show/hide the previous/next buttons depending on your queue.
- `updateProgressBar()` - sync the seek bar/play state (called automatically).
- `refresh()` - re-post the built notification.
- `release()` - clean up the `MediaSession` (call it in `App.on_stop()`).