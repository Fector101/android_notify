<div align="center">
    <br>
    <h1> Android-Notifiy </h1>
    <p> A Python library for effortlessly creating and managing Android notifications in Kivy android apps.</p>
    <p>Supports various styles and ensures seamless integration and customization.</p>
    <!-- <br> -->
    <!-- <img src="https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/democollage.jpg"> -->
</div>

## Overview

The Android Notify package provides a simple yet comprehensive way to create and manage rich notifications on Android devices directly from your Python code. This library bridges the gap between Python and Android's notification system, giving you full control over notifications with a clean, Pythonic API.

## Features

- **Multiple Notification Styles**: Support for various notification styles including:
  - Simple text notifications
  - Progress bar notifications (determinate and indeterminate)
  - Big text notifications
  - Inbox-style notifications
  - Large icon notifications
  - Big picture notifications
  - Combined image styles

- **Rich Functionality**:
  - Add action buttons with custom callbacks
  - Update notification content dynamically
  - Manage progress bars with fine-grained control
  - Custom notification channels for Android 8.0+
  - Silent notifications
  - Persistent notifications
  - Click handlers and callbacks

- **Developer Friendly**:
  - Intuitive API with helpful error messages
  - Graceful fallbacks when developing on non-Android platforms
  - Automatic permission handling
  - Comprehensive logging options

## Quick Start

```python
from android_notify import Notification, NotificationStyles

# Simple notification
Notification(
    title="Hello",
    message="This is a basic notification."
).send()

# Progress bar notification
notification = Notification(
    title="Downloading",
    message="Starting download...",
    style=NotificationStyles.PROGRESS
)
notification.send()

# Update progress
notification.updateProgressBar(50, message="Download in progress")

# Add action button
def on_button_click():
    print("Button clicked!")
    
notification.addButton("Cancel", on_button_click)
```

**Sample Image:**  
![basic notification img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/basicnoti.jpg)

## Installation

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

This package is available on PyPI and can be installed via pip:  
For testing purposes

```bash
pip install android_notify
```

## Documentation

For full documentation, examples, and advanced usage, API reference visit the
[documentation](https://android-notify.vercel.app/getting-started)

---

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! 😊 Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>
