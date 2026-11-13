# android-notify-music-bridge (Maven)

Android Java library (`io.github.fector101:android-notify-music-bridge`) used by
[Android Notify](https://android-notify.vercel.app/media-notifications#overview) media notifications on Android.

It contains `org.android_notify.music.MediaSessionCallback`, a
`MediaSession.Callback` bridge that forwards transport control events
(play/pause/seek/next/prev) to a Python listener implemented with pyjnius, and
the nested `MediaSessionCallback.MediaButtonReceiver` for notification action
buttons.

The bridge lives in a **fixed package** and is shipped pre-compiled, so users
never have to copy or edit Java files. To use it, add it to your `buildozer.spec`:

```ini
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.2
```

See [Media Notifications](https://android-notify.vercel.app/media-notifications#overview) for the full setup.

## [1.0.2] - 2026-11-13

### Fixed

- Notification play/pause/next/previous PendingIntents now target a
  non-exported `MediaSessionCallback.MediaButtonReceiver` registered by the AAR manifest. The
  receiver forwards actions to the active Python listener, including on
  Android 12 where an `ACTION_MEDIA_BUTTON` broadcast did not reach the
  `MediaSession.Callback`.

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