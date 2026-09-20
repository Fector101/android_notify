# android-notify-music-bridge (Maven)

Android Java library (`io.github.fector101:android-notify-music-bridge`) used by
[Android Notify](../README.md) music notifications on Android.

It contains `org.android_notify.music.MediaSessionCallback`, a
`MediaSession.Callback` bridge that forwards transport control events
(play/pause/seek/next/prev) to a Python listener implemented with pyjnius.

The bridge lives in a **fixed package** and is shipped pre-compiled, so users
never have to copy or edit Java files. To use it, add it to your `buildozer.spec`:

```ini
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.0
```

See [Music Notifications](../docs/music-notifications.md) for the full setup.

## [Unreleased]

## [1.0.1] - 2026-09-20

### Changed

- Lowered `minSdk` from 23 to 21. The bridge only uses
  `android.media.session.MediaSession.Callback`, which exists since API 21, so
  apps with `android.minapi = 21` now link the artifact without manifest
  conflicts.

## [1.0.0] - 2026-09-19

### Added

- Initial semver release of the Android-Notify music bridge
  (`org.android_notify.music.MediaSessionCallback`).