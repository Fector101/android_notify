# Advanced Features

## Updating notifications

Notifications can be updated in real-time. Pass the notification `id` (or reuse the same instance) to update instead of creating a new one.

```python
notification = Notification(title="Old title", message="Old message").send()
```

Update title and/or message:

```python
notification.updateTitle("New title")
notification.updateMessage("New message")
```

## Progress bar management

```python
from android_notify import Notification

notification = Notification(
    title="Downloading",
    message="0%",
    progress_current_value=0,
    progress_max_value=100,
).send()

# Update progress in real time
notification.updateProgressBar(50, "50% downloaded")

# Then remove it cleanly (optionally showing a final update briefly)
notification.removeProgressBar(message="Done", show_on_update=True)
```

## Adding style even when already sent

Use `.refresh()` to apply any new changes after sending:

```python
notification = Notification(title="Downloading", message="0%")
notification.send()

notification.setLargeIcon("imgs/profile.png")
notification.refresh()
```

## Channel management

Android 8.0+ requires notifications to belong to a channel. The default channel is created for you, but you can create, check and delete your own.

```python
from android_notify import Notification

# Create a channel
Notification.createChannel(
    id="news",
    name="News",
    description="Breaking news updates",
    importance="high",       # 'urgent', 'high', 'medium', 'low', 'none'
    vibrate=False,
)

# Send through the channel
Notification(
    title="New article",
    message="Check out the latest article",
    channel_id="news",
).send()
```

Check existence and delete channels:

```python
from android_notify import Notification

Notification.channelExists("news")       # bool
Notification.doChannelsExist(["news", "promo"])  # bool
Notification.getChannels()               # list of channel objects

Notification.deleteChannel("news")
Notification.deleteAllChannel()
```

![channel name](imgs/channel_name.jpg)

## Silent notifications

```python
from android_notify import Notification

Notification(
    title="Silent update",
    message="No sound or heads-up",
    silent=True,
).send()
```

## Persistent notifications

Keep the notification in the tray until cancelled by the user or the app:

```python
notification = Notification(
    title="Downloading...",
    message="Large file",
    persistent=True,
).send()
```

## Controlling popups (heads-up)

```python
from android_notify import Notification
import time

notification = Notification(
    title="Processing...",
    message="Starting task",
).send()
time.sleep(10)

# show heads-up when updated
notification.setOnlyAlertOnce(False)

notification.updateTitle("Processing Complete!")
notification.updateMessage("Task finished successfully")
```

## Custom sound

**Option 1: Audio files bundled in `res/raw`**

- Put audio files in the `res/raw` folder.
- From `buildozer.spec` point to the res folder: `android.add_resources = res`.
- Include the format: `source.include_exts = wav`.

```python
from android_notify import Notification

# Create a custom notification channel with a unique sound resource for android 8+
Notification.createChannel(
    id="weird_sound_tester",
    name="Weird Sound Tester",
    description="A test channel for custom sounds from the res/raw folder.",
    res_sound_name="sneeze"  # file name without .wav or .mp3
)

# Send a notification through the created channel
n = Notification(
    title="Custom Sound Notification",
    message="This tests playback of a custom sound (sneeze.wav) stored in res/raw.",
    channel_id="weird_sound_tester"  # important: tells the notification to use the right channel
)
n.setSound("sneeze")  # for android 7 and below
n.send()
```

**Option 2: Local file path or URI (`sound_path`)**

You can use a local audio file, a `content://`, `file://`, or `android.resource://` URI directly:

```python
from android_notify import Notification

# Using a local file path
Notification.createChannel(
    id="local_sound",
    name="Local Sound",
    sound_path="/storage/emulated/0/Download/alert.mp3"
)

# Using a content URI (e.g. from media store)
Notification.createChannel(
    id="uri_sound",
    name="URI Sound",
    sound_path="content://media/external/audio/media/123"
)

# Send notification with custom sound path
n = Notification(
    title="Custom Sound",
    message="Playing from local path",
    channel_id="local_sound"
)
n.setSound(sound_path="/storage/emulated/0/Download/alert.mp3")
n.send()
```

Private files (e.g. in the app's `data/` directory) are automatically copied to external storage before playing.

## Vibration

```python
from android_notify import Notification

notification = Notification(
    title="Vibration",
    message="Buzz buzz",
    vibrate=True,
).send()
```

Custom vibration pattern:

```python
notification.setVibrate([0, 500, 200, 500])
```

## Click handlers and data

`NotificationHandler.data_object` returns a `dict` of data in the clicked notification. `setData` can be called after `send` to change the stored `data_object`. Use the `name` argument if the value is constant.

```python
from android_notify import Notification

notification = Notification(title="Hello", name="change page")
notification.setData({"next wallpaper path": "test.jpg"})
notification.send()
```

```python
from android_notify import NotificationHandler

# get the data of the notification used to open the app
notification_data = NotificationHandler.data_object
# {"next wallpaper path": "test.jpg", "name": "change page"}
```

Get the name of the notification used to open the app:

```python
from android_notify import NotificationHandler

name = NotificationHandler.get_name(on_start=True)
```

## Cancel notifications

```python
notification = Notification(title="Hello", message="World").send()

# Later, cancel it
notification.cancel()
```

Cancel all notifications:

```python
Notification.cancelAll()
```

## Priority

Set the importance/priority of a notification after creation:

```python
from android_notify import Notification

notification = Notification(title="Urgent", message="Important").send()
notification.setPriority("high")  # 'urgent', 'high', 'medium', 'low', 'none'
```

## Misc

- `setWhen(secs_ago)` — set the timestamp shown on the notification (seconds ago).
- `setObeyUserClear(state)` — whether re-triggering the notification after the user cleared it from the tray is allowed.
- `isInTray()` — check if the notification is still shown in the tray.
- `NotificationHandler.bindNotifyListener()` / `unbindNotifyListener()` — listen for notification open events in your app.