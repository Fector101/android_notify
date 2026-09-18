# Android-Notify

Android-Notify is a Python library for effortlessly creating and managing Android notifications in **Kivy** and **Flet** apps. It bridges the gap between Python and Android's notification system, supports various styles, and ensures seamless integration, customization and Pythonic APIs.

```{toctree}
:maxdepth: 2
:caption: Contents

installation
quickstart
usage
advanced
api
```

## Features

- **Multiple notification styles**:
  - Simple text notifications
  - [Progress bar](usage.md#progress-bar) notifications (determinate and indeterminate)
  - Large icon notifications
  - Big picture notifications
  - Combined image styles
  - Custom notification icon — see the [images](usage.md#images) section
  - Big text notifications
  - Inbox-style notifications
  - Colored texts and icons

- **Rich functionality**:
  - Add action [buttons](usage.md#buttons) with custom callbacks
  - [Update notification](advanced.md#updating-notifications) content dynamically
  - Manage progress bars with fine-grained control
  - Custom notification [channels](advanced.md#channel-management) for Android 8.0+
  - Silent notifications
  - Persistent notifications
  - Click handlers and callbacks
  - Cancel notifications
  - Use [custom sound](advanced.md#custom-sound)
  - [Vibration](advanced.md#vibration)

## Quick Start

```python
from android_notify import Notification

# Simple notification
Notification(
    title="Hello",
    message="This is a basic notification."
).send()
```

## Support the Project

If you find this project helpful, consider buying me a coffee or giving it a star on [GitHub](https://github.com/Fector101/android_notify/). Your support helps maintain and improve the project.

## Bug Reports & Feature Requests

Found a bug or have an idea for a new feature? Feel free to open an issue [here](https://github.com/Fector101/android_notify/issues).

When reporting a bug, try to include:

- Device name
- Android version
- Steps to reproduce the issue
- Screenshots or logs (if possible)

Feature suggestions are also welcome.