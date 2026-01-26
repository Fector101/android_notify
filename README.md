<div align="center">
    <br>
    <h1> Android-Notify </h1>
    <p><a href='https://android-notify.vercel.app'>Android Notify</a> is a Python library for effortlessly creating and managing Android notifications in Kivy and Flet apps.</p>
    <p>Supports various styles and ensures seamless integration, customization and Pythonic APIs.</p>
    <!-- <br> -->
    <!-- <img src="https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/democollage.jpg"> -->
</div>
<!-- Channel [CRUD]
The Android Notify package provides a simple yet comprehensive way to create and manage rich notifications on Android devices directly from your Python code. This library bridges the gap between Python and Android's notification system, giving you full control over notifications with a clean, Pythonic API. -->

## Features

- **Multiple Notification Styles**: Support for various notification styles including:
  - Simple text notifications
  - [Progress bar notifications](https://android-notify.vercel.app/components#progress-bars) (determinate and indeterminate)
  - Large icon notifications
  - Big picture notifications
  - Combined image styles
  - Custom notification Icon - [images section](https://android-notify.vercel.app/components#images)
  - Big text notifications
  - Inbox-style notifications
  - Colored texts and Icons

- **Rich Functionality**:
  - Add action buttons with custom callbacks
  - [Update notification](https://android-notify.vercel.app/advanced-methods#updating-notification) content dynamically
  - Manage progress bars with fine-grained control
  - [Custom notification channels](https://android-notify.vercel.app/advanced-methods#channel-management) for Android 8.0+ (Creating and Deleting)
  - Silent notifications
  - Persistent notifications
  - Click handlers and callbacks
  - Cancel Notifications

## Quick Start

```python
from android_notify import Notification

# Simple notification
Notification(
    title="Hello",
    message="This is a basic notification."
).send()

```

**Sample Image:**  
![basic notification img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/basicnoti.jpg)

## Installation

<details>
<summary><b>Kivy apps:</b></summary>
<br/>

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add pyjnius so ensure it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify==1.60.8.dev0
# Add permission for notifications
android.permissions = POST_NOTIFICATIONS
```

</details>


<details>
<summary><b>Flet apps:</b></summary>
<br/>

In your `pyproject.toml` file, ensure you include the following:


```toml
[tool.flet.android]
dependencies = [
  "pyjnius","android-notify==1.60.8.dev0"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```
- example of [complete flet pyproject.toml](https://github.com/Fector101/flet-app/blob/main/pyproject.toml)

</details>



<details>

<summary><b>On Pydroid 3</b></summary>
<br/>

On the [pydroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) mobile app for running python code you can test some features.
- In pip section where you're asked to insert `Libary name` paste `android-notify==1.60.8.dev0`
- Minimal working example 
```py
# Testing with `android-notify==1.60.8.dev0` on pydroid
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android_notify import Notification
from android_notify.core import asks_permission_if_needed


class AndroidNotifyDemoApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Button(
            text="Ask Notification Permission",
            on_release=self.request_permission
        ))
        layout.add_widget(Button(
            text="Send Notification",
            on_release=self.send_notification
        ))
        return layout

    def request_permission(self, *args):
        asks_permission_if_needed(legacy=True)

    def send_notification(self, *args):
        Notification(
            title="Hello from Android Notify",
            message="This is a basic notification.",
            channel_id="android_notify_demo",
            channel_name="Android Notify Demo"
        ).send()


if __name__ == "__main__":
    AndroidNotifyDemoApp().run()
```

</details>


<details>

<summary><b>Desktop</b></summary>
<br/>

For IDE IntelliSense Can be installed via `pip install`:

```bash
pip install android_notify
android-notify -v
```
</details>

## Documentation
For Dev Version use
```ini
requirements = python3, kivy, pyjnius, https://github.com/Fector101/android_notify/archive/without-androidx.zip
```

<details>
<summary> <b> To talk to BroadCast Listener From Buttons </b> </summary>

- Make things happen without being in your app
```python
from android_notify import Notification
notification = Notification(title="Receiver Notification")
notification.addButton(text="Stop", receiver_name="CarouselReceiver", action="ACTION_STOP")
notification.addButton(text="Skip", receiver_name="CarouselReceiver", action="ACTION_SKIP")
```
You can use this [wiki](https://github.com/Fector101/android_notify/wiki/How-to-Use-with-Broadcast-Listener) as a guide create a broadcast listener
</details>

<details>
<summary> <b> To use colored text in your notifications </b> </summary>

- Copy the [res](https://github.com/Fector101/android_notify/tree/main/android_notify/res) folder to your app path.  
- Lastly in your `buildozer.spec` file  
Add `source.include_exts = xml` and `android.add_resources = # path you pasted`
```python
# Use Hex Code to be Safe
n = Notification(title="Title and Message Color", message="Testing",title_color="red")
n.send()
```

</details>

<details>
<summary> <b>To use Custom Sounds </b> </summary>

- Put audio files in `res/raw` folder,
- Then from `buildozer.spec` point to res folder `android.add_resources = res`
- and includes it's format `source.include_exts = wav`.

Lastly From the code 
```py
# Create a custom notification channel with a unique sound resource for android 8+
Notification.createChannel(
    id="weird_sound_tester",
    name="Weird Sound Tester",
    description="A test channel for custom sounds from the res/raw folder.",
    res_sound_name="sneeze" # file name without .wav or .mp3
)

# Send a notification through the created channel
n=Notification(
    title="Custom Sound Notification",
    message="This tests playback of a custom sound (sneeze.wav) stored in res/raw.",
    channel_id="weird_sound_tester" # important tells notification to use right channel
)
n.setSound("sneeze")# for android 7 below 
n.send()
```
</details>


<details>
<summary> <b> Vibrate feature</b> </summary>

```ini
# buildozer.spec
android.permissions = VIBRATE
```

```python
Notification.createChannel(id='shake', name="Shake Passage", vibrate=True)

n=Notification(title='Vibrate',channel_id='shake')
n.setVibrate() # for less than android 8
n.fVibrate() # To Force Vibrate (when user turned off in settings)
n.send()
```

</details>


<details>
<summary> <b> Add Data to Notification</b> </summary>


- `NotificationHandler.data_object` returns a `dict` of data in the clicked `notification`
- `setData` can also be called after `send` to change `data_object` stored
- Use `name` if value is constant `Notification(name="change page")`
```python
from android_notify import Notification, NotificationHandler

    def build(self):
        notification = Notification(title="Hello")
        notification.setData({"next wallpaper path": "test.jpg"})
        notification.send()

    def on_start(self):
        notification_data = NotificationHandler.data_object  # {"next wallpaper path": "test.jpg",...}
        print(notifcation_data)

    def on_resume(self):
        notification_data = NotificationHandler.data_object  # {"next wallpaper path": "test.jpg",...}
        print(notifcation_data)
```

</details>


### For full documentation, examples, and advanced usage, API reference visit the [documentation](https://android-notify.vercel.app)

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! 😊  
Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>
