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

1/3) In your `pyproject.toml` file, ensure you include the following:

```toml
[tool.flet.android]
dependencies = [
  "pyjnius","android-notify"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```
2/3) At Path `<project-root>/build/flutter/android/app/build.gradle` add the following lines at the end of the file:

Change from this: `dependencies{}`  
To this:
```gradle
dependencies {
    implementation 'androidx.core:core:1.6.0'
    implementation 'androidx.core:core-ktx:1.15.0'
}
```
3/3) At Path `<project-root>/build/flutter/android/app/proguard-rules.pro` add the following lines at the end of the file:

Change from this:
```proguard
-keep class com.flet.serious_python_android.** { *; }
-keepnames class * { *; }
```
To this:
```proguard
-keep class com.flet.serious_python_android.** { *; }
-keepnames class * { *; }

# Keep any AndroidX Core class with 'Notification' in its name
-keep class androidx.core.**Notification** { *; }
-keep class androidx.core.**Notification**$* { *; }

# Used to request access to Notification
-keep class androidx.core.app.ActivityCompat { *; }
```
> [!NOTE]  
> If you change these values `dependencies, name, bundle_id, product, company` in your `pyproject.toml` file, make sure to go through the above steps again to ensure the changes are reflected in the build files.
[complete flet example](https://github.com/Fector101/android_notify/tree/main/docs/examples/flet-working)

------
## Installing without Androidx
How to use without `gradle_dependencies`
Use `https://github.com/Fector101/android_notify/archive/without-androidx.zip` to install via `pip`
### In Kivy
```ini
# buildozer.spec
requirements = python3, kivy, pyjnius, https://github.com/Fector101/android_notify/archive/without-androidx.zip
```

### On Pydroid 3 
On the [pydroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) mobile app for running python code you can test some features.
- In pip section where you're asked to insert `Libary name` paste `https://github.com/Fector101/android_notify/archive/without-androidx.zip`
- Minimal working example 
```py
from kivy.app import App
from kivy.uix.button import Button
from android_notify import Notification


class TestApp(App):
    def build(self):
        return Button(
            text="Send Notification",
            on_release=lambda *args: Notification(
                title="Hello from Kivy",
                message="This is a basic notification.",
                channel_id="test_channel",
            ).send()
        )

if __name__ == "__main__":
    TestApp().run()
```

Can be installed via `pip` For testing purposes:

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

For full documentation, examples, and advanced usage, API reference visit the
[documentation](https://android-notify.vercel.app)

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! 😊 Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>
