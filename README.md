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

### Kivy Android apps:  

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

### Flet Android apps:  

1/3) In your `pyproject.toml` file, ensure you include the following:

```toml
[tool.flet.android]
dependencies = [
  "pyjnius","android_notify"
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

```

Can be installed via `pip` For testing purposes:

```bash
pip install android_notify
```

## Documentation
For Dev Version use
```requirements = python3, kivy, pyjnius, https://github.com/Fector101/android_notify/archive/main.zip```


To use colored text in your notifications:
- Copy the [res](android_notify/res) folder to your app path.  
Lastly in your `buildozer.spec` file
- Add `source.include_exts = xml` and `android.add_resources = ./res`

For full documentation, examples, and advanced usage, API reference visit the
[documentation](https://android-notify.vercel.app)

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! 😊 Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>
