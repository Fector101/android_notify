# Changelog

Release notes for all versions of Android Notify.

## Version 1.62

**Improvements**

- Dynamic broadcast buttons: `Notification.addButton(..., action=..., dynamic=True)` sends a package-scoped broadcast to a `BroadcastReceiver` registered at runtime, so a button can act without opening the app and without a manifest receiver or a Java class.
- `MediaNotification.setNowPlaying(title, artist)` updates the live notification (title, artist, artwork and lock-screen metadata) in one call on a track change.
- Media notification module moved to `android_notify.media` (was `android_notify.media.music`). `SoundLoader` and `MediaPermissionHandler` stay under `android_notify.media.music` and can be imported from `android_notify.media.music` or `android_notify.media.music.helper`.
- Media controllers that do not dispatch events can now drive the notification with `syncPlaybackState()`, including plain Kivy `SoundLoader` wrappers.
- Media artwork falls back to the app icon when a track has no embedded cover art, instead of keeping the previous track's image.
- Faster path and playback handling: removed the slow `android.storage` import from the notification path and optimized media position/length reads.

**Changed**

- Removed the `run_on_ui_thread` helper. Open activities from the UI thread directly; do not start an activity from a background thread.
- Button `PendingIntent` request codes are now unique per notification, so two notifications using the same button action no longer overwrite each other's extras.

**Fixed**

- Unknown media length no longer raises while the notification is being updated.
- Media notification metadata and artwork are refreshed on a track change without waiting for the next playback event.

**Docs**

- The music notifications page is now **Media Notifications** (`media-notifications`). The old page URL redirects with a short moved note.
- Documented plain controllers (`syncPlaybackState()`), Android background playback for Kivy's `SoundLoader`, and the default-cover fallback for tracks without embedded art.
- Documented runtime broadcast receivers for buttons that work from a service without Java.

## Version 1.61

**Improvements**

- Lazy Java class loading keeps app start-up time at 0.
- Support for Android 8 and below in the notification builder and permission checks.
- Flet and Androidx runtime detection and file-path fixes.
- Flet file-path fixes.
- Music notification with `SoundLoader` audio playback management.
- Automatic resource extraction for Android packages.

**Class: `Notification`**

New methods:

- `getChannels` - returns a list of dicts for every existing channel (`id`, `name`, `description`, `state`, `j_obj`).
- `setObeyUserClear` - control whether a notification reappears after the user clears it.
- `setOnlyAlertOnce` - control whether updates show a heads-up popup.

**Changed**

- `getChannels` now returns readable per-channel dicts instead of the raw Java list.
- Removed deprecated APIs (e.g. `Notification.addNotificationStyle`). Use the styles in `android_notify.NotificationStyles` directly.

**Fixed**

- Legacy permission check broken by lazy Java classes on Android 12 and below.
- Permission check in a service raising `NoneType` errors.
- Path issues in Flet apps.
- Auto-strip the audio extension from `res_sound_name` with a warning.

**Docs**

- Read the Docs site built with Sphinx, MyST and Furo.
- New foreground services and help pages.
- The `android.gradle_dependencies` example referred to music bridge 1.0.0; the published version is 1.0.1.

## Version 1.60

**Improvements**

- Interactions in Service: a way to pass in Broadcast Receiver and Actions to Buttons.
- Usage without gradle dependencies: new branch `without-androidx` was created, allowing usage in Pydroid3 and Flet apps. Install via `__version__.dev0`.
- Flet support: beta support for Flet Python apps.
- Better logging: replaced prints with a Python logger, allowing log levels.
- Modularization: split the package into smaller task-based structure for easier management.

**Class: `Notification`**

New arguments:

- `addButton` - `receiver_name`, `action`
- `createChannel` - `vibrate`, `res_sound_name`
- `setBigText` - `title`, `summary`
- `Notification()` - `name`, `title_color`, `message_color`, `silent`

New methods:

- `setColor` - color, changes app icon color using hex code.
- `setSubText` - text, adds small text near the title.
- `setWhen` - secs_ago, to change the time the notification was created.
- `channelExists` - channel_id, to check if said channel exists.
- `doChannelsExist` - ids, returns those that do not exist.
- `setData` - attach a dictionary of data for later use.
- `fVibrate` - trigger a standard notification vibration.
- `fill_args` - fills notification args without sending.
- `start_building` - builds the notification without sending, returns the builder (for foreground services).
- `isUsingCustom` - returns True if custom title/message colors are set.

Support for devices less than Android 8:

- `setVibrate` - pattern, defaults to a single vibration.
- `setSound` - res_sound_name, changes the default notification sound.

**Class: `NotificationHandler`**

New arguments:

- `get_name` - `on_start` must be True when called from `App.on_start()`.

New property:

- `data_object` - access data added via `Notification.setData`.

## Version 1.59

**Add new features**

- Added a way to access an old `Notification` instance with `Notification().id`.
- Methods to cancel a certain or all notifications: `Notification().cancel()`, `Notification.cancelAll`. If the old instance is not available and you need to cancel one, use the id with `Notification.cancel(_id)`.
- When setting a new component after `Notification().send`, use `Notification().refresh`.
- Instead of only requesting in `init`, created `NotificationHandler.asks_permission` and `NotificationHandler.has_permission`.

**Add methods working to free up `__init__` kwargs** (parsing out the `style` attribute):

- `setSmallIcon` == `Notification(..., app_icon="...")`
- `setLargeIcon` == `Notification(..., large_icon_path="...", style=NotificationStyles.LARGE_ICON)`
- `setBigPicture` == `Notification(..., body="...", style=NotificationStyles.BIG_PICTURE)`
- `setBigText` == `Notification(..., big_picture_path="...", style=NotificationStyles.BIG_TEXT)`
- For creating channels `Notification.createChannel(name, id, desc)`
- For deleting channels `Notification.deleteAllChannel()` and `Notification.deleteChannel(channel_id)`

**Changed**

- `Notification.identifer` to `Notification.name`
- `NotificationHandler.getIdentifer` to `NotificationHandler.get_name`

## Version 1.58

**Changed**

- `showInfiniteProgressBar` had no guard block when not on Android.

**Fixed**

- `NotificationHandler.getIdentifer` always returned a value even when the app was not opened from a notification.