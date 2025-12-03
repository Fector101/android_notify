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

### Kivy apps:  

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add pyjnius so ensure it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify
# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependencies (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core:1.6.0, androidx.core:core-ktx:1.15.0
android.enable_androidx = True
android.api = 35
```

### Flet apps:  
 In your `pyproject.toml` file, ensure you include the following:
```toml
[tool.flet.android]
dependencies = [
  "pyjnius","android-notify==1.60.4.dev0"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```
- example of [complete flet pyproject.toml](https://github.com/Fector101/flet-app/blob/main/pyproject.toml)
------
## Installing without Androidx
How to use without `gradle_dependencies`
Use `android-notify==1.60.4.dev0` to install via `pip`
### In Kivy
```ini
# buildozer.spec
requirements = python3, kivy, pyjnius, android-notify==1.60.4.dev0
```

### On Pydroid 3 
On the [pydroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) mobile app for running python code you can test some features.
- In pip section where you're asked to insert `Libary name` paste `https://github.com/Fector101/android_notify/archive/without-androidx.zip`
- Minimal working example 
```py
# Testing with `android-notify==1.60.4.dev0` on pydroid
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
        asks_permission_if_needed(no_androidx=True)

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

For IDE IntelliSense Can be installed via `pip install`:

```bash
pip install android_notify
android-notify -v
```

## Documentation
For Dev Version use
```requirements = python3, kivy, pyjnius, https://github.com/Fector101/android_notify/archive/main.zip```


To use colored text in your notifications:
- Copy the [res](https://github.com/Fector101/android_notify/tree/main/android_notify/res) folder to your app path.  
Lastly in your `buildozer.spec` file
- Add `source.include_exts = xml` and `android.add_resources = ./res`

To use Custom Sounds
- Put audio files in `res/raw` folder,
- Then from `buildozer.spec` point to res folder `android.add_resources = res`
- and includes it's format `source.include_exts = wav`.

Lastly From the code 
```py
# Create a custom notification channel with a unique sound resource for android 8+
Notification.createChannel(
    id="weird_sound_tester",
    name="Weird Sound Tester",
    description="A test channel used to verify custom notification sounds from the res/raw folder.",
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
For full documentation, examples, and advanced usage, API reference visit the
[documentation](https://android-notify.vercel.app)

## ☕ Support the Project

If you find this project helpful, any support would help me continue working on open-source projects. I’m currently saving for a laptop to keep developing.
[donate](https://www.buymeacoffee.com/fector101)
