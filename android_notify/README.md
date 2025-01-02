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
from android_notify import EnhancedNotificationManager, NotificationStyle, NotificationImportance

# Create a notification manager
notification = EnhancedNotificationManager(
    channel_id="messages",
    channel_name="Messages",
    importance=NotificationImportance.HIGH
)

# Set content
notification.set_content(
    title="Hello!",
    message="Welcome to Android Notify Enhanced",
    style=NotificationStyle.BIG_TEXT
)

# Send notification
notification.send()
```

MIT License

Copyright (c) 2024 Fabian
