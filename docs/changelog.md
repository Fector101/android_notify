# Changelog

Release notes for all versions of Android Notify.

| Marker | Meaning |
| --- | --- |
| [New] | New features or API |
| [Changed] | API changes or issues with advanced methods |
| [Fix] | Critical fixes |

## Version 1.60

**Improvements**

- [New] Interactions in Service: a way to pass in Broadcast Receiver and Actions to Buttons.
- [New] Usage without gradle dependencies: new branch `without-androidx` was created, allowing usage in Pydroid3 and Flet apps. Install via `__version__.dev0`.
- [New] Flet support: beta support for Flet Python apps.
- [New] Better logging: replaced prints with a Python logger, allowing log levels.
- [New] Modularization: split the package into smaller task-based structure for easier management.

**Class: `Notification`**

New arguments:

- [New] `addButton` - `receiver_name`, `action`
- [New] `createChannel` - `vibrate`, `res_sound_name`
- [New] `setBigText` - `title`, `summary`
- [New] `Notification()` - `name`, `title_color`, `message_color`, `silent`

New methods:

- [New] `setColor` - color, changes app icon color using hex code.
- [New] `setSubText` - text, adds small text near the title.
- [New] `setWhen` - secs_ago, to change the time the notification was created.
- [New] `channelExists` - channel_id, to check if said channel exists.
- [New] `doChannelsExist` - ids, returns those that do not exist.
- [New] `setData` - attach a dictionary of data for later use.
- [New] `fVibrate` - trigger a standard notification vibration.
- [New] `fill_args` - fills notification args without sending.
- [New] `start_building` - builds the notification without sending, returns the builder (for foreground services).
- [New] `isUsingCustom` - returns True if custom title/message colors are set.

Support for devices less than Android 8:

- [New] `setVibrate` - pattern, defaults to a single vibration.
- [New] `setSound` - res_sound_name, changes the default notification sound.

**Class: `NotificationHandler`**

New arguments:

- [New] `get_name` - `on_start` must be True when called from `App.on_start()`.

New property:

- [New] `data_object` - access data added via `Notification.setData`.

## Version 1.59

**Add new features**

- [New] Added a way to access an old `Notification` instance with `Notification().id`.
- [New] Methods to cancel a certain or all notifications: `Notification().cancel()`, `Notification.cancelAll`. If the old instance is not available and you need to cancel one, use the id with `Notification.cancel(_id)`.
- [New] When setting a new component after `Notification().send`, use `Notification().refresh`.
- [New] Instead of only requesting in `init`, created `NotificationHandler.asks_permission` and `NotificationHandler.has_permission`.

**Add methods working to free up `__init__` kwargs** (parsing out the `style` attribute):

- [New] `setSmallIcon` == `Notification(..., app_icon="...")`
- [New] `setLargeIcon` == `Notification(..., large_icon_path="...", style=NotificationStyles.LARGE_ICON)`
- [New] `setBigPicture` == `Notification(..., body="...", style=NotificationStyles.BIG_PICTURE)`
- [New] `setBigText` == `Notification(..., big_picture_path="...", style=NotificationStyles.BIG_TEXT)`
- [New] For creating channels `Notification.createChannel(name, id, desc)`
- [New] For deleting channels `Notification.deleteAllChannel()` and `Notification.deleteChannel(channel_id)`

**Changed**

- [Changed] `Notification.identifer` to `Notification.name`
- [Changed] `NotificationHandler.getIdentifer` to `NotificationHandler.get_name`

## Version 1.58

- [Changed] `showInfiniteProgressBar` had no guard block when not on Android.
- [Fix] `NotificationHandler.getIdentifer` always returned a value even when the app was not opened from a notification.