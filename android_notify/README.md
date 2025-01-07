# Android Notify Enhanced [dev]

For Stable Version documentation, please visit GitHub repository [main docs](https://github.com/fector101/android-notify).

An enhanced Android notification system for Python applications, providing a comprehensive way for creating and managing notifications on Android devices.

## Features

- 🎨 Multiple notification styles (default, big text, big picture, inbox, messaging)
- 🔔 Full notification channel support
- 🔄 Progress indicators and updates
- 🖼️ Custom icons and images
- 👆 Action buttons with custom intents
- 📱 Notification grouping
- ⚡ Priority and importance settings
- 🔧 Extensive customization options

## Installation

```bash
pip install android-notify
```

## Quick Start

```python
from android_notify import Notification

# Create a notification manager
notification = Notification(
    title="Hello!",
    message="Welcome to Android Notify Enhanced",
    channel_id="messages",
    channel_name="Messages",
)

# Send notification
notification.send()

# Update Title
notification.updateTitle("Download Complete")
```

MIT License

Copyright (c) 2024 Fabian
